import os
from gtts import gTTS
import base64
import streamlit as st
from io import BytesIO

def create_custom_audio_player(b64: str):
    """Create a custom styled audio player with play/pause button"""
    custom_css = """
        <style>
        .audio-container {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: #1E1E1E;
            border-radius: 12px;
            margin: 15px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .audio-button {
            background: #FF4B4B;
            border: none;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .audio-button:hover {
            background: #FF6B6B;
            transform: scale(1.05);
        }
        .audio-progress {
            flex-grow: 1;
            height: 6px;
            background: #333333;
            border-radius: 3px;
            overflow: hidden;
            cursor: pointer;
        }
        .time-display {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #FFFFFF;
            min-width: 90px;
            text-align: right;
        }
        </style>
    """
    
    audio_player = f"""
        {custom_css}
        <div class="audio-container">
            <button class="audio-button" id="playButton" onclick="togglePlay()">
                <svg width="20" height="20" viewBox="0 0 24 24">
                    <path id="playIcon" fill="currentColor" d="M8 5v14l11-7z"/>
                    <path id="pauseIcon" fill="currentColor" d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" style="display: none;"/>
                </svg>
            </button>
            <div class="audio-progress">
                <div id="progress" style="width: 0%; height: 100%; background: #0066cc;"></div>
            </div>
            <div class="time-display" id="timeDisplay">0:00 / 0:00</div>
            <audio id="audioPlayer" style="display: none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        </div>
        <script>
            const audio = document.getElementById('audioPlayer');
            const playButton = document.getElementById('playButton');
            const playIcon = document.getElementById('playIcon');
            const pauseIcon = document.getElementById('pauseIcon');
            const progress = document.getElementById('progress');
            const timeDisplay = document.getElementById('timeDisplay');
            
            function togglePlay() {{
                if (audio.paused) {{
                    audio.play();
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'block';
                }} else {{
                    audio.pause();
                    playIcon.style.display = 'block';
                    pauseIcon.style.display = 'none';
                }}
            }}
            
            function formatTime(seconds) {{
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
            }}
            
            audio.addEventListener('timeupdate', () => {{
                const percent = (audio.currentTime / audio.duration) * 100;
                progress.style.width = percent + '%';
                timeDisplay.textContent = `${{formatTime(audio.currentTime)}} / ${{formatTime(audio.duration)}}`;
            }});
            
            audio.addEventListener('ended', () => {{
                playIcon.style.display = 'block';
                pauseIcon.style.display = 'none';
            }});
        </script>
    """
    return audio_player

def generate_audio(text, lang='en'):
    """Generate audio and return bytes"""
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes.getvalue()

def text_to_speech(text, lang='en'):
    """Display custom audio player with the provided text"""
    audio_bytes = generate_audio(text, lang)
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(create_custom_audio_player(b64), unsafe_allow_html=True)

# Add new function for direct Streamlit audio player
def text_to_speech_native(text, lang='en'):
    """Display native Streamlit audio player with the provided text"""
    audio_bytes = generate_audio(text, lang)
    st.audio(audio_bytes, format="audio/mpeg")
