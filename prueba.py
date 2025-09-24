import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from prompts import generate_prompt

load_dotenv(find_dotenv())

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

question = "Según la política ¿Qué se considera como efectivo y equivalentes de efectivo?"
# question = "Según la política ¿Qué incluyen los pasivos financieros medidos a costo amortizado?"

# Read PDF
pdf =""
file_path = "sura-EEFF-2024-4t-Mini.pdf"
with open(file_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        pdf += page.extract_text() + "\n"

message=[
    {"role": "system", "content": "Eres un asistente experto en análisis financiero y contable. Tu tarea es analizar estados financieros y políticas contables de empresas, identificar riesgos, inconsistencias y oportunidades de mejora, y responder preguntas específicas basadas en el contenido proporcionado."},
    {"role": "user", "content": generate_prompt(pdf, question)}
]
    
def get_answer():
    
    response = client.responses.create(
        #model="gpt-5",
        model="gpt-5-nano",
        #gpt-3.5-turbo-16k
        input=generate_prompt(pdf, question)
    )
    return response

print(get_answer())