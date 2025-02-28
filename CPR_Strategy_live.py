import datetime
import time
from ib_async import *
import pdb
# util.startLoop()
import pandas as pd
import pandas_ta as ta


import logging
logging.basicConfig(level=logging.INFO, filename=f'strategy_template_{datetime.date.today()}',filemode='w',format="%(asctime)s - %(message)s")


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=4)


# tickers = [ 'WIPRO','TCS', 'SBIN', 'PNB', "ITC", 'IGL', 'DLF', 'ABB', 'INFY', 'ZOMATO', 'MCX', 'PAYTM' , 'DIXON', 'PRESTIGE', 'LODHA', 'DLF', 'ABB', 'MOTHERSON', 'GLENMARK', 'NYKAA']
tickers = ['DIXON', 'PRESTIGE', 'LODHA', 'DLF', 'ABB', 'MOTHERSON', 'GLENMARK', 'NYKAA', 'GUJGASLTD', 'ZOMATO', 'TIINDIA', 'MCX', 'PAYTM', 'MFSL', 'INDIANB', 'SUNTV', 'DRREDDY', 'JSWENERGY', 'SHREECEM', 'ATUL', 'CUB', 'IPCALAB', 'PVRINOX', 'OFSS', 'OIL', 'NCC', 'DALBHARAT', 'BHEL', 'UNIONBANK', 'INDHOTEL', 'NAUKRI', 'ASHOKLEY', 'PAGEIND', 'BANKINDIA', 'YESBANK', 'SIEMENS', 'BSE', 'CESC', 'ALKEM', 'ZYDUSLIFE', 'JUBLFOOD', 'KEI', 'BSOFT', 'RAMCOCEM', 'CDSL', 'TATACOMM', 'IRCTC', 'DEEPAKNTR', 'ASTRAL', 'HAVELLS', 'CANBK', 'KPITTECH', 'HFCL', 'PFC', 'DELHIVERY', 'HDFCLIFE', 'LTF', 'LTIM', 'POWERGRID', 'RECLTD', 'PNB', 'IGL', 'EICHERMOT', 'POLYCAB', 'GODREJCP', 'SBICARD', 'UBL', 'BOSCHLTD', 'JKCEMENT', 'AXISBANK', 'LICHSGFIN', 'VOLTAS', 'AMBUJACEM', 'SRF', 'SUNPHARMA', 'AARTIIND', 'JIOFIN', 'MPHASIS', 'ICICIBANK', 'RBLBANK', 'GNFC', 'COALINDIA', 'ACC', 'CAMS', 'TVSMOTOR', 'BATAINDIA', 'IEX', 'HAL', 'CIPLA', 'KOTAKBANK', 'PEL', 'MAXHEALTH', 'MARICO', 'APLAPOLLO', 'BEL', 'SBIN', 'ITC', 'NHPC', 'IDEA', 'INDIAMART', 'MARUTI', 'ESCORTS', 'GRANULES', 'LT', 'COFORGE', 'SJVN', 'ABCAPITAL', 'CYIENT', 'BRITANNIA', 'IRFC', 'TATAELXSI', 'SBILIFE', 'UPL', 'TRENT', 'RELIANCE', 'HDFCBANK', 'EXIDEIND', 'DABUR', 'BIOCON', 'VBL', 'WIPRO', 'GRASIM', 'DIVISLAB', 'HDFCAMC', 'POLICYBZR', 'LTTS', 'NMDC', 'ABFRL', 'ATGL', 'SONACOMS', 'ADANIENT', 'GAIL', 'MRF', 'DMART', 'INDIGO', 'IOC', 'TATASTEEL', 'LUPIN', 'HCLTECH', 'TATAPOWER', 'LICI', 'NESTLEIND', 'TATACHEM', 'PETRONET', 'INFY', 'ONGC', 'SAIL', 'PIIND', 'MGL', 'CGPOWER', 'AUBANK', 'SYNGENE', 'CONCOR', 'TECHM', 'JSWSTEEL', 'IRB', 'BPCL', 'NTPC', 'JSL', 'HINDALCO', 'ICICIGI', 'CROMPTON', 'COLPAL', 'TCS', 'CHOLAFIN', 'VEDL', 'HINDPETRO', 'TITAN', 'UNITDSPR', 'ANGELONE']
exchange='NSE'
currency='INR'


contract_objects={}
for tick in tickers:
    print(Stock(tick,exchange,currency))
    contract_objects[tick]=ib.qualifyContracts(Stock(tick,exchange,currency))[0]
print(contract_objects)


def get_daily_cpr_data(ticker_contract):
    logging.info('fetching historical data')



    bars = ib.reqHistoricalData(
    ticker_contract, endDateTime='', durationStr='2 D',
    barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=True,formatDate=2)
    # convert to pandas dataframe:
    
    cprdf = util.df(bars)
    cprdf = cprdf.head(1)
    # cprdf = cprdf.iloc[:-1]



    cprdf['pivot']= (cprdf['high'] + cprdf['low'] + cprdf['close']) / 3   # pivot = (high + low + close)/3
    cprdf['bc'] = ((cprdf['pivot'] + cprdf['low'])/2)    # bc = (pivot + low)/2
    # cprdf['tc']=  ((cprdf['pivot'] - cprdf['bc']) + cprdf['pivot'])   # tc = (pivot - bc) + pivot
    cprdf['tc']=  ((cprdf['pivot'] + cprdf['high']) /2)   # tc =   (pivot + high)/2
  

    
    cprdf['s1'] =  (cprdf['pivot'] * 2)  - cprdf['high'] # s1 = (2*pivot)-high 
    cprdf['s2'] = cprdf['pivot'] - (cprdf['high'] - cprdf['low'] )    # s2 = pivot - (high - low)
    cprdf['s3'] = cprdf['s1'] - (cprdf['high'] - cprdf['low'] ) # s3 = s1 - (high - low)
    cprdf['s4'] = cprdf['s3'] -  (cprdf['s1'] - cprdf['s2'] )   # s4 = s3 - (s1-s2)

    cprdf['r1'] =  (cprdf['pivot']*2)  - cprdf['low']    # r1 = (2* pivot)-low
    cprdf['r2'] = cprdf['pivot'] + (cprdf['high'] - cprdf['low'] )    # r2 = (pivot+(high - low))
    cprdf['r3'] = cprdf['r1'] +  (cprdf['high'] - cprdf['low'] )    # r3 = r1 + (high - low)
    cprdf['r4'] = cprdf['r3'] +  (cprdf['r2'] - cprdf['r1'] )   # r4 = r3 + (r2-r1)
    print(cprdf)



    logging.info('calculated indicators')
    
    return cprdf



def get_historical_data(ticker_contract):
    logging.info('fetching historical data')
    bars = ib.reqHistoricalData(
    ticker_contract, endDateTime='', durationStr='1 D',
    barSizeSetting='5 mins', whatToShow='MIDPOINT', useRTH=True,formatDate=1)
    # convert to pandas dataframe:
    df = util.df(bars)

    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    # print(df)
    # df['sma1']=ta.sma(df.close,20)
    # df['sma2']=ta.sma(df.close,50)
    logging.info('calculated indicators')
    
    return df


def close_ticker_postion(name,closing_price):

    df2=ib.reqPositions()
 
    df2['ticker_name']=[cont.symbol for cont in df2['contract']]
    cont=df2[df2['ticker_name']==name].contract.iloc[0]
    quant=df2[df2['ticker_name']==name].position.iloc[0]
    quant
    print(f'quantity that can you can close  {quant}')
    
    if quant>0:
        #sell
        ord=MarketOrder(action='SELL',totalQuantity=quant)
        ib.placeOrder(cont,ord)
        logging.info("closing position"+'SELL'+name)



def close_ticker_open_orders(ticker):
    ord = ib.openTrades()
    print(f'order is {ord}')
    
    if not ord:
        logging.info("No open trades found. Exiting function.")
        return  # Exit function if there are no open trades
    
    df1 = util.df(ord)
    
    if df1.empty:
        logging.info("No open orders found in DataFrame. Exiting function.")
        return  # Exit function if DataFrame is empty
    
    print(df1)
    print(df1.columns)
    
    df1['ticker_name'] = [cont.symbol for cont in df1['contract']]
    order_object = df1[df1['ticker_name'] == ticker]['order'].iloc[0]
    
    print(order_object)
    ib.cancelOrder(order_object)
    logging.info("Cancelled current order")

def trade_sell_stocks(name, closing_price):
    df2 = ib.reqPositions()
    
    if not df2:
        logging.info("No open positions found. Exiting function.")
        return  # Exit if there are no positions
    
    df2 = util.df(df2)  # Convert list to DataFrame

    if df2.empty:
        logging.info("No position data available. Exiting function.")
        return  # Exit if DataFrame is empty

    df2['ticker_name'] = [cont.symbol for cont in df2['contract']]
    
    if name not in df2['ticker_name'].values:
        logging.info(f"No open positions found for {name}. Exiting function.")
        return  # Exit if there is no position for the given ticker

    cont = df2[df2['ticker_name'] == name].contract.iloc[0]
    quant = df2[df2['ticker_name'] == name].position.iloc[0]

    logging.info(f"Closing position for {name} with quantity {quant}")

    order = MarketOrder('SELL', quant)
    trade = ib.placeOrder(cont, order)
    
    logging.info(f"Closed position for {name} at {closing_price}")




def trade_buy_stocks(ticker,closing_price,quantitys):
    global current_balance
    #market order
    contract = contract_objects[ticker]
    ord=MarketOrder(action='BUY',totalQuantity=quantitys)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    logging.info(trade)
    #stop loss order
    logging.info("placed market order")




def strategy(data, daily_cpr_df,ticker,quantity):
    global current_balance
    logging.info('inside strategy')
    print(ticker)
    print(data)
    
  


    # buy_condition=True
    current_balance=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
    current_balance=200000
    if current_balance>data.close.iloc[-1]:
        if data.close.iloc[-1]>daily_cpr_df['tc'].iloc[-1] and data.close.iloc[-1]<daily_cpr_df['r1'].iloc[-1] :
            logging.info('buy condiiton satisfied')
            trade_buy_stocks(ticker,data.close.iloc[-1],quantity)
        else :
            logging.info('no condition satisfied')
    else:
        logging.info('we dont have enough money')
        logging.info('current balance is',current_balance,'stock price is ',data.close[-1])




def main_strategy_code():
    
    print("inside main strategy")

    pos=ib.reqPositions() #for check position in our portfolio
    if len(pos)==0:
        pos_df=pd.DataFrame([])
    else:
        pos_df=util.df(pos)
        pos_df['name']=[cont.symbol for cont in pos_df['contract']]
        pos_df=pos_df[pos_df['position']>0]
    print(pos_df)
    ord=ib.reqAllOpenOrders() # for check have any open order
    if len(ord)==0:
        ord_df=pd.DataFrame([])
    else:
        ord_df=util.df(ord)
        ord_df['name']=[cont.symbol for cont in ord_df['contract']]
    print(ord_df)
    logging.info('fetched order_df and position_df')


    for ticker in tickers:
        logging.info(ticker)
        print('ticker name is',ticker,'################')
        ticker_contract=contract_objects[ticker]
        hist_df=get_historical_data(ticker_contract) #get historical data using function
        print(hist_df)
        daily_cpr_df=get_daily_cpr_data(ticker_contract) #get historical data with CPR levels using function
        print(daily_cpr_df)
        print(hist_df.close.iloc[-1])
        capital=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
        print(capital)
        capital=200000
        quantity=int((capital/10)/hist_df.close.iloc[-1])  #if you want to change how much quantitay to buy according to risk can change hear
        print(f'Quantity that can you buy  {ticker} {quantity}')
        logging.info('checking condition')   

        sl_price = daily_cpr_df['bc'].iloc[0]
        target_price = daily_cpr_df['r1'].iloc[0]
        print(f'your SL price is {sl_price}') 
        if quantity==0:
            logging.info('we dont have enough money so we cannot trade')
            pass

        if pos_df.empty:
                logging.info('we dont have any position')
                strategy(hist_df,daily_cpr_df,ticker,quantity=quantity)


        elif len(pos_df)!=0 and ticker not in pos_df['name'].tolist():
                logging.info('we have some position but current ticker is not in position')
                strategy(hist_df,daily_cpr_df,ticker,quantity=quantity)

        elif len(pos_df)!=0 and ticker in pos_df["name"].tolist():
                logging.info('we have some position and current ticker is in position')

                sl_price = daily_cpr_df['bc'].iloc[0]
                target_price = daily_cpr_df['r1'].iloc[0]
                print(f'your SL price is {sl_price}') 
                print(f'your target price is {target_price}')
                                                                                                                                        
                if hist_df.close.iloc[-1] <=sl_price:
                    logging.info('current ticker position SL Triggered')
                    trade_sell_stocks(ticker,hist_df.close.iloc[-1])

                if hist_df.close.iloc[-1]>=daily_cpr_df['r1'].iloc[0]:
                    logging.info('close current ticker position')
                    trade_sell_stocks(ticker,hist_df.close.iloc[-1])
                


    # close position interaday             
    close_hour,close_min=15,20
    close_position_time=datetime.datetime(current_time.year,current_time.month,current_time.day,close_hour,close_min)
    if datetime.datetime.now()==close_position_time:
            logging.info('close current ticker postion')
            trade_sell_stocks(ticker,hist_df.close.iloc[-1])
   

current_time=datetime.datetime.now()
print(current_time)

print(datetime.datetime.now())
#start time
start_hour,start_min=7,10
#end time
end_hour,end_min=23,30
start_time=datetime.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
end_time=datetime.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)
print(start_time)
print(end_time)

candle_size = 300

while datetime.datetime.now()<end_time:
    # Run your function
    main_strategy_code()
    now = datetime.datetime.now()
    print(now)
    seconds_until_next_minute = candle_size - now.second+1
    print(seconds_until_next_minute)
    # Sleep until the end of the current minute
    time.sleep(seconds_until_next_minute)
