import pyttsx3
import streamlit as st

def text_to_speech(text):
    engine = pyttsx3.init()
    # Set the speech rate (default is 200, higher number = faster speech)
    engine.setProperty('rate', 150)  
    engine.say(text)
    engine.runAndWait()

