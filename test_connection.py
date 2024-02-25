import streamlit as st
from streamlit_gsheets import GSheetsConnection
import hashlib

# Update Google Sheets with the new vendor data
#conn.update(worksheet="Example 1", data=data)


def check_credentials(username, password):

    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(worksheet="Example 1",usecols=range(3),  # specify columns which you want to get, comment this out to get all columns
            ttl = 20)
    data = data.dropna(how="all")

    def encrypt_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    return username in data['Username'].tolist() and encrypt_password(password) == data[data['Username']==username]['Password'].tolist()[0]


        
