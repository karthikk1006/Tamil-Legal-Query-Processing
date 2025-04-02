import streamlit as st
import requests
import tempfile
import os
import sounddevice as sd
import numpy as np
import wave
import base64

BACKEND_URL = "http://10.5.14.138:8000"  # Replace <backend-ip> with actual backend IP

st.set_page_config(page_title="Tamil Legal Query Chatbot", layout="wide")
st.title("🤖 Tamil Legal Query Chatbot")

st.markdown("Have a continuous conversation with the chatbot by speaking or uploading audio files.")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

def record_audio(duration=5, samplerate=44100):
    st.session_state.recording = True
    st.info("Recording... Speak now!")
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    st.session_state.recording = False
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        with wave.open(temp_audio.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())
        st.session_state.audio_file = temp_audio.name

# Centered UI
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a", "ogg"])
    st.write("OR")
    duration = st.slider("Select recording duration (seconds)", 1, 10, 5)
    record_button = st.button("🎤 Start Recording")
    if record_button:
        record_audio(duration)

audio_path = None
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(uploaded_file.read())
        audio_path = temp_audio.name
    st.session_state.audio_file = None  # Clear recorded file if a new one is uploaded
elif st.session_state.audio_file:
    audio_path = st.session_state.audio_file

if audio_path:
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
        with st.spinner("Processing... Please wait."):
            try:
                response = requests.post(f"{BACKEND_URL}/process", files=files)
                if response.status_code == 200:
                    data = response.json()
                    user_query_audio = audio_path
                    processed_text = data.get("text", "Error processing the audio file.")
                    audio_base64 = data.get("audio_file", "")
                    st.session_state.chat_history.append((user_query_audio, processed_text, audio_base64))
                    st.session_state.audio_file = None  # Reset audio file after processing
                else:
                    st.error(f"Error: Received unexpected status code {response.status_code}")
            except requests.exceptions.RequestException:
                st.error("Error processing the audio file.")

st.subheader("💬 Chatbot Conversation")

for query_audio, response, audio_base64 in st.session_state.chat_history:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.write("**🗣️ User Query:**")
        st.audio(query_audio, format='audio/wav')
    with col2:
        st.write("**🤖 Chatbot Response:**")
        st.info(response)
    with col3:
        if audio_base64:
            audio_bytes = base64.b64decode(audio_base64)
            st.write("🔊 Tamil Speech Output:")
            st.audio(audio_bytes, format='audio/wav')
