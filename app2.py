import streamlit as st
import tempfile
import os
import sounddevice as sd
import numpy as np
import wave

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
    
    temp_audio_path = "recorded_audio.wav"
    with wave.open(temp_audio_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())
    st.session_state.audio_file = temp_audio_path

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
elif st.session_state.audio_file:
    audio_path = st.session_state.audio_file

if audio_path:
    st.audio(audio_path, format='audio/wav')
    tamil_text = "நீங்கள் எதை பற்றி கேட்கிறீர்கள்?"
    processed_text = "இது ஒரு சோதனை பதிலாகும்."
    audio_output = None  # No real audio output for now
    
    # Append to chat history
    st.session_state.chat_history.append((tamil_text, processed_text, audio_output))

st.subheader("💬 Chatbot Conversation")

for query, response, audio in st.session_state.chat_history:
    col1, col2 = st.columns([1, 1])
    with col2:
        st.write("**🗣️ User Query (Tamil):**")
        st.success(query)
    with col1:
        st.write("**🤖 Chatbot Response (Tamil):**")
        st.info(response)
        if audio:
            st.write("🔊 Tamil Speech Output:")
            st.audio(audio, format='audio/wav')
            st.download_button("Download Tamil Speech", audio, file_name="Tamil_Speech.wav")
