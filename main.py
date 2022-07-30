import requests
import math
import time
import datetime
from PyP100 import PyP100, PyP110
import argparse
import sys
import asyncio
from plugController import MinerPlug
from threads import RepeatTimer, asyncWithMaxLaps, thread_with_exception
#!!!!!!!!!THIS PROGRAM NEEDS NMAP INSTALLED ON THE SYSTEM!!!!!!!!!

repeatIntervalInMinutes = 15
hashRates = {
        "speeds": {"DAGGERHASHIMOTO": 96, "KAWPOW": 46, "BEAMV3": 47.2, "GRINCUCKATOO32": 0.845, "CUCKOOCYCLE": 11.5,
                   "ZHASH": 146.6, "OCTOPUS": 73.2, "AUTOLYKOS": 195, "ZELHASH": 78}}
coinTimeSpanInHours = 3
priceTimeRangeInHours = 12
pcElectricityUseInWatts = 349
electricityPriceIn_vs_currency = 0.1
cardID = 'https://api2.nicehash.com/main/api/v2/public/profcalc/device?device=1821b5f3-581f-4d0a-9ae1-8db2e2f758e6'
coinName = 'bitcoin'
vs_currency = 'eur'
ipMask = '192.168.1.0/24'

async def init():
    while True:
        #asyncio.run(asyncWithMaxLaps(1, 3, print, "a"))
        t1 = thread_with_exception(1, 3, print, "a")
        t1.start()
        time.sleep(3)
        t1.raise_exception()
        print("b")
        time.sleep(1)
        #await a
    #p100_1 = MinerPlug("5C:A6:E6:FF:00:76", ipMask, args.email, args.password)
    #success = p100_1.initializeConnection()
    #if success == True:
    #    p100_1.turnOn()
    #plugTest()
    #timer = RepeatTimer(repeatIntervalInMinutes * 60, recurringTask)
    #timer.start()

def print_test():
    print("a")

def plugTest():
    p110 = PyP100.P100("192.168.1.18", str(args.email), str(args.password))
    p110.handshake()
    p110.login()
    info = p110.getDeviceInfo()
    onState = info['result']['device_on']
    while True:
        try:
            if onState == True:
                p110.turnOff()
            else:
                p110.turnOn()
            onState = not onState
            time.sleep(2)
        except:
            print("switching error")
            time.sleep(2)

def recurringTask():
    dailyElectricCost = getDailyElectricityCost()
    coinPrice = getPriceAvg()
    coinsPerDay = getCoinsPerDay()
    printer(dailyElectricCost, coinPrice, coinsPerDay)

def printer(dailyElectricCost, coinPrice, coinsPerDay):
    e = datetime.datetime.now()
    print('--------------------- %s ---------------------' % e)
    print('Income per day: ' + f'{coinsPerDay:.20f}' + ' ' + coinName + ' / ' + str(coinPrice * coinsPerDay) + ' ' + vs_currency)
    print('Coin price: ' + str(int(coinPrice)))
    print('Electricity cost per day: ' + str(dailyElectricCost))
    profit = (coinPrice * coinsPerDay) - dailyElectricCost
    print('P/L per day: ' + str(profit) + ' ' + vs_currency)


def getDailyElectricityCost():
    return float(pcElectricityUseInWatts * electricityPriceIn_vs_currency / 1000 * 24)


def getPriceAvg():
    toTime = int(time.time())
    fromTime = int(toTime - (priceTimeRangeInHours * 60 * 60))
    priceAPI = 'https://api.coingecko.com/api/v3/coins/' + coinName + '/market_chart/range?vs_currency=' + vs_currency + '&from=' + str(fromTime) + '&to=' + str(toTime)
    priceResponse = requests.get(priceAPI).json()
    priceAverage = 0
    for i in priceResponse['prices']:
        priceAverage += float(i[1] / len(priceResponse['prices']))
    return priceAverage


def getCoinsPerDay():
    payload = hashRates
    response = requests.post('https://api2.nicehash.com/main/api/v2/public/profcalc/profitability', json=payload)
    responseContent = response.json()["values"]
    timeDiff = int(list(responseContent)[-1]) - int(list(responseContent)[-2])
    nOfDataPoints = math.ceil(int(coinTimeSpanInHours * 60 * 60 / timeDiff))
    sumOfAverages = 0

    nOfAdditions = nOfDataPoints
    for i in range(-1, -abs(nOfDataPoints), -1):
        if i < -abs(len(responseContent)):
            nOfAdditions = abs(i) - 1
            break
        cont = responseContent[list(responseContent)[i]]
        sumOfAverages += cont['p']
    averageCoinsPerDay = float(sumOfAverages / nOfAdditions)
    return averageCoinsPerDay




args = ""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NH-Profit-Switch')
    parser.add_argument('--email', help="Your TP-link Tapo email")
    parser.add_argument('--password', help="Your TP-link Tapo password")
    args = parser.parse_args(sys.argv[1:])
    asyncio.run(init())