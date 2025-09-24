import os
import re
import json
import pickle
from pathlib import Path
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
from openai import OpenAI
import tiktoken
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from prompts import generate_prompt, save_prompt_to_file

# --- Config ---
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
EMBEDDINGS_DIR.mkdir(exist_ok=True)
SURA_PDF_PATH = BASE_DIR / "sura-EEFF-2024-4t.pdf"

ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def chunk_tokens(document: str, token_limit: int = 500) -> List[str]:
    """
    Divide el documento en chunks basados en tokens.
    Aumenté el límite a 500 tokens para chunks más contextuales.
    """
    enc = tiktoken.encoding_for_model('gpt-3.5-turbo')
    chunks = []
    tokens = enc.encode(document, disallowed_special=())
    
    while tokens:
        chunk = tokens[:token_limit]
        chunk_text = enc.decode(chunk)
        
        # Buscar el último punto de ruptura natural
        last_punctuation = max(
            chunk_text.rfind("."),
            chunk_text.rfind("?"),
            chunk_text.rfind("!"),
            chunk_text.rfind("\n"),
        )
        
        if last_punctuation != -1 and len(tokens) > token_limit:
            chunk_text = chunk_text[:last_punctuation + 1]
        
        cleaned_text = chunk_text.replace("\n", " ").strip()
        
        if cleaned_text and (not cleaned_text.isspace()):
            chunks.append(cleaned_text)
        
        tokens = tokens[len(enc.encode(chunk_text, disallowed_special=())):]
    
    return chunks


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Genera embeddings usando OpenAI API en lugar de modelos locales para mejor rendimiento.
    """
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding


def read_pdf_text(file_path: str) -> Tuple[str, str, str, int]:
    """
    Lee el PDF y extrae (texto, país, empresa, año).
    Para el archivo de Sura, usa valores por defecto.
    """
    stem = Path(file_path).stem
    
    # Caso especial para Sura
    if "SegurasSuraSA" in stem:
        empresa = "SURA"
        pais = "República Dominicana"
        anio = 2024
    else:
        # Parseo normal
        parts = stem.split("_")
        if len(parts) != 3:
            # Si no sigue el formato, usar valores por defecto
            empresa = stem.upper()[:10]  # Primeros 10 caracteres
            pais = "No especificado"
            anio = 2024
        else:
            empresa_token, pais_token, anio_token = (p.strip() for p in parts)
            empresa = empresa_token.upper()
            
            pais_map = {
                "MEX": "México", "MX": "México",
                "COL": "Colombia", "CO": "Colombia",
                "ESP": "España", "ES": "España",
                "USA": "Estados Unidos", "US": "Estados Unidos",
                "CHL": "Chile", "CL": "Chile",
                "ARG": "Argentina",
                "PER": "Perú", "PE": "Perú",
                "DOM": "República Dominicana", "DO": "República Dominicana", 
                "RD": "República Dominicana",
            }
            
            pais = pais_map.get(pais_token.upper(), pais_token.title())
            
            m = re.search(r"(\d{4})", anio_token)
            if m:
                anio = int(m.group(1))
            else:
                anio = 2024

    # Lectura del PDF
    text_parts = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")
            except Exception:
                pass
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    
    text = "\n".join(text_parts).strip()
    return text, pais, empresa, anio


class KnowledgeBase:
    """
    Clase para manejar la base de conocimiento con embeddings.
    """
    def __init__(self, name: str):
        self.name = name
        self.chunks = []
        self.embeddings = []
        self.metadata = {}
        self.embeddings_path = EMBEDDINGS_DIR / f"{name}_embeddings.pkl"
    
    def build_from_pdf(self, pdf_path: str, force_rebuild: bool = False):
        """
        Construye o carga la base de conocimiento desde un PDF.
        """
        if not force_rebuild and self.embeddings_path.exists():
            print(f"Cargando embeddings existentes para {self.name}...")
            self.load()
            return
        
        print(f"Construyendo base de conocimiento para {self.name}...")
        text, pais, empresa, anio = read_pdf_text(pdf_path)
        
        if not text:
            raise ValueError(f"No se pudo extraer texto del PDF: {pdf_path}")
        
        self.metadata = {
            "pais": pais,
            "empresa": empresa,
            "anio": anio,
            "pdf_path": str(pdf_path)
        }
        
        # Generar chunks
        self.chunks = chunk_tokens(text, token_limit=500)
        print(f"Generados {len(self.chunks)} chunks")
        
        # Generar embeddings para cada chunk
        print("Generando embeddings...")
        self.embeddings = []
        for i, chunk in enumerate(self.chunks):
            if i % 10 == 0:
                print(f"  Procesando chunk {i}/{len(self.chunks)}")
            embedding = get_embedding(chunk)
            self.embeddings.append(embedding)
        
        # Guardar para uso futuro
        self.save()
        print(f"Base de conocimiento guardada para {self.name}")
    
    def save(self):
        """Guarda la base de conocimiento en disco."""
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings,
            "metadata": self.metadata
        }
        with open(self.embeddings_path, "wb") as f:
            pickle.dump(data, f)
    
    def load(self):
        """Carga la base de conocimiento desde disco."""
        with open(self.embeddings_path, "rb") as f:
            data = pickle.load(f)
        self.chunks = data["chunks"]
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Busca los chunks más similares a la consulta.
        """
        query_embedding = get_embedding(query)
        
        # Calcular similitudes
        similarities = []
        for embedding in self.embeddings:
            sim = cosine_similarity(
                np.array(query_embedding).reshape(1, -1),
                np.array(embedding).reshape(1, -1)
            )[0][0]
            similarities.append(sim)
        
        # Obtener los top_k chunks más similares
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], similarities[idx]))
        
        return results


# Inicializar base de conocimiento de Sura al arrancar la aplicación
sura_kb = KnowledgeBase("sura")

@app.before_request
def initialize_sura_knowledge():
    """Inicializa la base de conocimiento de Sura al arrancar."""
    if SURA_PDF_PATH.exists():
        try:
            sura_kb.build_from_pdf(str(SURA_PDF_PATH), force_rebuild=False)
            print(f"Base de conocimiento de Sura inicializada con {len(sura_kb.chunks)} chunks")
        except Exception as e:
            print(f"Error al inicializar base de conocimiento de Sura: {e}")
    else:
        print(f"ADVERTENCIA: No se encontró el archivo {SURA_PDF_PATH}")


def generate_comparison_prompt(sura_context: List[str], other_context: List[str], 
                               question: str, other_metadata: Dict) -> str:
    """
    Genera un prompt optimizado para comparar políticas contables.
    """
    sura_text = "\n\n".join([f"[Fragmento {i+1}]: {chunk}" for i, chunk in enumerate(sura_context)])
    other_text = "\n\n".join([f"[Fragmento {i+1}]: {chunk}" for i, chunk in enumerate(other_context)])
    
    prompt = f"""Eres un experto analista financiero especializado en comparación de políticas contables.

    TAREA: Comparar las políticas contables entre SURA 2024 y {other_metadata['empresa']} ({other_metadata['pais']}, {other_metadata['anio']}) específicamente sobre: {question}

    DOCUMENTOS DE REFERENCIA:

    === POLÍTICAS DE SURA ===
    {sura_text}

    === POLÍTICAS DE {other_metadata['empresa'].upper()} ===
    {other_text}

    INSTRUCCIONES:
    1. Identifica las políticas contables relevantes a la pregunta en ambas empresas
    2. Compara las diferencias principales entre ambas políticas
    3. Señala similitudes importantes si las hay
    4. Proporciona citas específicas de los documentos cuando sea posible
    5. Si alguna información no está disponible en los fragmentos proporcionados, indícalo claramente

    FORMATO DE RESPUESTA:
    - Comienza con un resumen ejecutivo de las diferencias principales
    - Detalla las políticas de cada empresa
    - Presenta una tabla comparativa si es apropiado
    - Concluye con las implicaciones de estas diferencias

    Responde de manera clara, profesional y citando los documentos cuando sea relevante."""
        
    return prompt


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "pdf" not in request.files:
            return jsonify({"ok": False, "error": "No se envió archivo PDF"}), 400
        
        file = request.files["pdf"]
        question = (request.form.get("question") or "").strip()
        
        if not file or file.filename == "":
            return jsonify({"ok": False, "error": "Archivo PDF inválido"}), 400
        if not allowed_file(file.filename):
            return jsonify({"ok": False, "error": "Formato no permitido (solo .pdf)"}), 400
        if not question:
            return jsonify({"ok": False, "error": "La pregunta no puede estar vacía"}), 400
        
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({"ok": False, "error": "OPENAI_API_KEY no está configurada"}), 500
        
        # Verificar que la base de conocimiento de Sura esté inicializada
        if not sura_kb.chunks:
            return jsonify({"ok": False, "error": "Base de conocimiento de Sura no inicializada"}), 500
        
        # Guardar y procesar el PDF subido
        filename = secure_filename(file.filename)
        file_path = UPLOAD_DIR / filename
        file.save(str(file_path))
        
        # Crear base de conocimiento temporal para el PDF subido
        other_kb = KnowledgeBase(f"temp_{filename}")
        other_kb.build_from_pdf(str(file_path), force_rebuild=True)
        
        # Buscar chunks relevantes en ambas bases de conocimiento
        sura_results = sura_kb.search_similar(question, top_k=3)
        other_results = other_kb.search_similar(question, top_k=3)
        
        # Extraer solo los textos de los chunks más relevantes
        sura_context = [chunk for chunk, _ in sura_results]
        other_context = [chunk for chunk, _ in other_results]
        
        # Generar prompt de comparación
        prompt = generate_comparison_prompt(
            sura_context, 
            other_context, 
            question,
            other_kb.metadata
        )
        
        saved_path = save_prompt_to_file(prompt, "debug/prompt_dump.txt")
        print(f"Prompt guardado en: {saved_path} (longitud: {len(prompt)} caracteres)")
        
        
        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Cambiado a un modelo más estable
            messages=[
                {"role": "system", "content": "Eres un experto analista financiero."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        output_text = response.choices[0].message.content
        
        # Limpiar archivos temporales
        try:
            os.remove(file_path)
            if other_kb.embeddings_path.exists():
                os.remove(other_kb.embeddings_path)
        except:
            pass
        
        return jsonify({"ok": True, "answer": output_text}), 200
    
    except Exception as e:
        app.logger.exception("Error en /analyze")
        return jsonify({"ok": False, "error": f"Error interno: {str(e)}"}), 500


@app.route("/rebuild-sura", methods=["POST"])
def rebuild_sura():
    """Endpoint para reconstruir la base de conocimiento de Sura."""
    try:
        if not SURA_PDF_PATH.exists():
            return jsonify({"ok": False, "error": "Archivo de Sura no encontrado"}), 404
        
        sura_kb.build_from_pdf(str(SURA_PDF_PATH), force_rebuild=True)
        return jsonify({"ok": True, "message": f"Base reconstruida con {len(sura_kb.chunks)} chunks"}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)