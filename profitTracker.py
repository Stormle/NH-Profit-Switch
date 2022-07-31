import datetime
import math
import time
import requests


class Tracker:
    def __init__(self, pcElectricityUseInWatts, electricityPriceIn_vs_currency, hashRates):
        self.hashRates = hashRates
        self.repeatIntervalInMinutes = 15
        self.coinTimeSpanInHours = 3
        self.priceTimeRangeInHours = 12
        self.pcElectricityUseInWatts = pcElectricityUseInWatts
        self.electricityPriceIn_vs_currency = electricityPriceIn_vs_currency
        self.cardID = 'https://api2.nicehash.com/main/api/v2/public/profcalc/device?device=1821b5f3-581f-4d0a-9ae1-8db2e2f758e6'
        self.coinName = 'bitcoin'
        self.vs_currency = 'eur'
        self.profitability = 0

    def set_coin_time_span_in_hours(self, number):
        self.coinTimeSpanInHours = number

    def set_repeat_interval_in_minutes(self, number):
        self.repeatIntervalInMinutes = number

    def set_vs_currency(self, currency):
        self.vs_currency = currency

    def set_coinName(self, coin_name):
        self.vs_currency = coin_name

    def refresh(self):
        self.profitability = recurringTask(self)
        return self.profitability

    def get_profitability(self):
        return self.profitability


def recurringTask(self):
    """Returns P/L of 24 hours"""
    dailyElectricCost = getDailyElectricityCost(self)
    coinPrice = getPriceAvg(self)
    try:
        if not coinPrice[0]:
            print("Coingecko API did not respond correctly. Using previous profit value. Error: " + coinPrice[1])
            return self.profitability
    except(Exception,):
        pass

    coinsPerDay = getCoinsPerDay(self)
    try:
        if not coinsPerDay[0]:
            print("NiceHash API did not respond correctly. Using previous coin gain value. Error: " + coinsPerDay[1])
    except(Exception,):
        pass

    printer(self, dailyElectricCost, coinPrice, coinsPerDay)
    return (coinPrice * coinsPerDay) - dailyElectricCost


def getDailyElectricityCost(self):
    return float(self.pcElectricityUseInWatts * self.electricityPriceIn_vs_currency / 1000 * 24)


def getPriceAvg(self):
    toTime = int(time.time())
    fromTime = int(toTime - (self.priceTimeRangeInHours * 60 * 60))
    priceAPI = 'https://api.coingecko.com/api/v3/coins/' + self.coinName + '/market_chart/range?vs_currency=' + self.vs_currency + '&from=' + str(
        fromTime) + '&to=' + str(toTime)
    response = ""
    try:
        response = requests.get(priceAPI)
        priceResponse = response.json()
        priceAverage = 0
        for i in priceResponse['prices']:
            priceAverage += float(i[1] / len(priceResponse['prices']))
        return priceAverage
    except (Exception, ) as e:
        return False, response.reason



def getCoinsPerDay(self):
    response = ""
    try:
        payload = self.hashRates
        response = requests.post('https://api2.nicehash.com/main/api/v2/public/profcalc/profitability', json=payload)
        responseContent = response.json()["values"]
        timeDiff = int(list(responseContent)[-1]) - int(list(responseContent)[-2])
        nOfDataPoints = math.ceil(int(self.coinTimeSpanInHours * 60 * 60 / timeDiff))
        sumOfAverages = 0

        nOfAdditions = nOfDataPoints
        for i in range(-1, -abs(int(nOfDataPoints)) - 1, -1):
            if i < -abs(len(responseContent)):
                nOfAdditions = abs(i) - 1
                break
            cont = responseContent[list(responseContent)[i]]
            sumOfAverages += cont['p']
        averageCoinsPerDay = float(sumOfAverages / nOfAdditions)
        return averageCoinsPerDay
    except(Exception,) as e:
        return False, response.reason


def printer(self, dailyElectricCost, coinPrice, coinsPerDay):
    e = datetime.datetime.now()
    print('--------------------- %s ---------------------' % e)
    print('Income per day: ' + f'{coinsPerDay:.20f}' + ' ' + self.coinName + ' / ' + str(
        coinPrice * coinsPerDay) + ' ' + self.vs_currency)
    print('Coin price: ' + str(int(coinPrice)))
    print('Electricity cost per day: ' + str(dailyElectricCost))
    profit = (coinPrice * coinsPerDay) - dailyElectricCost
    print('P/L per day: ' + str(profit) + ' ' + self.vs_currency)
