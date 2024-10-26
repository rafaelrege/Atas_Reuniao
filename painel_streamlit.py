from moviepy.editor import AudioFileClip
import uuid
import streamlit as st
import assemblyai as aai
from openai import OpenAI
import fitz  # PyMuPDF para manipulação de PDFs
import pytesseract  # Para OCR de imagens
import pandas as pd  # Para manipulação de arquivos Excel
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
from PIL import Image  # Para manipulação de imagens extraídas
import io
import docx  # Para manipulação de arquivos .docx (Word)

# Configure os caminhos das APIs e do Tesseract
aai.settings.api_key = st.secrets['assemblyai']['api_key']
client = OpenAI(api_key=st.secrets['openai']['api_key'])

def mp4_to_mp3(mp4_filename, mp3_filename):
    arquivo_a_ser_convertido = AudioFileClip(mp4_filename)
    arquivo_a_ser_convertido.write_audiofile(mp3_filename)
    arquivo_a_ser_convertido.close()

def generate_response(prompt_system, prompt_text):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7
    )
    texto_retorno = response.choices[0].message.content.strip()
    return texto_retorno

def extract_text_from_pdf(pdf_filename):
    doc = fitz.open(pdf_filename)
    text = ""
    for page in doc:
        text += page.get_text()
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            text += pytesseract.image_to_string(image) + '\n'
    return text

def extract_text_from_docx(docx_filename):
    doc = docx.Document(docx_filename)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_excel(excel_filename):
    data = pd.read_excel(excel_filename)
    text = data.to_string(index=False)  # Converte o conteúdo do Excel para uma string legível
    return text

st.title('Automação de atas')
st.write('Criando uma ferramenta de automação de atas de reunião com tecnologia de IA com Python')

uploaded_file = st.file_uploader("Selecione o seu arquivo", accept_multiple_files=False, type=['mp4', 'pdf', 'docx', 'xlsx'])

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension == 'mp4':
        with st.spinner('Convertendo de mp4 para mp3'):
            mp4_filename = uploaded_file.name
            mp3_filename = f"{uuid.uuid4().hex}.mp3"

            tempfile = open(mp4_filename, 'wb')
            tempfile.write(uploaded_file.read())
            tempfile.close()

            mp4_to_mp3(mp4_filename, mp3_filename)
        st.success("Conversão de MP4 para MP3 realizada!")

        with st.spinner('Convertendo de mp3 para texto'):
            transcriber = aai.Transcriber()
            config = aai.TranscriptionConfig(speaker_labels=True, speakers_expected=2, language_code='pt')
            transcricao = transcriber.transcribe(mp3_filename, config=config)

            texto_transcrito = ""
            for sentenca in transcricao.utterances:
                texto_transcrito += f"Pessoa {sentenca.speaker}: {sentenca.text}\n"
            st.text_area('Transcrição', texto_transcrito)
        st.success("Transcrição realizada!")

    elif file_extension == 'pdf':
        with st.spinner('Extraindo texto do PDF e imagens (OCR)'):
            pdf_filename = uploaded_file.name
            tempfile = open(pdf_filename, 'wb')
            tempfile.write(uploaded_file.read())
            tempfile.close()

            texto_transcrito = extract_text_from_pdf(pdf_filename)
            st.text_area('Texto extraído', texto_transcrito)
        st.success("Texto extraído do PDF!")

    elif file_extension == 'docx':
        with st.spinner('Extraindo texto do arquivo Word'):
            docx_filename = uploaded_file.name
            tempfile = open(docx_filename, 'wb')
            tempfile.write(uploaded_file.read())
            tempfile.close()

            texto_transcrito = extract_text_from_docx(docx_filename)
            st.text_area('Texto extraído do Word', texto_transcrito)
        st.success("Texto extraído do arquivo Word!")

    elif file_extension == 'xlsx':
        with st.spinner('Extraindo texto do arquivo Excel'):
            excel_filename = uploaded_file.name
            tempfile = open(excel_filename, 'wb')
            tempfile.write(uploaded_file.read())
            tempfile.close()

            texto_transcrito = extract_text_from_excel(excel_filename)
            st.text_area('Texto extraído do Excel', texto_transcrito)
        st.success("Texto extraído do arquivo Excel!")

    with st.spinner('Gerando ata de reunião'):
        prompt_system = 'Você é um ótimo gerente de projetos com grandes capacidades de criação de atas de reunião'
        prompt_text = 'Em uma redação de nível especializado, resuma as notas da reunião em um único parágrafo. Em seguida, escreva uma lista de cada um de seus pontos-chaves tratados na reunião. Por fim, liste as próximas etapas ou itens de ação sugeridos pelos palestrantes, se houver.'
        prompt_text += '===========\n' + texto_transcrito

        texto_retorno = generate_response(prompt_system, prompt_text)
        st.markdown(texto_retorno)
