import requests
import json
import pandas as pd
import smtplib
import time


def sendemail(message):
    email = 'kannomonster@gmail.com'
    password = 'CandyZ.1999'

    header = 'From: %s\n' % (email)
    header += 'To: %s\n' % (email)
    header += 'Cc: %s\n' % (email)
    header += 'Subject: %s\n\n' % ('SMA Alert')
    message = header + message

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(email, password)
    problems = server.sendmail(email, email, message)
    server.quit()
    return problems


def download_data(ticker):
    url = 'https://api.iextrading.com/1.0/stock/%s/chart/5y' % (ticker)
    response = requests.get(url)
    data = json.loads(response.text)
    dataframe_li = []
    for d in data:
        temp = [d['open'], d['high'], d['low'], d['close'], d['volume'], d['date']]
        dataframe_li.append(temp)

    df = pd.DataFrame(dataframe_li, columns=['open', 'high', 'low', 'close', 'volume', 'date'])
    return df

def precent_chage(new, old):
	return (((new - old) / old) * 100.0)


file_name = 'symbols.txt'
sma_window = 200

f = open(file_name)
line = f.readline()
symbols = line.split(',')
print (symbols)

current_date = ''
prev_date = ''

while True:
    data = download_data('SPY')
    current_date = data['date'].iloc[-1]

    if current_date != prev_date or True:
        prev_date = current_date
        msg = ''
        print ('alert fired')
        for s in symbols:
            data = download_data(s)
            sma = data['close'].rolling(window=sma_window).mean()

            currentSMA = sma.iloc[-1]
            currentHigh = data['high'].iloc[-1]
            currentLow = data['low'].iloc[-1]
            currentOpen = data['open'].iloc[-1]
            currentClose = data['close'].iloc[-1]

            if msg == '':
            	msg += data['date'].iloc[-1] + '\n\n'
            msg += s + ' $' + str(currentClose) + '\n'
            msg += 'daily change: ' + str(round(precent_chage(currentClose, currentOpen), 2))
            msg += '% weekly change: '+ str(round(precent_chage(currentClose, data['close'].iloc[-5]))) + '%\n'
            msg += 'distance from ' + str(sma_window) + ' sma: ' + str(round(precent_chage(currentClose, currentSMA))) + '%\n'

            if currentClose > currentSMA and data['close'].iloc[-2] < currentSMA:
                msg += s + ' crossed above the ' + str(sma_window) + ' day sma' + '\n'

            elif currentClose < currentSMA and data['close'].iloc[-2] > currentSMA:
                msg += s + ' crossed bellow the ' + str(sma_window) + ' day sma' + '\n'

            elif currentHigh >= currentSMA and currentClose < currentSMA:
                msg += s + ' high touched the ' + str(sma_window) + ' day sma' + '\n'

            elif currentLow <= currentSMA and currentClose > currentSMA:
                msg += s + ' low touched the ' + str(sma_window) + ' day sma' + '\n'

            msg += '\n'

        if len(msg) != 0:
            sendemail(msg)
            print ('mail sent')

    time.sleep(60)
