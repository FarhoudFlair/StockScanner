# Imports
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
from pandas import ExcelWriter
import pandas_datareader as pdr_lib
import yfinance as yf
import pandas as pd
import datetime
import time
yf.pdr_override()
#indicies = [si.tickers_sp500(), si.tickers_nasdaq(), si.tickers_dow()]
#index_names = ['^GSPC', '^IXIC', '^DJI'] 
#index_names_readable = ['S&P500', 'NASDAQ', 'DOWJONES']

excel_file = "TSX_constituents.csv"
data = pd.read_csv(excel_file)

# Extract the values from the second column (RS_Rating)
stockNames = data['Symbol'].tolist()
print(stockNames)
#second_column_values = data.iloc[:, 0].tolist()
# Create a .txt file and write the comma-separated values
#output_file = f"MinerviniWatchlist.txt"
# with open(output_file, 'a') as f:
#     f.write(','.join(map(str, stockNames)))


for i in range(2, 3):    # Variables
    print('INDEX: TSX')
    tickers = stockNames
    #tickers.append(si.tickers_other())
    tickers = [str(item).replace(".", "-") for item in tickers] # Yahoo Finance uses dashes instead of dots
    tickers = [str(item) + ".TO" for item in tickers]
    #index_name = '^GSPC' # S&P 500
    index_name = "^GSPTSE"
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    exportList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])
    returns_multiples = []

    # Index Returns
    index_df = pdr.get_data_yahoo(index_name, start_date, end_date)
    index_df['Percent Change'] = index_df['Adj Close'].pct_change()
    index_return = (index_df['Percent Change'] + 1).cumprod()[-1]

    # Find top 30% performing stocks (relative to the S&P 500)
    for ticker in tickers:
        # Download historical data as CSV for each stock (makes the process faster)
        try:
            df = pdr.get_data_yahoo(ticker, start_date, end_date)
            if index_df.empty:
                print(f'{ticker} returned no data')
                tickers.remove(ticker)
                continue
            else:
                print(f'{ticker} downloaded')
        except Exception as e:
            error_message = str(e)
            print(error_message)
            print(f"Error downloading data for {ticker}")
            tickers.remove(ticker)
            continue
        try:
            df.to_csv(f'screenerTickersSPXTSX/{ticker}.csv')
        except Exception as e:
            error_message = str(e)
            print(error_message)
            print(f"Error here on writing to csv file for {ticker}")
            continue

        #check for empty excel file in row 2
        excel_file = f'screenerTickersSPXTSX/{ticker}.csv'  
        data = pd.read_csv(excel_file)

        # Check if row 2 is empty
        try:
            row_2 = data.iloc[1]  # Get the second row
            is_empty = row_2.isnull().all()
        except IndexError as e:
            print("IndexError:", e)
            is_empty=True
            tickers.remove(ticker)
            continue

        if is_empty:
            print("Row 2 is empty.")
            tickers.remove(ticker)
            continue
        else:
            print("Row 2 is not empty.")
        # Calculating returns relative to the market (returns multiple)
        df['Percent Change'] = df['Adj Close'].pct_change()
        stock_return = (df['Percent Change'] + 1).cumprod()[-1]
        
        returns_multiple = round((stock_return / index_return), 2)
        returns_multiples.extend([returns_multiple])
        
        print (f'Ticker {tickers.index(ticker)}: {ticker}; Returns Multiple against SPXTSX: {returns_multiple}\n')
        time.sleep(0.2)

    # Creating dataframe of only top 30%
    rs_df = pd.DataFrame(list(zip(tickers, returns_multiples)), columns=['Ticker', 'Returns_multiple'])
    rs_df['RS_Rating'] = rs_df.Returns_multiple.rank(pct=True) * 100
    rs_df = rs_df[rs_df.RS_Rating >= rs_df.RS_Rating.quantile(.70)]

    # Checking Minervini conditions of top 30% of stocks in given list
    rs_stocks = rs_df['Ticker']
    for stock in rs_stocks:    
        try:
            df = pd.read_csv(f'screenerTickersSPXTSX/{stock}.csv', index_col=0)
            sma = [50, 150, 200]
            for x in sma:
                df["SMA_"+str(x)] = round(df['Adj Close'].rolling(window=x).mean(), 2)
            
            # Storing required values 
            currentClose = df["Adj Close"][-1]
            moving_average_50 = df["SMA_50"][-1]
            moving_average_150 = df["SMA_150"][-1]
            moving_average_200 = df["SMA_200"][-1]
            low_of_52week = round(min(df["Low"][-260:]), 2)
            high_of_52week = round(max(df["High"][-260:]), 2)
            RS_Rating = round(rs_df[rs_df['Ticker']==stock].RS_Rating.tolist()[0])
            
            try:
                moving_average_200_20 = df["SMA_200"][-20]
            except Exception:
                moving_average_200_20 = 0

            # Condition 1: Current Price > 150 SMA and > 200 SMA
            condition_1 = (currentClose > moving_average_150) and (currentClose > moving_average_200)
            
            # Condition 2: 150 SMA and > 200 SMA
            condition_2 = moving_average_150 > moving_average_200

            # Condition 3: 200 SMA trending up for at least 1 month
            condition_3 = moving_average_200 > moving_average_200_20
            
            # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
            condition_4 = (moving_average_50 > moving_average_150) and (moving_average_50 > moving_average_200)
            
            # Condition 5: Current Price > 50 SMA
            condition_5 = currentClose > moving_average_50
            
            # Condition 6: Current Price is at least 30% above 52 week low
            condition_6 = currentClose >= (1.3*low_of_52week)
            
            # Condition 7: Current Price is within 25% of 52 week high
            condition_7 = currentClose >= (.75*high_of_52week)
            
            # If all conditions above are true, add stock to exportList
            if(condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7):
                exportList = exportList.append({'Stock': stock, "RS_Rating": RS_Rating ,"50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)
                print (stock + " made the Minervini requirements")
        except Exception as e:
            print (e)
            print(f"Could not gather data on {stock}")

    exportList = exportList.sort_values(by='RS_Rating', ascending=False)
    print('\n', exportList)
    writer = ExcelWriter(f"ScreenOutputSPXTSX.xlsx")
    exportList.to_excel(writer, "Sheet1")
    writer.save()


    # excel_file = f"ScreenOutputSPXTSX.xlsx"
    # data = pd.read_excel(excel_file, engine='openpyxl')

    # # Extract the values from the second column (RS_Rating)
    # stockNames = data['Stock']

    # # Create a .txt file and write the comma-separated values
    # output_file = f"MinerviniWatchlist.txt"
    # with open(output_file, 'a') as f:
    #     f.write(','.join(map(str, stockNames)))

    # print("Stock Names written to", output_file)