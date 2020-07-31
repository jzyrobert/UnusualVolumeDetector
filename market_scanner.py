import os
import time
import yfinance as yf
import dateutil.relativedelta
from datetime import date
import datetime
import numpy as np
import sys
from stocklist import NasdaqController
from tqdm import tqdm

DAYS_TO_REPORT = 1
MONTHS_TO_CHECK = 5

class mainObj:
    def getData(self, ticker, months):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=months)
        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, pastDate, currentDate)
        sys.stdout = sys.__stdout__
        return data[["Volume"]]

    def find_anomalies(self, data, cutoff):
        anomalies = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        indexs = data[data['Volume'] > upper_limit].index.tolist()
        outliers = data[data['Volume'] > upper_limit].Volume.tolist()
        index_clean = [str(x)[:-9] for x in indexs]
        d = {'Dates': index_clean, 'Volume': outliers}
        return d

    def find_anomalies_two(self, data, cutoff):
        indexs = []
        outliers = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        for i in range(len(data)):
            temp = data['Volume'].iloc[i]
            if temp > upper_limit:
                indexs.append(str(data['Date'].iloc[i])[:-9])
                outliers.append(temp)
        d = {'Dates': indexs, 'Volume': outliers, 'Average' : data_mean}
        return d
    
    def printAndAdd(self, s):
        print(s)
        return s

    def customPrint(self, d, tick):
        output = self.printAndAdd("*******  " + tick.upper() + "  *******") + "\n"
        output += self.printAndAdd("Average: {}\n".format(d['Average']))
        output += "Anomalies: \n"
        for i in range(len(d['Dates'])):
            str1 = str(d['Dates'][i])
            str2 = str(d['Volume'][i])
            output += self.printAndAdd(str1 + " - " + str2 + "\n")
        return output

    def days_between(self, d1, d2):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    def main_func(self, cutoff, months, days):
        if months is None:
            months = MONTHS_TO_CHECK
        if days is None:
            days = DAYS_TO_REPORT
        yield "Scanning for stocks that exceeded {} standard deviations of their {}-month average in the last {} days".format(cutoff, months, days)
        StocksController = NasdaqController(True)
        list_of_tickers = StocksController.getList()
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        start_time = time.time()
        for x in tqdm(list_of_tickers):
            d = (self.find_anomalies_two(self.getData(x, months), cutoff))
            if d['Dates']:
                for i in range(len(d['Dates'])):
                    if self.days_between(str(currentDate)[:-9], str(d['Dates'][i])) <= days:
                        stock = self.customPrint(d, x)
                        yield stock

        timeTaken = "\n\n\n\n--- this took {} seconds to run ---".format(time.time() - start_time)
        print(timeTaken)
        yield timeTaken


# input desired anomaly standard deviation cuttoff
# run time around 50 minutes for every single ticker.
# mainObj().main_func(10)
