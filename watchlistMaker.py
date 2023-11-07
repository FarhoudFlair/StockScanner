from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
from pandas import ExcelWriter
import pandas_datareader as pdr_lib
import yfinance as yf
import pandas as pd
import datetime
import time 
output_file = f"MinerviniWatchlist.txt"
with open(output_file, 'w') as f:
    f.write('')

index_names_readable = ['S&P500', 'NASDAQ', 'DOWJONES', 'SPXTSX']
TV_Prefix = ['', '', '', "TSX:"]
for indexName in range(0,4):
    excel_file = f"ScreenOutput{index_names_readable[indexName]}.xlsx"
    data = pd.read_excel(excel_file, engine='openpyxl')

    # Extract the values from the second column (RS_Rating)
    stockNames = data['Stock']
    #tickers = [str(item).replace(".TO", "") for item in stockNames] # Yahoo Finance uses dashes instead of dots
    modified_tickers = [item[:-3] if item.endswith(".TO") else item for item in stockNames]
    
    # modified_tickers = []

    # for item in stockNames:
    #     if item.endswith(".TO"):
    #         modified_tickers.append(item[:-3])
    #     else:
    #         modified_tickers.append(item)

    modified_tickers = [str(item).replace("-", ".") for item in modified_tickers] # Yahoo Finance uses dashes instead of dots
    modified_tickers = [f"{TV_Prefix[indexName]}" + str(item) for item in modified_tickers]
    print(modified_tickers) 
    # Create a .txt file and write the comma-separated values
    output_file = f"MinerviniWatchlist.txt"
    with open(output_file, 'a') as f:
        f.write(','.join(map(str, modified_tickers)))

    print("Stock Names written to", output_file)