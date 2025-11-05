import time
import math
import schedule
from pybit.unified_trading import HTTP
session = HTTP(testnet=False, api_key="", api_secret="")
def autoTrading():
    firstToTest = 20
    lastToTest = 140
    time.sleep(0.5)
    try:
        instrumentsResponse = session.get_instruments_info(category="linear", limit=1000)
    except Exception as e:
        print("Problem retrieving instrument data")
        exit(1)
    allCoins = instrumentsResponse["result"]["list"]
    allPerpetualCoins = []
    for coin in allCoins:
        if coin["deliveryTime"] == "0":
            allPerpetualCoins.append(coin)
    timeSortedCoins = sorted(allPerpetualCoins, key=lambda x: int(x["launchTime"]), reverse=True)
    usefulCoinData = []
    for coin in timeSortedCoins:
        coinData = {
            "symbol": coin["symbol"],
            "qtyStep": float(coin["lotSizeFilter"]["qtyStep"]),
            "copyTrading": coin["copyTrading"],
            "ohlc": []
        }
        time.sleep(0.5)
        try:
            klineResponse = session.get_kline(symbol=coin["symbol"], interval="D", limit=1000)
        except Exception:
            print("Problem retrieving kline data")
            exit(1)
        for candle in klineResponse["result"]["list"]:
            coinData["ohlc"].append({
                "timeStamp": float(candle[0]),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4])
            })
        usefulCoinData.append(coinData)
    totalCoinData = usefulCoinData[:lastToTest]
    testCoinData = usefulCoinData[firstToTest:lastToTest]
    time.sleep(0.5)
    try:
        walletResponse = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
    except Exception as e:
        print("Problem retreiving wallet data")
        exit(1)
    balance = float(walletResponse["result"]["list"][0]["totalWalletBalance"])
    initialMargin = walletResponse["result"]["list"][0]["totalInitialMargin"]
    if initialMargin == "":
        initialMargin = 0
    else:
        initialMargin = float(initialMargin)
    tpStart = 1
    tpEnd = 100
    tpIncrement = 1
    slStart = 1
    slEnd = 101
    slIncrement = 1
    strategyData = []
    for tp in range(tpStart, tpEnd, tpIncrement):
        for sl in range(slStart, slEnd, slIncrement):
            strategyData.append({
                "tp": tp,
                "sl": sl
            })
    for i in range(0, len(strategyData), 1):
        strategy = strategyData[i]
        tpPercentage = strategy["tp"] / 100
        slPercentage = strategy["sl"] / 100
        leverage = 1 / slPercentage
        if leverage >= 5:
            leverage = 5
        total = 0
        wins = 0
        entryTimes = []
        exitTimes = []
        for coin in testCoinData:
            prevCandle = 0
            entryPrice = 0
            reversedOHLC = list(reversed(coin["ohlc"]))
            for k, candle in enumerate(reversedOHLC):
                timeStamp = int(candle["timeStamp"])
                open = candle["open"]
                high = candle["high"]
                low = candle["low"]
                close = candle["close"]
                if close > open:
                    bearish = False
                    size = close - open
                else:
                    bearish = True
                    size = open - close
                confirmed = k != len(reversedOHLC) - 1
                if prevCandle != 0:
                    prevOpen = prevCandle["open"]
                    prevClose = prevCandle["close"]
                    if prevClose > prevOpen:
                        prevBullish = True
                        prevSize = prevClose - prevOpen
                    else:
                        prevBullish = False
                        prevSize = prevOpen - prevClose
                    if confirmed and bearish and prevBullish and size > prevSize and entryPrice == 0:
                        entryTimes.append(timeStamp)
                        entryPrice = close
                        continue
                if entryPrice != 0:
                    tpPrice = entryPrice - entryPrice * tpPercentage
                    slPrice = entryPrice + entryPrice * slPercentage
                    if high > slPrice:
                        exitTimes.append(timeStamp)
                        total += 1
                        break
                    elif low < tpPrice:
                        exitTimes.append(timeStamp)
                        total += 1
                        wins += 1
                        break
                prevCandle = candle
        events = (
            [(time, 1) for time in entryTimes] + 
            [(time, -1) for time in exitTimes]
        )
        events.sort()
        currentOpenTrades = 0
        maxOpenTrades = 0
        for _, event_type in events:
            currentOpenTrades += event_type
            maxOpenTrades = max(maxOpenTrades, currentOpenTrades)
        strategy["maxOpenTrades"] = maxOpenTrades
        winRate = wins / total if total > 0 else 0
        lossRate = 1 - winRate
        strategy["winRate"] = winRate
        if leverage > 5:
            leverage = 5
        if maxOpenTrades > 0 and winRate >= 0.7:
            expectedValue = ((winRate * tpPercentage) - (lossRate * slPercentage)) / maxOpenTrades * leverage
        else: 
            expectedValue = 0
        strategy["expectedValue"] = expectedValue
    sortedStrategyData = sorted(strategyData, key=lambda x: x["expectedValue"], reverse=True)
    print(sortedStrategyData[0])
    bestStrategy = sortedStrategyData[0]
    potentialTrades = []
    strategy = bestStrategy
    tpPercentage = strategy["tp"] / 100
    slPercentage = strategy["sl"] / 100
    for coin in totalCoinData:
        alreadyEntered = False
        prevCandle = 0
        entryPrice = 0
        reversedOHLC = list(reversed(coin["ohlc"]))
        for k, candle in enumerate(reversedOHLC):
            open = candle["open"]
            close = candle["close"]
            if close > open:
                bearish = False
                size = close - open
            else:
                bearish = True
                size = open - close
            lastConfirmed = k == len(reversedOHLC) - 2
            pastConfirmed = k != len(reversedOHLC) - 1 and not lastConfirmed
            if prevCandle != 0:
                prevOpen = prevCandle["open"]
                prevClose = prevCandle["close"]
                if prevClose > prevOpen:
                    prevBullish = True
                    prevSize = prevClose - prevOpen
                else:
                    prevBullish = False
                    prevSize = prevOpen - prevClose
                if pastConfirmed and bearish and prevBullish and size > prevSize and alreadyEntered == False:
                    alreadyEntered = True
                if lastConfirmed and bearish and prevBullish and size > prevSize and alreadyEntered == False:
                    entryPrice = close
            if entryPrice != 0:
                tpPrice = entryPrice - entryPrice * tpPercentage
                slPrice = entryPrice + entryPrice * slPercentage
                potentialTrades.append({"symbol": coin["symbol"], "tpPrice": tpPrice, "slPrice": slPrice})
                break
            prevCandle = candle
    print(potentialTrades)
    for potentialTrade in potentialTrades:
        for coin in totalCoinData:
            if coin["symbol"] == potentialTrade["symbol"]:
                symbol = coin["symbol"]
                leverage = 100 / bestStrategy["sl"]
                if leverage > 5:
                    leverage = 5
                stringLeverage = str(leverage)
                maxOpenTrades = bestStrategy["maxOpenTrades"]
                dollarAmount = balance / maxOpenTrades
                assetPrice = coin["ohlc"][0]["close"]
                qty = dollarAmount / assetPrice
                leveragedQty = qty * leverage
                qtyStep = coin["qtyStep"]
                roundedQty = qtyStep * math.floor(leveragedQty / qtyStep)
                stringRoundedQty = str(roundedQty)
                tpPrice = potentialTrade["tpPrice"]
                stringTpPrice = str(tpPrice)
                slPrice = potentialTrade["slPrice"]
                stringSlPrice = str(slPrice)
                availableBalance = balance - initialMargin
                if availableBalance > dollarAmount:
                    try:
                        session.set_leverage(category="linear", symbol=symbol, buyLeverage=stringLeverage, sellLeverage=stringLeverage)
                    except Exception as e:
                        print("Problem setting leverage")
                        exit(1)
                    try:
                        session.place_order(category="linear", symbol=symbol, side="Sell", orderType="Market", qty=stringRoundedQty, takeProfit=stringTpPrice, stopLoss=stringSlPrice)
                    except Exception as e:
                        print("Problem placing order")
                        exit(1)
schedule.every().day.at("02:00").do(autoTrading)
while True:
    schedule.run_pending()
    time.sleep(60)