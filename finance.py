# finance.py
# finance flask application

import sys
from flask import Flask, render_template, request, url_for
from financeLib.intradaytools import *
from financeLib.charts import *

# initialize flask app
application = Flask(__name__)

# create form
@application.route("/finance/")
def form():

    return render_template('form.html')

# get information from form, run volatility calculations
@application.route("/finance/volatility/", methods=['POST'])
def volatility():
	
    # pull ticker from from
    ticker = request.form['ticker']
	
    # find market based on ticker (uses google finance)
    market = findmarket(ticker)

    ticker = ticker.upper()
    market = market.upper()

    # get intraday information for the last 15 days, save to temp file
    temp(ticker, market)

    # open tempfile, save lines, delete temp file.
    with open ('/intradata/temp') as f:
        templines = f.readlines()
    os.remove('/intradata/temp')

    # check for exsisting data files
    filecheck = os.path.isfile('/intradata/' + ticker)

    # create new ticker data file if one does not exist or add new lines lines to existing files
    if filecheck == False:
        with open('/intradata/' + ticker, 'w') as f:
            newfile = f.writelines(templines[7:-1])
    else:
        # parse exsiting data files, and new temp data files
        tempfile, tempdays = parsefile(templines)
        with open('/intradata/' + ticker) as f:
            existinglines = f.readlines()
        existingfile, existingdays = parsefile(existinglines)

        # merge files, get data older than 15 days from existing file & get data within current 15 days from temp file
        mergedfile = ''
        for x in range(len(existingdays)):
            if existingdays[x] in tempdays:
                # recent data within the last 15 days - should append from new data (tempfile)
                pass
            else:
                # older data no longer in the last 15 days - append from existing data (existingfile)
                mergedfile += str(existingfile[str(existingdays[x]) + 'data'])

        # append all new data (will override old similar data, and keep current day up todate)
        for x in range(len(tempdays)):
            mergedfile += str(tempfile[str(tempdays[x]) + 'data'])

        # overide exsiting file with new data
        with open('/intradata/' + ticker, 'w') as f:
            f.write(mergedfile)

    # open ticker data file and use data
    with open('/intradata/' + ticker) as f:
        data = f.readlines()

    # create dictionary for data storage && store data / run calculations for each min (390 mins per day) 
    intraday = {}
    average = {}
    day = 0
    for line in data: # every line = 1 min of data
        split = line.split(',')
        if str(split[0]).startswith('a'): # replace unix time stamp (which starts with 'a') for new day with 0
            split[0] = str(0) # split[0] = int ranging 0 - 390. represents time: 0 = 6:30 (market open) 390 = 13:00 (market close) 

        intraday[str(day) + split[0] + 'high'] = float(split[2]) # split[2] = current min high $ value 
        intraday[str(day) + split[0] + 'low'] = float(split[3]) # split[3] = current min low $ value
        intraday[str(day) + split[0] + 'open'] = float(split[4]) # split[4] = current min open $ value
        intraday[str(day) + split[0] + 'close'] = float(split[1]) # split[1] = current min close $ value
        intraday[str(day) + split[0] + 'vol'] = int(split[5]) # split[5] = current min volume # of shares

        # volatility formulas
        intraday[str(day) + split[0] + 'volatilityByMin'] = ((float(split[1]) / float(split[4])) - int(1)) * int(100)
        intraday[str(day) + split[0] + 'volatilityVsMktOpen'] = ((float(split[1]) / float(intraday[(str(day)) + '0' + 'open'])) - int(1)) * int(100)

        # create storage locations for averages
        average[split[0] + 'volatilityByMin'] = 0
        average[split[0] + 'volatilityVsMktOpen'] = 0
        average[split[0] + 'close'] = 0

        # day counter.  If at any time current min == 390 mark one complete day
        if int(split[0]) == int(390):
            day += 1

    # summation for all individual days data 
    for x in range(day):
        for x2 in range(390):
            average[str(x2) + 'volatilityByMin'] += float(intraday[str(x) + str(x2) + 'volatilityByMin'])
            average[str(x2) + 'volatilityVsMktOpen'] += float(intraday[str(x) + str(x2) + 'volatilityVsMktOpen'])
            average[str(x2) + 'close'] += float(intraday[str(x) + str(x2) + 'close'])

    # calculate averages based on above summation / # of days of data stored in ticker file
    for x in range(390):
        average[str(x) + 'volatilityByMin'] /= int(day)
        average[str(x) + 'volatilityVsMktOpen'] /= int(day)
        average[str(x) + 'close'] /= int(day)

    # get min value / max value / arrays to be used for charting
    lowvalVBM, lowtimeVBM, lowamountVBM, highvalVBM, hightimeVBM, highamountVBM, allvalsVBM = minmax(average, 'volatilityByMin')
    lowvalVMO, lowtimeVMO, lowamountVMO, highvalVMO, hightimeVMO, highamountVMO, allvalsVMO = minmax(average, 'volatilityVsMktOpen')

    graphVBM = createLineGraph('Volatility by Minute', 'volByMin', allvalsVBM)
    displayVBM = displayLineGraph('volByMin')	

    graphVMO = createLineGraph('Volatility by Minuite Vs. Market Open', 'volVsMktOpen', allvalsVMO)
    displayVMO = displayLineGraph('volVsMktOpen')

    return render_template('volatility.html', ticker=ticker, market=market, highamountVBM=highamountVBM, highvalVBM=highvalVBM, hightimeVBM=hightimeVBM, lowamountVBM=lowamountVBM, lowvalVBM=lowvalVBM, lowtimeVBM=lowtimeVBM, highamountVMO=highamountVMO, highvalVMO=highvalVMO, hightimeVMO=hightimeVMO, lowamountVMO=lowamountVMO, lowtimeVMO=lowtimeVMO, lowvalVMO=lowvalVMO, graphVBM=graphVBM, displayVBM=displayVBM, graphVMO=graphVMO, displayVMO=displayVMO)




if __name__ == "__main__":
    application.run(host="0.0.0.0")
