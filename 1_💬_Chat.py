from openai import OpenAI
import streamlit as st

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/ 
st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

st.title("Chat")


if "openai_client" not in st.session_state or st.session_state["openai_client"] is None:
    password = st.text_input("Enter Password", type="password", autocomplete="on", key="password_token")

    if password in st.secrets["password"]:
        st.session_state["openai_client"] = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        st.success('Valid password', icon="✅")
    else :
        st.session_state["openai_client"] = None
        st.error('Not a valid password', icon="🚨")


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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
    
    else :
        with st.chat_message("assistant"):
            st.write("No client connection")
