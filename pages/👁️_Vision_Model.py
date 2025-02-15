import streamlit as st
from PIL import Image
import requests
import base64
import uuid

FASTAPI_PROCESS_IMAGE_URL = "https://mini-cdss-fastapi.onrender.com/process-image/"
FASTAPI_PROCESS_IMAGE_ANSWER_URL = "https://mini-cdss-fastapi.onrender.com/process-image-answer/"


st.title("Try our 👁️ Vision Model!")

if "uploaded_image_file" not in st.session_state:
    st.session_state.uploaded_image_file = ""
if "user_query" not in st.session_state:
    st.session_state.user_query = ""


def process_inputs():
    uploaded_image_file = st.session_state.uploaded_image_file
    query = st.session_state.user_query

    if not uploaded_image_file:
        st.error("Please upload an image.")
        return
    if not query:
        st.error("Please enter a query.")
        return

    # Convert image to Base64
    image_bytes = uploaded_image_file.getvalue()
    base64_encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    if "thread_id" in st.session_state:
        thread_id = st.session_state.thread_id
    else:
        thread_id = str(uuid.uuid4())

    # Prepare form data
    data = {"query": query, "thread_id": thread_id}
    files = {"image": (uploaded_image_file.name, image_bytes, uploaded_image_file.type)}

    # Send the image & query to FastAPI
    with st.spinner("Processing image..."):
        response = requests.post(FASTAPI_PROCESS_IMAGE_URL, data=data, files=files)

    if response.status_code == 200:
        st.success("Graph triggered! Fetching the answer...")

        # Fetch the result from FastAPI
        with st.spinner("Retrieving answer..."):
            answer_response = requests.post(FASTAPI_PROCESS_IMAGE_ANSWER_URL, data={"thread_id": thread_id})

        if answer_response.status_code == 200:
            answer = answer_response.text.strip()
            st.session_state.image_processing_answer = answer
            st.markdown(f"{answer}")
        else:
            st.error(f"Error fetching answer: {answer_response.text}")

    else:
        st.error(f"Error triggering process: {response.text}")




# Upload file
uploaded_image_file = st.file_uploader("Choose a medical image...", type=["png", "jpg", "jpeg"])

# Display image if uploaded
if uploaded_image_file is not None:
    st.session_state.uploaded_image_file = uploaded_image_file
    image = Image.open(uploaded_image_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)


user_query=st.text_input("Enter your medical query here...")

if st.button(label="Submit Query", type="primary"):
    st.session_state.user_query = user_query
    process_inputs()
    
