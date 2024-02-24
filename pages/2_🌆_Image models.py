import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO


# Function to generate images with specific parameters
def generate_images(prompt, model, size, quality, n, style=None):
    # Construct request parameters
    params = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "quality": quality,
        "n": n
    }
    if style is not None:
        params["style"] = style  # Add style parameter if specified
    
    # Make API call to generate images
    response = st.session_state["openai_client"].images.generate(**params)
    return response

# Function to display an image from a URL
def display_image(image_url):
    # Fetch image from URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # Convert image to byte array for Streamlit display
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

# Function to process API response and display images
def process_and_display_images(prompt, model, size, quality, n, style=None):
    # Generate images with provided parameters
    images_response = generate_images(prompt, model, size, quality, n, style)
    
    # Process each image in the response
    image_list = [display_image(image_data.url) for image_data in images_response.data]
    return image_list





if "openai_client" not in st.session_state or st.session_state["openai_client"] is None:
    c_1,c_2 = st.columns(2)
    c_1.error('No Connection', icon="🚨")

    if c_2.button("Connect"):
        st.switch_page("1_💬_Chat.py")
    
    st.session_state["openai_client"] = None

# Display input fields in two columns
col1, col2 = st.columns([0.2, 0.2])

# Input fields for selecting model, image size, quality, and number of images
model = col1.selectbox("Model:", ["dall-e-2", "dall-e-3"])
size_options = ["256x256", "512x512", "1024x1024"] if model == "dall-e-2" else ["1024x1024", "1792x1024", "1024x1792"]
size = col1.selectbox("Image size:", size_options)
quality_options = ["standard"] if model == "dall-e-2" else ["standard", "hd"]
quality = col2.selectbox("Image quality:", quality_options)
style = col2.selectbox("Image style:", ["vivid", "natural"]) if model == "dall-e-3" else None
n = col2.slider("Number of images to generate:", 1, 10, 1) if model == "dall-e-2" else 1
use_column_width = col2.toggle('Adjust screen picture', value=True)


# Initialize or reset the image messages in the session state if the 'Reload' button is clicked or if 'image_messages' does not already exist
if col1.button('Reload') or "image_messages" not in st.session_state:
    st.session_state.image_messages = []

# Iterate through the saved image messages in the session state to display them
for image_message in st.session_state.image_messages:
    # Use Streamlit's chat_message container to display each message based on its role ('user' or 'assistant')
    with st.chat_message(image_message["role"]):
        
        # Check if the message type is text to display it using markdown
        if image_message["type"] == "text":
            st.markdown(image_message["content"])
        # If the message contains images, iterate through the images and display each one
        else:
            for i, image in enumerate(image_message["content"]):
                st.image(image, caption=f"Generated Image {i+1}", use_column_width=use_column_width)

# Capture user input through a chat interface and save the input along with the user's role and content type
if prompt := st.chat_input("Enter the image description"):
        
    if st.session_state["openai_client"] is not None:    
        # Append the user's prompt as a text message to the session state
        st.session_state.image_messages.append({"role": "user", "content": prompt, "type": "text"})
        
        # Display the user's prompt in the chat interface
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process and display images based on the user's prompt
        with st.chat_message("assistant"):
            list_image = process_and_display_images(prompt, model, size, quality, n, style=style)
            for i, image in enumerate(list_image):
                st.image(image, caption=f"Generated Image {i+1}", use_column_width=use_column_width)

        # Append the generated images as a message to the session state to be displayed in the chat interface
        st.session_state.image_messages.append({"role": "assistant", "content": list_image, "type": "image"})
    else :
        with st.chat_message("assistant"): 

            st.write("No client connection")


            
            


