import streamlit as st
from streamlit_gsheets import GSheetsConnection
import hashlib
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

def token_month_year():
    now = datetime.datetime.now()
    month_year = now.strftime("Tokens_%B_%Y")
    return month_year

def recuperation_month_usage():

    worksheet_name = token_month_year()
    try :
        
        df_token_month = conn.read(worksheet=worksheet_name,usecols=range(data['Username'].count()+1), ttl = 1)
        
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
        df_token_month = conn.read(worksheet=worksheet_name,usecols=range(data['Username'].count()+1), ttl = 1)

    return df_token_month , worksheet_name

df_token_month , worksheet_name = recuperation_month_usage()


@st.cache_data
def chat_model_options():
    # Filter rows with 'Usage' equal to 'chat'
    filtered_df = df_models[df_models['Usage'] == 'chat']

    # Create model_options dictionary
    model_options = dict(zip(filtered_df['Alias'], filtered_df['Name']))
    
    return model_options


def check_credentials(username, password):

    def encrypt_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    return username in data['Username'].tolist() and encrypt_password(password) == data[data['Username']==username]['Password'].tolist()[0]


def update_token_values(username, model, num_token_prompt, num_token_response):
    """
    Updates the token values for a specific user and model.

    Parameters:
    - username: The username of the user.
    - model: The model name.
    - num_token_prompt: Number of prompt tokens to add.
    - num_token_response: Number of response tokens to add.
    """
    #df_token_month , worksheet_name = recuperation_month_usage()

    df_models.set_index("Model_id", inplace=True)
    model_id = df_models[df_models["Name"] == model].index[0]

    df_token_month.set_index("Model_id", inplace=True)
    tokens = tuple(map(int, df_token_month.loc[model_id, username].strip("()").split(",")))

    df_token_month.loc[model_id, username] = str((tokens[0] + num_token_prompt, tokens[1] + num_token_response))

    df_models.reset_index(inplace=True)
    df_token_month.reset_index(inplace=True)

    # conn.update(worksheet=worksheet_name, data=df_token_month)

def retrieve_sum_price(username):
    """
    Retrieves the sum price for a specific user based on token usage and model prices.

    Parameters:
    - username: The username of the user.

    Returns:
    - sum_price: The sum price calculated based on token usage and model prices.
    """

    # df_token_month , _ = recuperation_month_usage()

    df_models.set_index("Model_id", inplace=True)

    df_token_month.set_index("Model_id", inplace=True)

    sum_price = 0
    for model_id in df_models.index:
        price = tuple(map(float, df_models.loc[model_id, "Price"].strip("()").split(",")))
        tokens = tuple(map(int, df_token_month.loc[model_id, username].strip("()").split(",")))
        sum_price += price[0] / 1000 * tokens[0] + price[1] / 1000 * tokens[1]

    df_token_month.loc["Somme", username] = sum_price

    df_models.reset_index(inplace=True)
    df_token_month.reset_index(inplace=True)

    return sum_price


def update_df_token_month():


    conn.update(worksheet=worksheet_name, data=df_token_month)