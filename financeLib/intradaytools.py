#!/usr/bin/env python3
# intradaytools.py
# library to be used across all analysis scripts

import redis
import datetime
import os
import requests
import sys
from bs4 import BeautifulSoup, NavigableString

# scrape website, return html
def scrape(website):

    set_url = website
    cal_resp = requests.get(set_url)
    cal_data = cal_resp.text
    data = BeautifulSoup(cal_data, 'lxml')

    return data

# create a temporary file, will be used to compare to possible exsisting data
def temp(ticker, market):

    data = scrape('https://www.google.com/finance/getprices?q=' + str(ticker.upper()) + '&x=' + str(market.upper()) + '&i=60&p=30d&f=d,c,h,l,o,v')
    data = str(data)
    with open('/intradata/temp', 'w') as f:
        f.write(data)
    r = redis.Redis('localhost')
    r.set('temp',data)

# find the market that the particular ticker is traded on
def findmarket(ticker):
	
    data = scrape('https://www.google.com/finance?q=' + ticker)
    title = str(data.title)
    if 'NASDAQ' in title:
        return 'NASD'
    else:
        return 'NYSE'

# input string of comma delimited intraday data, return dict which is ready to be used for calulations
def parsefile(lines):

    tempfile = {}
    days = []
    mins = 0
    for x in range(len(lines)):
        split = lines[x].split(',')
        if str(split[0]).startswith('a'):
            currentday = split[0]
            days.append(currentday)
            tempfile[currentday + 'days'] = split[0]
            tempfile[currentday + 'mins'] = mins
            tempfile[currentday + 'data'] = ''
            tempfile[currentday + 'data'] += str(lines[x])
        else:
            if len(days) != 0 and x + 1 != len(lines):
                tempfile[str(currentday) + 'mins'] += 1
                tempfile[str(currentday) + 'data'] += str(lines[x])

    return tempfile, days

# input dict of averaged data, return the highest and lowest points as well as an array to be used for graphs
def minmax(dictionary, dataset):

    lowval = dictionary[str(0) + dataset]
    lowmin = 0
    lowamount = 0
    highval = dictionary[str(0) + dataset]
    highmin = 0
    highamount = 0
    allvals = []

    for x in range(390):
        if dictionary[str(x) + dataset] < lowval:
            lowval = dictionary[str(x) + dataset]
            lowmin = x
            lowamount = '{:.2f}'.format(dictionary[str(x) + 'close'])
        if dictionary[str(x) + dataset] > highval:
            highval = dictionary[str(x) + dataset]
            highmin = x
            highamount = '{:.2f}'.format(dictionary[str(x) + 'close'])
        allvals.append(dictionary[str(x) + dataset])

    # calculate times (based on market open (6:30 GMT+8)
    today = datetime.datetime.today()
    marketopen = datetime.datetime(today.year, today.month, today.day, 6, 30)
    lowdelta = datetime.timedelta(minutes = int(lowmin))
    highdelta = datetime.timedelta(minutes = int(highmin))
    marketlow = marketopen + lowdelta
    markethigh = marketopen + highdelta
    marketlow = str(marketlow.strftime("%I:%M%p"))
    markethigh = str(markethigh.strftime("%I:%M%p"))

    return lowval, marketlow, lowamount, highval, markethigh, highamount, allvals

