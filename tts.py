import os
from gtts import gTTS
import pygame

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

text_to_speech("Hello, how are you?")

