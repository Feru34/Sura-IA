import os
import re
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
from openai import OpenAI
from prompts import generate_prompt, save_prompt_to_file

# --- Config ---
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
# Limita archivos a 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_pdf_text(file_path: str) -> tuple[str, str, str, int]:
    """
    Lee el PDF y extrae (texto, país, empresa, año) asumiendo nombres con formato:
    EMPRESA_PAIS_AÑO.pdf  (p.ej., SIM_MEX_2025.pdf)

    Returns:
        text (str): Texto concatenado del PDF.
        pais (str): Nombre de país normalizado (ej. "México", "Colombia").
        empresa (str): Token de empresa en mayúsculas (ej. "SIM").
        anio (int): Año de 4 dígitos (ej. 2025).
    """
    # --- Parseo del nombre ---
    stem = Path(file_path).stem  # "EMPRESA_PAIS_AÑO"
    parts = stem.split("_")
    if len(parts) != 3:
        raise ValueError(f"Formato inválido: se esperaba EMPRESA_PAIS_AÑO.pdf, recibido: {stem}")

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
        "DOM": "República Dominicana", "DO": "República Dominicana", "RD": "República Dominicana",
    }

    pais = pais_map.get(pais_token.upper(), pais_token.title())

    m = re.search(r"(\d{4})", anio_token)
    if not m:
        raise ValueError(f"Año inválido en el nombre de archivo: {anio_token}")
    anio = int(m.group(1))

    # --- Lectura del PDF ---
    text_parts = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")  # intento de desencriptar sin password
            except Exception:
                pass
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)

    text = "\n".join(text_parts).strip()
    return text, pais, empresa, anio


def extract_output_text(response) -> str:
    # Manejo robusto por variaciones del SDK
    try:
        return response.output_text
    except Exception:
        try:
            out0 = response.output[0]
            if hasattr(out0, "content"):
                content = out0.content
                if isinstance(content, (list, tuple)) and content:
                    first = content[0]
                    if isinstance(first, dict):
                        for k in ("text", "value", "content"):
                            if k in first:
                                return first[k]
                    else:
                        for k in ("text", "value", "content"):
                            if hasattr(first, k):
                                return getattr(first, k)
            return str(response)
        except Exception as e:
            return f"[No se pudo extraer texto de la respuesta]\n{e}"


@app.route("/", methods=["GET"])
def index():
    # Página principal
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
            return jsonify({"ok": False, "error": "OPENAI_API_KEY no está configurada en .env"}), 500

        filename = secure_filename(file.filename)
        file_path = UPLOAD_DIR / filename
        file.save(str(file_path))

        pdf_text = read_pdf_text(str(file_path))[0]
        pais = read_pdf_text(str(file_path))[1]
        empresa = read_pdf_text(str(file_path))[2]
        anio = read_pdf_text(str(file_path))[3]
        if not pdf_text:
            return jsonify({"ok": False, "error": "No se pudo extraer texto del PDF (¿es un escaneo sin OCR?)"}), 400

        prompt = generate_prompt(pdf_text, question, pais, empresa, anio)
        saved_path = save_prompt_to_file(prompt, "debug/prompt_dump.txt")
        print(f"Prompt guardado en: {saved_path} (longitud: {len(prompt)} caracteres)")
        
        response = client.responses.create(
            model="gpt-5-nano",
            # input="Dime un dato curioso.",
            input=prompt,
            # verbosity="low",
            # reasoning_effort="minimal",
            # temperature=0.0,
            # max_output_tokens=1200,
        )
        output_text = extract_output_text(response)

        return jsonify({"ok": True, "answer": output_text}), 200

    except Exception as e:

        app.logger.exception("Fallo en /analyze")
        return jsonify({"ok": False, "error": f"Error interno: {e}"}), 500
    

if __name__ == "__main__":
    # Ejecutar Flask en local
    app.run(host="127.0.0.1", port=5000, debug=True)
