import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# global vars
mysymbol = 'MSFT'   # stock symbol
start = '1993-12-31'    # start date
end = '2023-12-31'    # end date
money = 10000   # starting money

def download_stock_data():  # download stock data from yahoo finance
    return yf.download(mysymbol, start=start, end=end, interval='1D')   

def do_sma_calcs(stockdata):    # do moving averages calculations
    stockdata['fastMA'] = stockdata['Close'].rolling(window=10).mean()  # 10 day moving
    stockdata['slowMA'] = stockdata['Close'].rolling(window=200).mean() # 200 day moving
    return stockdata

def run_strategy(stockdata):
    cash = money  # starting money
    num_shares = 0  # number of shares
    my_trades = []  # list to hold trades
    
    # loop through days
    for i in range(200, len(stockdata)):
        current_price = stockdata['Close'].iloc[i]  # get current price of stock at day i 
        # check if fast ma crosses above slow ma
        if stockdata['fastMA'].iloc[i] > stockdata['slowMA'].iloc[i] and stockdata['fastMA'].iloc[i-1] <= stockdata['slowMA'].iloc[i-1]:
            if cash > 0:  # we have money to buy
                shares = int(cash / current_price)  # buy as many shares as we can
                price = shares * current_price  # total price of shares
                cash = cash - price # subtract price from cash
                num_shares = num_shares + shares    # add shares to total
                my_trades.append(('BUY', stockdata.index[i], shares, current_price))    # add trade to list
        
        # check if fast ma crosses below slow ma
        if stockdata['fastMA'].iloc[i] < stockdata['slowMA'].iloc[i] and stockdata['fastMA'].iloc[i-1] >= stockdata['slowMA'].iloc[i-1]:    
            if num_shares > 0:  # we have shares to sell
                money_back = num_shares * current_price # get money back from selling shares
                cash = cash + money_back    # add money back to cash
                my_trades.append(('SELL', stockdata.index[i], num_shares, current_price))   # add trade to list
                num_shares = 0  # reset shares to 0
    
    # sell everything at end if we still have shares
    if num_shares > 0:
        final_sale = num_shares * stockdata['Close'].iloc[-1]   # sell all shares at final price
        cash = cash + final_sale    # add final sale to cash
        my_trades.append(('SELL', stockdata.index[-1], num_shares, stockdata['Close'].iloc[-1]))    # add trade to list
    
    return cash, my_trades

def make_plot(stockdata, trades):   # make plot of stock data and trades
    plt.figure(figsize=(30, 5)) # set size of plot
    plt.plot(stockdata.index, stockdata['Close'], label='Price')    # plot price
    plt.plot(stockdata.index, stockdata['fastMA'], label='Fast MA')  # plot fast ma
    plt.plot(stockdata.index, stockdata['slowMA'], label='Slow MA') # plot slow ma
    
    buys = []   # get buy points
    for t in trades:    # loop through trades
        if t[0] == 'BUY':   # check if trade is buy
            buys.append(t[1])   # add date to buys list
            
    sells = []  # get sell points
    for t in trades:    # loop through trades
        if t[0] == 'SELL':  # check if trade is sell
            sells.append(t[1])  # add date to sells list
    
    plt.scatter(buys, stockdata.loc[buys, 'Close'], color='green', marker='^', label='Buy')  # plot buy points
    plt.scatter(sells, stockdata.loc[sells, 'Close'], color='red', marker='v', label='Sell')    # plot sell points
    plt.title(f'Trading Results for {mysymbol}')    # set title
    plt.xlabel('Date')  # set x label
    plt.ylabel('Price') # set y label
    plt.legend()    # show legend
    plt.show()  # show plot

# run everything
data = download_stock_data()    # download stock data
data = do_sma_calcs(data)   # do moving averages calculations
ending_balance, all_trades = run_strategy(data)   # run strategy

print(f"Started with: ${money}")
print(f"Ended with: ${ending_balance:.2f}")
print(f"Profit %: {(ending_balance - money) / money * 100:.2f}%")
print(f"Number of trades made: {len(all_trades)}")

make_plot(data, all_trades) # make plot of stock data and trades