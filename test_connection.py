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

df_models = conn.read(worksheet="Models", usecols=range(5), ttl = 20)

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
        
        df_token_month = conn.read(worksheet=worksheet_name,usecols=range(data['Username'].count()+1), ttl = 4)
        
    except WorksheetNotFound:

        df_token_month = pd.DataFrame()

        df_token_month["Model_id"] = df_models["Model_id"].tolist() + ["Somme"]
        n = len(df_models["Model_id"])

        for user in data['Username'].tolist():
            df_token_month[user] = [(0,0) for i in range(n)] + [0] # + somme of the depense

        df_token_month = conn.create(
            worksheet=worksheet_name,
            data=df_token_month,
        )
        df_token_month = conn.read(worksheet=worksheet_name,usecols=range(data['Username'].count()+1), ttl = 4)

    return df_token_month , worksheet_name


def add_token(username, model, num_token_prompt,num_token_response):

    df_models.set_index("Model_id", inplace=True)

    model_id = df_models[df_models["Name"] == model].index[0]
    
    df_token_month , worksheet_name = recuperation_month_usage()

    df_token_month.set_index("Model_id", inplace=True)
    tokens = tuple(map(int, df_token_month.copy().loc[model_id, username].strip("()").split(",")))

    df_token_month.loc[model_id, username] = str((tokens[0] + num_token_prompt ,tokens[1] + num_token_response))

    somme = 0
    for id_model in df_models.index.tolist() : 

        price = tuple(map(float, df_models.loc[id_model, "Price"].strip("()").split(",")))
        tokens = tuple(map(int, df_token_month.copy().loc[model_id, username].strip("()").split(",")))

        somme += price[0] /1000 * tokens[0] + price[1] /1000 * tokens[1]

    df_token_month.loc["Somme", username] = somme

    # Calcul du prix mensuel
    st.session_state["month_price"] = somme

    # Vérification de l'existence de session_price_before
    if "session_price_before" not in st.session_state:
        st.session_state["session_price_before"] = somme

    # Calcul du prix de la session actuelle
    st.session_state["session_price_current"] = somme - st.session_state["session_price_before"]

    df_models.reset_index(inplace=True)
    df_token_month.reset_index(inplace=True)

    conn.update(worksheet=worksheet_name, data=df_token_month)

