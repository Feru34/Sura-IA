import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
from openai import OpenAI
from prompts import generate_prompt

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


def read_pdf_text(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


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

        # sanity checks útiles
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({"ok": False, "error": "OPENAI_API_KEY no está configurada en .env"}), 500

        filename = secure_filename(file.filename)
        file_path = UPLOAD_DIR / filename
        file.save(str(file_path))

        # Leer PDF
        pdf_text = read_pdf_text(str(file_path))
        if not pdf_text:
            return jsonify({"ok": False, "error": "No se pudo extraer texto del PDF (¿es un escaneo sin OCR?)"}), 400

        # Generar prompt y consultar modelo
        prompt = generate_prompt(pdf_text, question)
        response = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            # verbosity="low",
            # reasoning_effort="minimal",
            # temperature=0.0,
            # max_output_tokens=1200,
        )
        output_text = extract_output_text(response)

        return jsonify({"ok": True, "answer": output_text}), 200

    except Exception as e:
        # Log a consola para que veas el error real en el terminal
        app.logger.exception("Fallo en /analyze")
        return jsonify({"ok": False, "error": f"Error interno: {e}"}), 500
    

if __name__ == "__main__":
    # Ejecutar Flask en local
    app.run(host="127.0.0.1", port=5000, debug=True)
