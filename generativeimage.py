import streamlit as st
import requests
import base64

def generative_image_editing():
    
    url = "http://127.0.0.1:7860"
    endpoint = "txt2img"

    # Inputs in the sidebar
    user_prompt = st.sidebar.text_input("Enter a prompt:")
    nsteps = st.sidebar.slider("Steps", min_value=1, max_value=150, value=20)

    referenceImage = st.sidebar.checkbox("Generate using reference image?")

    payload = {
        "prompt": user_prompt,
        "steps": nsteps,
    }

    if referenceImage:
        endpoint = "img2img"
        referenceImageFile = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if referenceImageFile:
            st.sidebar.image(referenceImageFile)
            image_bytes = referenceImageFile.getvalue()
            encodedImage = base64.b64encode(image_bytes).decode()
            payload["init_images"] = [encodedImage]
            denoise = st.sidebar.slider("Denoise Strength", min_value=0.0, max_value=1.0, value=0.75)
            payload["denoising_strength"] = denoise
    else:
        if "init_images" in payload:
            del payload["init_images"]

    generateButton = st.sidebar.button("Generate Image")

    if generateButton:
        if user_prompt:
            response = requests.post(url=f'{url}/sdapi/v1/{endpoint}', json=payload)
            if response.status_code == 200:
                r = response.json()
                st.session_state.generatedImage = "data:image/png;base64," + r['images'][0]
            else:
                st.error(f"Failed to generate image. Server responded with status code: {response.status_code}")

    if st.session_state.get("generatedImage", False):
        st.image(st.session_state.generatedImage)
