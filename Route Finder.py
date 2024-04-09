import streamlit as st

# Import your mode functions
from textbased import *
from imagebased import *
from voicebased import *
from generativeimage import *
from utilities import *

def main():
    st.set_page_config(page_title="Multi-Modal Route Finder")

    if 'show_landing' not in st.session_state:
        st.session_state['show_landing'] = True
    if 'mode_selected' not in st.session_state:
        st.session_state['mode_selected'] = None

    # Display landing page or the selected mode
    if st.session_state['show_landing']:
        display_landing_page()
    else:
        mode_selection(st.session_state['mode_selected'])

    # "Back to Home" button at the bottom of the sidebar
    with st.sidebar:
        # Using an empty block with a large height to push the button down
        # Adjust the number of empty lines based on your app's needs
        st.empty()
        for _ in range(2):  # This number may need to be adjusted
            st.write("")  # Adding vertical space
        if not st.session_state['show_landing']:
            if st.button("Back to Home"):
                st.session_state['show_landing'] = True
                st.session_state['mode_selected'] = None

def display_landing_page():
    st.title("Welcome to the Multi-Modal Route Finder")
    st.write("This project offers various modes of interaction for route planning. Please select a mode to get started.")

    if st.button('Text-based Mode'):
        st.session_state['show_landing'] = False
        st.session_state['mode_selected'] = 'Text-based'
    if st.button('Image-based Mode'):
        st.session_state['show_landing'] = False
        st.session_state['mode_selected'] = 'Image-based'    
    if st.button('Voice-based Mode'):
        st.session_state['show_landing'] = False
        st.session_state['mode_selected'] = 'Voice-based'
    if st.button('Generative Image Mode'):
        st.session_state['show_landing'] = False
        st.session_state['mode_selected'] = 'Generative Image'

def mode_selection(mode):
    if mode == 'Text-based':
        st.header("Text-based Mode")
        st.write("Interact using simple text commands to define your starting point and destination. This mode is ideal for quick and efficient route planning through textual input.")
        text_based_mode()
    elif mode == 'Image-based':
        st.header("Image-based Mode")
        st.write("Upload images or maps of your area of interest to receive route suggestions. Utilize visual cues to navigate and explore possible routes in a more intuitive manner.")
        image_based_mode()
    elif mode == 'Voice-based':
        st.header("Voice-based Mode")
        st.write("Speak your route preferences and commands to initiate route planning. This hands-free mode offers an accessible and convenient way to plan your travel without the need for typing.")
        voice_based_mode()
    elif mode == 'Generative Image':
        st.header("Generative Image Mode")
        st.write("Leverage the power of generative AI to visualize routes. Customize your journey by interacting with generated images, allowing for a dynamic and engaging route planning experience.")
        generative_image_editing()
    

if __name__ == "__main__":
    main()
