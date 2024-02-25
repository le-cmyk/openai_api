import streamlit as st
from streamlit_gsheets import GSheetsConnection
import hashlib
import gspread
from gspread.exceptions import WorksheetNotFound
import datetime
import pandas as pd


# Update Google Sheets with the new vendor data
#conn.update(worksheet="Example 1", data=data)
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(worksheet="Example 1",usecols=range(3),  # specify columns which you want to get, comment this out to get all columns
        ttl = 20)
data = data.dropna(how="all")

df_models = conn.read(worksheet="Models",usecols=range(4),  # specify columns which you want to get, comment this out to get all columns
        ttl = 50)
df_models = df_models.dropna(how="all")


def check_credentials(username, password):

    def encrypt_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    return username in data['Username'].tolist() and encrypt_password(password) == data[data['Username']==username]['Password'].tolist()[0]


        




def token_month_year():
    now = datetime.datetime.now()
    month_year = now.strftime("Tokens_%B_%Y")
    return month_year

def recuperation_month_usage():

    worksheet_name = token_month_year()
    try :
        
        df_token_month = conn.read(worksheet=worksheet_name,usecols=range(data['Username'].count()+1), ttl = 40)
        
    except WorksheetNotFound:

        df_token_month = pd.DataFrame()

        df_token_month["Model_id"] = df_models["Model_id"]
        n = len(df_models["Model_id"])

        for user in data['Username'].tolist():
            df_token_month[user] = [0 for i in range(n)]

        st.dataframe(df_token_month)
        df_token_month = conn.create(
            worksheet=worksheet_name,
            data=df_token_month,
        )
    return df_token_month
