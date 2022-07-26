import requests
import math
import time
import datetime
from threading import Timer
from PyP100 import PyP100, PyP110

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


def init():
    plugTest()
    timer = RepeatTimer(repeatIntervalInMinutes * 60, recurringTask)
    timer.start()


def plugTest():
    p110 = PyP100.P100("192.168.1.18", "email", "password")
    p110.handshake()
    p110.login()
    while True:
        p110.turnOff()
        time.sleep(3)
        p110.turnOn()
        time.sleep(3)

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


class RepeatTimer(Timer):
    def run(self):
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    init()
