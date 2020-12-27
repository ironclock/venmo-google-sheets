import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages")
import venmo_api
import pprint
from venmo_api import Client
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import time

# venmo access token (do not share with anyone)
access_token = "sensitive - hidden"

# log us in
venmo = Client(access_token=access_token)

# this is our user id
userid = "sensitive - hidden"

# pull transaction data from our user id
transactions = venmo.user.get_user_transactions(user_id=userid)


# create dataframe for transactions data
df = pd.DataFrame(columns = ['date', 'amount', 'audience', 'payment type','comment'])

for t in transactions:
    t_date = str(datetime.utcfromtimestamp(t.date_created).strftime('%Y-%m-%d %H:%M:%S'))
    t_amount = t.amount
    t_audience = t.audience
    t_comment = t.note
    t_payment_type = t.payment_type
    new_row = {'date':t_date,
               'amount':t_amount,
               'audience':t_audience,
               'payment type':t_payment_type,
               'comment':t_comment}
    df = df.append(new_row, ignore_index=True)



# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# name of the google sheets workbook
sheet = client.open("venmo").sheet1

# deleting rows to be updated
for ind in df.index:
    sheet.delete_rows(8)
    print("Deleted row. Waiting 2 seconds...")
    time.sleep(2)

# inserting new rows
for ind in df.index:
    row = [df['date'][ind],
           df['amount'][ind],
           df['audience'][ind],
           df['payment type'][ind],
           df['comment'][ind]]
    index = ind + 8
    sheet.insert_row(row,index)
    print("Inserting row. Waiting 2 seconds...")
    time.sleep(2)

# access token
token = "sensitive - hidden"

def get_my_balance():
    header = {
        "Authorization": token,
        "User-Agent": "Venmo/8.6.1 (iPhone; iOS 13.0; Scale/3.0)"
    }
    url = "https://api.venmo.com/v1/account"
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        print("Something went wrong, check the logs")
        print(response.status_code, response.reason, response.text)
        return 0

    json = response.json()
    return float(json.get('data').get('balance'))

balance = str(get_my_balance())

balance = "balance : $" + balance

sheet.update_cell(4,1,balance)
print("Updated balance")

ts = str(datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

ts = "last updated : " + ts

sheet.update_cell(5,1,ts)
print("Updated time")


                  

                             
