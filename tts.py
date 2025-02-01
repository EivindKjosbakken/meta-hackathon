import os
from gtts import gTTS
import pygame
import base64
import streamlit as st

def text_to_speech(text, lang='en'):
    """
    Convert text to speech using gTTS and play it using pygame
    Args:
        text (str): Text to convert to speech
        lang (str): Language code (default: 'en')
    """
    # Create temporary audio file
    filename = "temp_speech.mp3"
    
    # Generate speech
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    
    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Cleanup
    pygame.mixer.quit()
    os.remove(filename)

def autoplay_audio3(file, autoplay=True):
    """
    Play audio file with optional autoplay using Streamlit
    Args:
        file (bytes): Audio file in bytes format
        autoplay (bool): Whether to autoplay the audio (default: True)
    """
    b64 = base64.b64encode(file).decode()
    if autoplay:
        md = f"""
            <audio id="audioTag" controls autoplay>
            <source src="data:audio/mp3;base64,{b64}"  type="audio/mpeg" format="audio/mpeg">
            </audio>
            """
    else:
        md = f"""
            <audio id="audioTag" controls>
            <source src="data:audio/mp3;base64,{b64}"  type="audio/mpeg" format="audio/mpeg">
            </audio>
            """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )

text_to_speech("Hello, how are you?")

