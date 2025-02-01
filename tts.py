import os
from gtts import gTTS
import pygame
import base64
import streamlit as st


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

def text_to_speech(text, lang='en'):
    """
    Convert text to speech using gTTS and play it using Streamlit's audio player
    Args:
        text (str): Text to convert to speech
        lang (str): Language code (default: 'en')
    """
    # Create temporary audio file
    filename = "temp_speech.mp3"
    
    # Generate speech
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    
    # Read the audio file and play it
    with open(filename, 'rb') as f:
        audio_bytes = f.read()
    autoplay_audio3(audio_bytes)
    
    # Cleanup
    os.remove(filename)

# # Create Streamlit UI
# def main():
#     st.title("Text to Speech App")
    
#     # Text input
#     user_text = st.text_input("Enter text to convert to speech:", "Hello, how are you?")
    
#     # Language selection
#     language = st.selectbox("Select language:", ["en", "fr", "es", "de"], index=0)
    
#     # Button to trigger conversion
#     if st.button("Convert to Speech"):
#         text_to_speech(user_text, language)

# if __name__ == "__main__":
#     main()

