import streamlit as st
import speech_recognition as sr
from textbased import *

def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Please speak now...")
        audio_data = recognizer.listen(source)
        
        try:
            # Using Google's speech recognition
            text = recognizer.recognize_google(audio_data)
            st.write(f"Recognized Location: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio")
        except sr.RequestError as e:
            st.error(f"Speech recognition request failed; {e}")

def voice_based_mode():
    """Functionality for finding routes based on voice input"""
    # Instructions for voice input
    st.sidebar.write("Please provide voice input for Starting Location and Goal Location.")
    
    # Trigger voice input and update session state
    if st.sidebar.button("Start Speaking for Start Location", key="start_speak_button"):
        st.session_state['start_location_voice'] = voice_to_text()

    if st.sidebar.button("Start Speaking for Goal Location", key="goal_speak_button"):
        st.session_state['goal_location_voice'] = voice_to_text()

    profile = st.sidebar.radio("Transportation Mode", ("Driving", "Walking", "Cycling"), key="transport_mode").lower()

    if st.sidebar.button("Find Route", key="find_route_voice_button"):
        st.session_state['output_generated'] = True
        find_route_text_mode(st.session_state['start_location_voice'], st.session_state['goal_location_voice'], profile)