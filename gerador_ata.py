from openai import OpenAI
import streamlit as st

client = OpenAI (api_key = st.secrets['openai']['api_key'])


def generate_response(prompt_text):

	response = client.chat.completions.create(
		model="gpt-3.5-turbo-0125",  # Specify the model to use
		messages=[
			{"role": "system", "content": "You are a helpful assistant."},
			{"role": "user", "content": prompt_text}
		],
		max_tokens=150,			# Limits how long the response can be
		temperature=0.7			# A value between 0-1 that controls randomness
	)  # Ensure this line ends with the closing parenthesis


	texto_retorno = response.choices[0].message.content.strip()

	return texto_retorno


if __name__ == "__main__":

	prompt_text = "Qual é a capital da França."

	resposta = generate_response(prompt_text)

	print(resposta)