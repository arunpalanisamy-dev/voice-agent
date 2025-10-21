import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs import generate, save, set_api_key, voices
from googletrans import Translator
from speech_recognition import Recognizer, Microphone
from datetime import datetime
import os

# ---- CONFIG ----
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_NAME = "Sarah"  # Change to your ElevenLabs voice name
set_api_key(ELEVEN_API_KEY)

# Mapping language code to voices
VOICE_LANGUAGE_MAP = {
    "en-US": "Sarah",     # Default voice for English
    "hi-IN": "Sarah",     # Sarah supports multilingual
    "ta-IN": "Sarah",     # Tamil via multilingual support
    "fr-FR": "Sarah"      # French too (via multilingual)
}


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

def transcribe_audio(lang_code="en-US"):
    recognizer = Recognizer()
    with Microphone() as source:
        st.info("🎙️ Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language=lang_code)
    except:
        return None

# Google Translate helper
def translate_response(text, target_lang="en"):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except:
        return text



# ---- TTS Function ----
def generate_voice(text, voice=VOICE_NAME):
    try:
        audio = generate(text=text, voice=voice, model="eleven_multilingual_v1")
        filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        save(audio, filename)
        return filename
    except Exception as e:
        st.error(f"Voice generation failed: {e}")
        return None

## --- Streamlit UI ---
st.title("🌍 Multilingual Voice Agent")

language = st.selectbox(
    "🗣️ Choose your language:",
    ["English (en-US)", "Hindi (hi-IN)", "Tamil (ta-IN)", "French (fr-FR)"]
)
lang_code = language.split("(")[-1].strip(")")
voice = VOICE_LANGUAGE_MAP.get(lang_code, "Sarah")

if st.button("🎤 Start Talking"):
    user_text = transcribe_audio(lang_code)
    if user_text:
        st.success(f"📝 Transcribed: {user_text}")

        # Optional: Translate response
        response = f"You said: {user_text}"
        translated_response = translate_response(response, target_lang=lang_code.split("-")[0])

        audio_file = generate_voice(translated_response, voice=voice)
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button("⬇️ Download Audio", data=audio_bytes, file_name=audio_file, mime="audio/mpeg")
        else:
            st.error("⚠️ Failed to generate or locate audio file.")
    else:
        st.warning("😕 Could not understand your speech. Try again.")