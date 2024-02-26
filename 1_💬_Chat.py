# to run the app : streamlit run 1_💬_Chat.py.py
# to have the correct version  : pipreqs --encoding=utf8 --force

from openai import OpenAI
import streamlit as st
import tiktoken

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/ 
st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
from test_connection import check_credentials, add_token

st.title("Chat")


if "openai_client" not in st.session_state or st.session_state["openai_client"] is None:

    form = st.form("Connection")

    username = form.text_input("Enter Username", type="default", autocomplete="on", key="chat_username_token")

    password = form.text_input("Enter Password", type="password", autocomplete="on", key="chat_password_token")

    if form.form_submit_button ("Connection"):

        if check_credentials(username,password) == True: #password in st.secrets["password"]:
            st.session_state["openai_client"] = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            st.session_state["username"] = username

            add_token(st.session_state["username"], "gpt-3.5-turbo-0125", 0,0)

            form.success('Valid password', icon="✅")
        else :
            st.session_state["openai_client"] = None
            st.session_state["username"] = "Guest"
            st.session_state["session_price_before"] = 0
            st.session_state["session_price_current"] = 0
            st.session_state["month_price"] = 0
            form.error('Not a valid password', icon="🚨")
    
    else :
        st.session_state["openai_client"] = None
        st.session_state["username"] = "Guest"
        st.session_state["session_price_before"] = 0
        st.session_state["session_price_current"] = 0
        st.session_state["month_price"] = 0


model_options = {
    "gpt-3.5": "gpt-3.5-turbo-0125",
    "gpt-4": "gpt-4-0125-preview",
}

col1,col2,col3 = st.columns([0.2,0.2,0.1])

# Selection of the model
model_choice = model_options.get(col1.selectbox("Select an option", model_options.keys(), label_visibility="collapsed"))

if "openai_chat_model" not in st.session_state or model_choice != st.session_state["openai_chat_model"]:
    st.session_state["openai_chat_model"] = model_choice

# Create a slider to choose a temperature
def map_temperature(temperature):
    if temperature == 'Precise':
        return 0.0
    elif temperature == 'Balance':
        return 0.75
    elif temperature == 'Creative':
        return 1.5

selected_temperature = col2.select_slider('Choose a temperature', options=['Precise', 'Balance', 'Creative'], label_visibility="collapsed")
mapped_temperature = map_temperature(selected_temperature)

if "openai_chat_temperature" not in st.session_state or mapped_temperature != st.session_state["openai_chat_temperature"]:
    st.session_state["openai_chat_temperature"] = mapped_temperature

# Reload button 
if col3.button('Reload') or "messages" not in st.session_state :
    st.session_state.messages = []

# Counting the number of token
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# Writing the existing part 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Prompt and the response
if prompt := st.chat_input("Enter the question"):
    if st.session_state["openai_client"] is not None:

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            
            stream = st.session_state["openai_client"].chat.completions.create(
                model=st.session_state["openai_chat_model"],
                temperature=st.session_state["openai_chat_temperature"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                 stream=True,
            )

            response = st.write_stream(stream) 

        st.write(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


        num_token_prompt = num_tokens_from_string(prompt, "cl100k_base")
        num_token_response = num_tokens_from_string(response, "cl100k_base")

        add_token(st.session_state["username"], st.session_state["openai_chat_model"], num_token_prompt,num_token_response)
        



        
    
    else :
        with st.chat_message("assistant"):
            st.write("No client connection")


# Formater et afficher les valeurs dans la barre latérale
st.sidebar.write("Month price: {:.4%}".format(st.session_state["month_price"]))
st.sidebar.write("Current session: {:.4f}".format(st.session_state["session_price_current"]))
