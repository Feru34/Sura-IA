# AI PDF Analyst (Flask + OpenAI)

Aplicación web en **Flask** que permite **subir un PDF**, hacer una **pregunta** y obtener una **respuesta** generada por IA (modelo `gpt-5-nano` de OpenAI) usando tu `prompts.py`.

Diseño limpio inspirado en **Google Design** y con acento de **Azure**.

---

## ✨ Características

* Carga de **PDF** (hasta 20 MB).
* Formulario para **preguntas abiertas**.
* Llamada a OpenAI (`gpt-5-nano`), respuesta en JSON.
* UI cuidada: `templates/index.html` + `static/styles.css`.
* Manejo de errores consistente en **/analyze** (devuelve JSON incluso en fallos).

---

## 🧱 Requisitos

* **Python 3.10+** (recomendado 3.10/3.11)
* Cuenta y **API Key** de OpenAI (`OPENAI_API_KEY`)
* Pip/venv

> Si el PDF es un **escaneo** (imagen), PyPDF2 no extraerá texto. En ese caso, ejecuta OCR previamente (por ejemplo, con `ocrmypdf`).

---

## 📁 Estructura del proyecto

```
ai-pdf-analyst/
├─ app.py
├─ prompts.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ uploads/             # se crea/usa en runtime
├─ templates/
│  └─ index.html
└─ static/
   ├─ styles.css
   └─ azure-logo.svg
```

---

## ⚙️ Instalación y ejecución en local

> Los comandos muestran ambas variantes: **bash** (macOS/Linux) y **PowerShell** (Windows).

### 1) Clonar y entrar

```bash
git clone <URL-del-repo>.git ai-pdf-analyst
cd ai-pdf-analyst
```

### 2) Crear y activar entorno virtual

**macOS/Linux (bash):**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

### 3) Instalar dependencias

```bash
pip install -r requirements.txt
```

> Si ya tenías instalado `openai`, asegúrate de estar en una versión reciente:
>
> ```bash
> pip install --upgrade openai
> ```

### 4) Configurar variables de entorno

Copia el ejemplo y edítalo con tu clave:

```bash
cp .env.example .env
```

Edita `.env` y reemplaza:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **No** subas `.env` al repositorio.

### 5) Ejecutar la app

**Opción A (python):**

```bash
python app.py
```

**Opción B (Flask CLI):**

```bash
flask --app app run --debug
```

Abre en el navegador: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Probar el endpoint /analyze (opcional)

Puedes llamar al endpoint con `curl` (requiere un PDF y una pregunta):

```bash
curl -X POST http://127.0.0.1:5000/analyze \
  -F "pdf=@sura-EEFF-2024-4t-Mini.pdf" \
  -F "question=Según la política ¿Qué se considera como efectivo y equivalentes de efectivo?"
```

Respuesta esperada (JSON):

```json
{
  "ok": true,
  "answer": "..."
}
```

---

## 🔧 Configuración útil

* **Tamaño máximo de archivo:** en `app.config["MAX_CONTENT_LENGTH"]` (por defecto 20 MB).
* **Formatos permitidos:** solo `.pdf` (ver `ALLOWED_EXTENSIONS` en `app.py`).
* **Modelo OpenAI:** `gpt-5-nano` (cámbialo en `app.py` si necesitas otro).
* **Carpeta de cargas:** `uploads/` (no se versiona).
* **Rutas estáticas/plantillas:** definidas explícitamente con `Path` para evitar problemas de rutas en Windows.

---

## 🔌 Endpoints

* `GET /`
  Devuelve la página principal (`templates/index.html`).

* `POST /analyze`
  Form-data:

  * `pdf` (archivo `.pdf`)
  * `question` (texto)

  Respuesta JSON:

  * `{"ok": true, "answer": "..."}`
  * `{"ok": false, "error": "mensaje"}`

---

## 🧯 Solución de problemas

### 1) “TemplateNotFound: index.html”

* Asegúrate de que **existe** `templates/index.html`.
* Verifica que en `app.py` se inicializa Flask con:

  ```python
  app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
  ```
* No combines carpetas (p. ej., evita nombres tipo `uploads; templates`). Deben ser **dos** carpetas separadas: `uploads/` y `templates/`.

### 2) “Unexpected token ‘<’, ‘\<!doctype’ is not valid JSON”

El cliente esperaba JSON, pero el servidor devolvió **HTML** (normalmente un error 500/413).

* Revisa la traza en consola.
* `/analyze` ya está envuelto para **devolver JSON** incluso en errores.
* Causas comunes:

  * **`OPENAI_API_KEY`** no configurada.
  * PDF excede **20 MB** → devuelve `{"ok": false, "error": "... (413)"}`.
  * PDF **escaneado** sin OCR → PyPDF2 no extrae texto.
  * Excepción dentro de `prompts.py` (regex/encoding).

### 3) “El archivo supera el límite (20 MB)”

* Reduce el tamaño o aumenta el límite:

  ```python
  app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024  # 40 MB
  ```

### 4) No extrae texto del PDF

* Si es un escaneo, corre **OCR** antes (p. ej., `ocrmypdf input.pdf output.pdf`).

### 5) Conectividad con OpenAI

* Verifica internet y que tu clave es válida.
* Prueba un request mínimo en Python para descartar problemas de red.

---

