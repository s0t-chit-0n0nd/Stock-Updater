from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

import datetime
import pandas as pd
import numpy as np
from nsepython import *
import pprint
from googleapiclient import discovery #write in Gsheet

def nse_quote(symbol):
    symbol = nsesymbolpurify(symbol)

    if any(x in symbol for x in fnolist()):
        payload = nsefetch('https://www.nseindia.com/api/quote-derivative?symbol='+symbol)
    else:
        payload = nsefetch('https://www.nseindia.com/api/quote-equity?symbol='+symbol)
    return payload
def is_market_open():
    l = nse_marketStatus()
    k= list(l.values())                 #4types of market
    openis = list(k[0][0].keys())
    market_status = k[0][0][openis[1]] #equitymarketclosed/open
    return market_status
def stock_details(SPREADSHEET_ID,range_sheet):
    try: 
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=range_sheet).execute()
        values = result.get('values', [])
        print(np.matrix(values))
        # print(values)
        # pprint.pprint(values)
    
        if not values:
            print('No data found.')
        return values
            
    except HttpError as err:
        print(err)
def stock_lastprices(START,END,values,currentPrices,percent_change):
    currentPrices =[]
    percent_change = []
    for i in range(START,END):
        print(values[i][0],end="\t")
        print(nse_eq(values[i][0])['priceInfo']['lastPrice'],end="\t")
        print(nse_eq(values[i][0])['priceInfo']['change'])
        name = values[i][0]

        if(len(name) != 0):
            currentPrices.append([nse_eq(values[i][0])['priceInfo']['lastPrice']])
            percent_change.append([nse_eq(values[i][0])['priceInfo']['lastPrice']])
        else:
            print("No stock name at",i+2)

    # return currentPrices,percent_change
#  write current price in Gsheets
def update_current_Prices(SHEETNAME,END,current_price,rowOfStockNameStart,ColumnOfCurrentPrice):
    # SAMPLE_SPREADSHEET_ID = '1AGa2EAdTE0AEE243utzlAJGeWwjD5yhNgU8-GFSyC_A'
    current_range= SHEETNAME+"!"+ColumnOfCurrentPrice+rowOfStockNameStart+":"+ColumnOfCurrentPrice+str(END+2)
    ValueInputOption = "USER_ENTERED"
    value_current_rangebody = {"values" : current_price}

    request = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                                    range=current_range, 
                                                    valueInputOption=ValueInputOption, 
                                                    body=value_current_rangebody)
    response = request.execute()# pprint(response)

    last_updated()
def last_updated():
    x = datetime.datetime.now()
    # print(type(x))
    current_range= SHEETNAME+"!E2"
    ValueInputOption = "USER_ENTERED"
    updatedon=[]
    updatedon.append([str(x.strftime("%H:%M {%d %b}"))])
    value_current_rangebody = {"values" : updatedon}

    request = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                                    range=current_range, 
                                                    valueInputOption=ValueInputOption, 
                                                    body=value_current_rangebody)
    response = request.execute()

def write_is_market_open(SHEETNAME,at):
    # SAMPLE_SPREADSHEET_ID = '1AGa2EAdTE0AEE243utzlAJGeWwjD5yhNgU8-GFSyC_A'
    current_range= SHEETNAME+"!"+at
    ValueInputOption = "USER_ENTERED"
    status= is_market_open()
    enter=[[status]]
    value_current_rangebody = {"values" : enter}#list of lists

    request = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                                    range=current_range, 
                                                    valueInputOption=ValueInputOption, 
                                                    body=value_current_rangebody)
    response = request.execute()# pprint(response)
def write_link(SHEETNAME,values,at,START,END):
    current_range= SHEETNAME+"!"+at+str(START)+":"+at+str(END+2)
    ValueInputOption = "USER_ENTERED"
    enter=[]
    for i in range(END):
        name = values[i][0]
        enter.append(["https://www.google.com/finance/quote/"+name+":NSE"])
    # print(enter)
    value_current_rangebody = {"values" : enter}#list of lists

    request = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                                    range=current_range, 
                                                    valueInputOption=ValueInputOption, 
                                                    body=value_current_rangebody)
    request.execute()
def update_change(SHEETNAME,END,list_percent_change,rowOfStockNameStart,ColumnOfCurrentPrice):
    # SAMPLE_SPREADSHEET_ID = '1AGa2EAdTE0AEE243utzlAJGeWwjD5yhNgU8-GFSyC_A'
    current_range= SHEETNAME+"!"+ColumnOfCurrentPrice+rowOfStockNameStart+":"+ColumnOfCurrentPrice+str(END+2)
    ValueInputOption = "USER_ENTERED"
    value_current_rangebody = {"values" : list_percent_change}

    request = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                                                    range=current_range, 
                                                    valueInputOption=ValueInputOption, 
                                                    body=value_current_rangebody)
    response = request.execute()# pprint(response)
def update_sheet(START):
    write_is_market_open(SHEETNAME,"A1")
    place_of_number_of_stock = SHEETNAME+"!"+"B2"#tis have to be correctly user written
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range=place_of_number_of_stock).execute()
    END_ROW = int(result.get('values', [])[0][0])
    link_at_column = "N"
    range_stocks = SHEETNAME+"!"+"B"+"3"+":"+"N"+str(END_ROW+2)
    stockdetails = stock_details(SAMPLE_SPREADSHEET_ID,range_stocks)    #2D array with stock details
    current_price=[]
    percent_change = []
    stock_lastprices(START,END_ROW,stockdetails,current_price,percent_change)            #2D-list of current prices of stocks {[[7],[69]]}
    
    update_current_Prices(SHEETNAME,END_ROW,current_price,"3","E")
    update_change(SHEETNAME,END_ROW,percent_change,"3","L")
    # write_link(SHEETNAME,stockdetails,link_at_column,3,END_ROW)

    print(current_price)
    print(percent_change)
    print("\nupdated prices of stocks")

# SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = 'D:\Lakshay\P\Investing\keys.json' 
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)
# Call the Sheets API
sheet = service.spreadsheets()

SHEETNAME = "GCurrent"
SAMPLE_SPREADSHEET_ID = '1AGa2EAdTE0AEE243utzlAJGeWwjD5yhNgU8-GFSyC_A'
START = 0
# update_sheet(START)

# # print(nse_eq("JUSTDIAL")['priceInfo']['lastPrice'])
# pprint.pprint(nse_eq("JUSTDIAL")['priceInfo'])
# # print(nse_eq("JUSTDIAL")['priceInfo']['intraDayHighLow']['min'])
# # print(nse_eq("JUSTDIAL")['priceInfo']['intraDayHighLow']['max'])
# print(nse_eq("JUSTDIAL")['priceInfo']['close'])
pprint.pprint(nse_eq("JUSTDIAL")['priceInfo'])