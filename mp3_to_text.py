import assemblyai as aai
import streamlit as st

aai.settings.api_key = st.secrets['assemblyai']['api_key']

transcriber = aai.Transcriber()

mp3_filename = r'da6b607c52fd4604a81eaa9b45c71abe.mp3'

config = aai.TranscriptionConfig( speaker_labels = True, speakers_expected = 2, language_code = 'pt' )

transcriber = aai.Transcriber()
transcricao = transcriber.transcribe(mp3_filename, config = config)


for sentenca in transcricao.utterances:
	print(f"Pessoa {sentenca.speaker}: {sentenca.text}")
# transcript = transcriber.transcribe(mp3_filename)
# transcript = transcriber.transcribe("./my-local-audio-file.wav")

# print(transcript.text)