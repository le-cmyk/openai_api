# to run the app : streamlit run 1_💬_Chat.py.py
# to have the correct version  : pipreqs --encoding=utf8 --force

from openai import OpenAI
import streamlit as st
import tiktoken

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/ 
st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
from test_connection import check_credentials, retrieve_sum_price, update_token_values, chat_model_options, update_df_token_month

st.title("Chat")


if "openai_client" not in st.session_state or st.session_state["openai_client"] is None:

    form = st.form("Connection")

    username = form.text_input("Enter Username", type="default", autocomplete="on", key="chat_username_token")

    password = form.text_input("Enter Password", type="password", autocomplete="on", key="chat_password_token")

    if form.form_submit_button ("Connection"):

        if check_credentials(username,password) == True: #password in st.secrets["password"]:
            st.session_state["openai_client"] = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            st.session_state["username"] = username

            st.session_state["session_price_before"] = retrieve_sum_price(username)
            st.session_state["month_price"] = retrieve_sum_price(username)
            st.session_state["session_price_current"] = 0

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



# Display choices
col1,col2,col3 = st.columns([0.2,0.2,0.1])

# Selection of the model
model_options = chat_model_options()
model_choice = model_options.get(col1.selectbox("Select an option", model_options.keys(), label_visibility="collapsed"))


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
                model=model_choice,
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

        update_token_values(st.session_state["username"], model_choice, num_token_prompt,num_token_response)
    
    else :
        with st.chat_message("assistant"):
            st.write("No client connection")



if st.session_state["openai_client"] is not None:

    st.session_state["month_price"] = retrieve_sum_price(st.session_state["username"])
    st.session_state["session_price_current"] = st.session_state["month_price"] - st.session_state["session_price_before"]

    st.sidebar.metric(
        label="Spend",
        value="{:.4} $/month".format(st.session_state["month_price"]),
        delta="{:.4} $/session".format(st.session_state["session_price_current"]),
        delta_color="inverse",
        help="""This metric represents your spending on token consumption. 
            The 'Spend' value is calculated based on your monthly consumption and is displayed in dollars per month. 
            The 'Delta' value shows the spending per session, indicating the change in spending compared to the previous session. 
            The spending data is stored and associated with your username."""
    )

    update_df_token_month()


