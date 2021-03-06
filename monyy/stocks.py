from iexfinance.stocks import get_historical_data
from iexfinance.stocks import Stock as Stocks
from iexfinance.stocks import get_crypto_quotes
from datetime import datetime, timedelta


def returnStock(abbreviation):
    stockprice = Stocks(abbreviation).get_price()
    return stockprice

def stockPriceOnDay(abbreviation, on_day):
    start = datetime.now()
    day = on_day
    end = start-timedelta(days=on_day)
    #print(start)
    #print(end)
    ok = False
    while ok is False:
        try:
            stockprices = get_historical_data(abbreviation, end, start)
            stockprices_on_end = stockprices[str(end.date())]
            close_on_end = stockprices_on_end['close']
            ok = True
        except Exception as error:
            #print("exception is "+str(error))
            pass
        day = day+1
        end = start-timedelta(days=day)
        #print(day)
    return close_on_end

def closingPricesFrom(abbreviation, on_day):
    start = datetime.now()
    end = start-timedelta(days=on_day)
    print(start)
    print(end)
    stockprices = get_historical_data(abbreviation, end, start)
    count = 1
    closing_prices = []
    while count<=on_day:
        day = start-timedelta(days=count)
        try:
            stockprices_on_end = stockprices[str(day.date())]
            close_on_end = stockprices_on_end['close']
        except:
            pass
        closing_prices.append(close_on_end)
        count=count+1
    return closing_prices

"""Bitcoin USD (BTCUSDT)
EOS USD (EOSUSDT)
Ethereum USD (ETHUSDT)
Binance Coin USD (BNBUSDT)
Ontology USD (ONTUSDT)
Bitcoin Cash USD (BCCUSDT)
Cardano USD (ADAUSDT)
Ripple USD (XRPUSDT)
TrueUSD (TUSDUSDT)
TRON USD (TRXUSDT)
Litecoin USD (LTCUSDT)
Ethereum Classic USD (ETCUSDT)
MIOTA USD (IOTAUSDT)
ICON USD (ICXUSDT)
NEO USD (NEOUSDT)
VeChain USD (VENUSDT)
Stellar Lumens USD (XLMUSDT)
Qtum USD (QTUMUSDT)
"""
def returnCrypto(abbreviation):
    return get_crypto_quotes(abbreviation)

def getTaxRate(val):
    taxedAmount = 0
    bracket = [10000, 40000, 80000, 160000, 200000, 500000, 100000000]
    rate = [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    
    i = 0
    while (val > bracket[i]):
        taxedAmount += bracket[i]*rate[i] #TAX MATH
        val -= bracket[i]
        i+=1
    
    taxedAmount += val*rate[i]
    return taxedAmount
    
    
#r = int(input("Tax math"))
#print(getTaxRate(r))
# print(returnStock('GOOGL'))  
# print(stockPriceOnDay('GOOGL', 2))
# print(closingPricesFrom('GOOGL', 14))
