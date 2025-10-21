import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs import generate, save, set_api_key, voices
from datetime import datetime
import os

# ---- CONFIG ----
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_NAME = "Sarah"  # Change to your ElevenLabs voice name
set_api_key(ELEVEN_API_KEY)


# ---- STT Function ----
def transcribe_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak into the microphone.")
        audio = recognizer.listen(source)

    try:
        st.info("Transcribing...")
        text = recognizer.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Google could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Request error from Google STT: {e}")
    return None


# ---- TTS Function ----
def generate_voice(text, voice=VOICE_NAME):
    st.info("Generating voice with ElevenLabs...")
    audio = generate(
        text=text,
        voice=voice,
        model="eleven_monolingual_v1"
    )
    filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    save(audio, filename)
    st.success("Voice generated and saved.")
    return filename


# ---- Streamlit App UI ----
st.title("🎤 Voice Agent with ElevenLabs + Google STT")

if st.button("Start Talking"):
    user_text = transcribe_speech()
    if user_text:
        # Placeholder logic: echo
        response_text = f"You said: {user_text}"

        audio_file = generate_voice(response_text)

        # Playback and download
        audio_bytes = open(audio_file, 'rb').read()
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            label="Download Response",
            data=audio_bytes,
            file_name=audio_file,
            mime="audio/mpeg"
        )
