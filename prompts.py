# prompts.py
from __future__ import annotations
import re
from textwrap import dedent
import os


# --- NUEVO: referencia fija SURA para arrendamientos ---
SURA_LEASE_POLICY = dedent("""
Nota 2.4.6. Arrendamientos 
Grupo SURA evalúa al inicio del contrato si un contrato es, o contiene, un arrendamiento. Es decir, si el contrato 
otorga el derecho a controlar el uso de un activo identificado por un período de tiempo a cambio de una 
contraprestación. 
Grupo SURA aplica un enfoque único de reconocimiento y medición para todos los arrendamientos, excepto
los arrendamientos a corto plazo y los arrendamientos de activos de bajo valor. Grupo SURA reconoce pasivos 
por arrendamiento para realizar pagos por arrendamiento y activos por derecho de uso que representan el 
derecho a usar los activos subyacentes. 
Reconocimiento inicial 
Grupo SURA reconoce los activos por derecho de uso en la fecha de comienzo del arrendamiento, es decir, la 
fecha en que el activo subyacente está disponible para su uso. 
Los activos por derecho de uso se miden al costo, menos cualquier depreciación y pérdidas por deterioro, y 
ajustado por cualquier nueva medición de los pasivos por arrendamiento. El costo de activos por derecho de 
uso incluye el monto de los pasivos por arrendamiento reconocidos, los costos directos iniciales incurridos y los 
pagos realizados en o antes de la fecha de inicio menos los incentivos de arrendamiento recibidos. Los activos 
por derecho de uso se deprecian en línea recta durante el plazo más corto del arrendamiento y la vida útil 
estimada de los activos. Además, están sujetos a revisión de pérdidas por deterioro. 
Los pasivos por arrendamiento son medidos al valor presente de los pagos de arrendamiento a realizar durante 
el plazo del arrendamiento. Los pagos de arrendamiento incluyen pagos fijos menos los incentivos de 
arrendamiento por cobrar, si los hubiere. Los pagos de arrendamiento también incluyen el precio de ejercicio 
de una opción de compra que Grupo SURA ejercerá con certeza razonable y los pagos de multas por rescindir 
el arrendamiento, si el plazo del arrendamiento refleja que Grupo SURA ejerce la opción de rescisión. 
Al calcular el valor presente de los pagos de arrendamiento se utiliza la tasa de interés implícita en el 
arrendamiento cuando es fácilmente determinable; en caso de que no sea fácilmente determinable se utiliza 
su tasa incremental de endeudamiento a la fecha de inicio del arrendamiento.

Medición posterior
Después la fecha de comienzo, el importe de los pasivos por arrendamiento se incrementa para reflejar la 
acumulación de intereses y reducido por los pagos de arrendamiento realizados. Además, el importe en libros 
de los pasivos por arrendamiento se vuelve a medir cuando haya una modificación, un cambio en el plazo del 
arrendamiento, un cambio en los pagos del arrendamiento o un cambio en la evaluación de una opción para 
comprar el activo subyacente.
""").strip()



def _clean_text(text: str) -> str:
    """
    Limpia texto extraído de PDF:
    - Une guiones de corte de línea (palabra-\ncontinuación -> palabracontinuación)
    - Normaliza espacios repetidos y saltos de línea excesivos
    - Quita caracteres de control fuera de \n y \t
    """
    if not text:
        return ""
    t = text

    # Unir palabras cortadas por salto de línea con guion final
    t = re.sub(r"-\s*\n\s*", "", t)

    # Reemplazar saltos blandos por espacio
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)

    # Normalizar múltiples nuevas líneas (máx 2 seguidas)
    t = re.sub(r"\n{3,}", "\n\n", t)

    # Colapsar espacios múltiples
    t = re.sub(r"[ \t]{2,}", " ", t)

    # Remover caracteres no imprimibles (excepto \n y \t)
    t = re.sub(r"[^\x09\x0A\x20-\x7E\u00A0-\uFFFF]", "", t)
    return t.strip()


def _truncate_middle(text: str, max_chars: int = 35000, head: int = 20000) -> str:
    """
    Si el texto excede max_chars, conserva el inicio (head) y el final
    (lo que quepa) separándolos con un marcador. Así evitamos prompts enormes.
    """
    if len(text) <= max_chars:
        return text
    tail = max_chars - head - len("\n\n[... CONTENIDO RECORTADO ...]\n\n")
    tail = max(tail, 0)
    return (
        text[:head]
        + "\n\n[... CONTENIDO RECORTADO ...]\n\n"
        + (text[-tail:] if tail > 0 else "")
    )
    
def save_prompt_to_file(prompt: str, filepath: str = "debug/prompt.txt") -> str:
    """
    Guarda el contenido de `prompt` en un archivo de texto UTF-8.
    Crea la carpeta destino si no existe y retorna la ruta absoluta.
    """
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(prompt)

    return os.path.abspath(filepath)


def generate_prompt_like_robot(pdf_text: str, question: str) -> str:
    """
    Construye el prompt del analista financiero/contable usando:
    - pdf_text: texto extraído de un PDF (políticas/EEFF/contrato).
    - question: pregunta específica a responder.
    Devuelve un string listo para enviar al modelo.
    """
    pdf_text = _clean_text(pdf_text)
    pdf_text = _truncate_middle(pdf_text, max_chars=35000, head=20000)

    prompt = dedent(f"""
    <ROLE>
    Eres un **analista financiero senior** y **especialista en políticas contables** con conocimiento profundo de estados financieros (balance, estado de resultados, flujo de caja, notas) y experiencia específica en **Grupo Sura** (estructura de negocios, prácticas contables típicas de sociedades holding y compañías de servicios financieros en Colombia). Tu trabajo: recibir información adjunta sobre estados financieros y políticas contables, analizarlas y **responder preguntas** basadas en esa información y en lo que ya se sabe de Grupo Sura.
    </ROLE>

    <INSTRUCCIONES>
    1. **Respeta y conserva todas las etiquetas** del input (por ejemplo `<INPUT>`, `<TABLA>`, `<NOTAS>`, etc.). No las elimines ni las renombres.
    2. Cuando el usuario provea documentos o tablas, primero **extrae y normaliza** la información (mapeo de cuentas, periodos, moneda).
    3. Al responder: **indica claramente** (a) qué proviene de los datos entregados, (b) qué proviene de conocimiento general sobre Grupo Sura y (c) qué es una inferencia o suposición.
    4. Si una pregunta requiere conocimiento externo no provisto, **comunícalo explícitamente** y ofrece alternativas (ej., pedir más datos o permitir usar conocimiento público).
    5. Entrega (si aplica) un **resumen ejecutivo**, un **análisis numérico** (ratios y tendencias), **identificación de riesgos / impactos contables** y **recomendaciones prácticas**.
    6. Siempre muestra las **fórmulas** usadas en cálculos clave y las **líneas/etiquetas** exactas de las tablas de entrada que usaste (por ejemplo: `<INPUT>.BalanceSheet.ActivosCorrientes.Caja`).
    7. Idioma de salida: **español** (a menos que el usuario pida lo contrario).
    </INSTRUCCIONES>

    <INPUT>
    <!-- Texto plano extraído del PDF. Mantener formato y etiquetas originales si existen. -->
    {pdf_text}
    </INPUT>

    <PASOS_A_SEGUIR>
    1. **Validación**: Verifica que las etiquetas estén presentes y que los periodos/moneda tengan sentido. Reporta valores faltantes.
    2. **Normalización**: Mapear cuentas a un plan estándar (ej. ActivosCorrientes, PasivosNoCorrientes, IngresosOperacionales, GastosOperacionales).
    3. **Reconciliación**: Asegurar que activos = pasivos + patrimonio; si no, reportar partidas por conciliar y posibles causas (moneda, omisiones, error de signo).
    4. **Cálculos clave**:
       * Liquidez: Current Ratio = Activos Corrientes / Pasivos Corrientes
       * Endeudamiento: Debt/Equity = Pasivo Total / Patrimonio
       * Rentabilidad: ROE = Resultado Neto / Patrimonio promedio; Margen operativo = Utilidad operativa / Ingresos
       * Cobertura intereses = EBIT / Gastos financieros
       * Flujo libre = Flujo operativo - Capex
       * Variaciones YoY y % de cada gran rubro
    5. **Análisis de políticas**: Identificar impactos por políticas (p. ej. reconocimiento de ingresos, consolidación de entidades, tratamiento de asociados y JV, uso de valoración a valor razonable, estimaciones de vida útil y provisiones).
    6. **Comparativa con Grupo Sura** (si corresponde): señalar si las políticas/ratios están alineadas con prácticas comunes de un holding financiero/seguros en Colombia (por ejemplo: tratamiento de instrumentos financieros, consolidación, participaciones estratégicas).
    7. **Respuesta a la pregunta**: entregar respuesta directa, referenciada a las líneas de input y con nivel de confianza (Alto/Medio/Bajo). Incluir supuestos y pasos para replicar los cálculos.
    8. **Recomendaciones**: acciones contables/operativas y preguntas de seguimiento (qué datos faltan).
    </PASOS_A_SEGUIR>

    <OUTPUT>
    Formato de respuesta preferido (JSON + sección humana):
    {{
      "summary_executive": "Resumen breve de 3-5 líneas",
      "validation_checks": ["lista de problemas detectados con referencias a etiquetas"],
      "key_ratios": {{
        "CurrentRatio": {{"value": "X", "formula": "ActivosCorrientes / PasivosCorrientes", "source_lines": ["<INPUT>..."]}}
      }},
      "accounting_policy_issues": [
        {{"issue": "Descripción", "impact": "Cuantitativo si aplica", "reference_note": "<INPUT> Lx-Ly"}}
      ],
      "answer_to_question": {{
        "direct_answer": "Respuesta clara y breve",
        "supporting_analysis": "Explicación y cálculos detallados con referencias exactas",
        "assumptions": ["..."],
        "confidence": "Alto/Medio/Bajo"
      }},
      "recommendations": ["..."],
      "follow_up_questions": ["..."]
    }}
    Además agrega al final una **versión humana** legible (no JSON) para presentaciones o emails.
    </OUTPUT>

    <PREGUNTA_DEL_USUARIO>
    {question}
    </PREGUNTA_DEL_USUARIO>

    FIN DEL PROMPT.
    """).strip()

    return prompt



def generate_prompt(pdf_text: str, question: str, pais : str, empresa: str, anio : int) -> str:
    """
    Genera un prompt para respuesta exclusivamente en lenguaje natural (sin JSON ni tablas),
    incorporando la Nota 2.4.6 de SURA como referencia base para arrendamientos.
    """
    pdf_text = _clean_text(pdf_text)
    pdf_text = _truncate_middle(pdf_text, max_chars=35000, head=20000)

    prompt = dedent(f"""
    <ROLE>
    Eres un analista financiero senior y especialista en políticas contables con conocimiento profundo de estados financieros (balance, estado de resultados, flujo de caja, notas) y experiencia específica en Grupo Sura (estructura de negocios, prácticas contables típicas de sociedades holding y compañías de servicios financieros en Colombia).
    </ROLE>

    <OBJETIVO>
    Analiza la información adjunta y responde la pregunta. 
    La salida debe ser exclusivamente en lenguaje natural, en español, en formato de prosa clara y coherente, sin JSON, sin tablas, sin listas con viñetas o numeradas, y sin bloques de código. 
    Incluye fórmulas clave de forma inline cuando ayuden a la comprensión (por ejemplo: Current Ratio = Activos Corrientes / Pasivos Corrientes).
    </OBJETIVO>

    <CRITERIOS_DE_RESPUESTA>
    - Explica qué parte proviene de los datos del <INPUT>, qué es conocimiento general/sector y qué es inferencia necesaria.
    - Si falta información en el <INPUT>, indícalo de forma explícita y sugiere qué nota o tabla sería necesaria.
    - Cuando uses cifras o razones, muestra la fórmula de manera breve e indica en el mismo párrafo las etiquetas/líneas relevantes del <INPUT>.
    - Describe inconsistencias (p. ej., activos ≠ pasivos + patrimonio) y causas probables (moneda, omisiones, signos).
    - Cierra con una respuesta directa y el nivel de confianza (Alto/Medio/Bajo) en texto natural.
    - Usa máximo 150 palabras.
    </CRITERIOS_DE_RESPUESTA>

    <REFERENCIAS_DE_CÁLCULOS_SUGERIDAS>
    - Liquidez: Current Ratio = Activos Corrientes / Pasivos Corrientes.
    - Endeudamiento: Debt/Equity = Pasivo Total / Patrimonio.
    - Rentabilidad: ROE = Resultado Neto / Patrimonio promedio; Margen operativo = Utilidad operativa / Ingresos.
    - Cobertura de intereses: EBIT / Gastos financieros.
    - Flujo libre: Flujo operativo − Capex.
    - Variaciones YoY y participación porcentual por rubro principal.
    </REFERENCIAS_DE_CÁLCULOS_SUGERIDAS>

    <REFERENCIA_SURA_ARRENDAMIENTOS>
    Usa esta referencia oficial (Nota 2.4.6 de Grupo SURA) como línea base cuando el <INPUT> no incluya la nota completa. 
    Si el <INPUT> provee definiciones o tratamientos distintos, **prioriza el contenido del <INPUT>** y explica la diferencia:
    {SURA_LEASE_POLICY}
    </REFERENCIA_SURA_ARRENDAMIENTOS>

    <INPUT>
    Esto es lo reportado en el estado financerio de {empresa} en el pais {pais} en año {anio} : {pdf_text}
    </INPUT>

    <PREGUNTA_DEL_USUARIO>
    {question}
    </PREGUNTA_DEL_USUARIO>

    Instrucción final y obligatoria: responde únicamente en prosa, en español, sin JSON, sin tablas y sin listas. Si necesitas enumerar ideas, hazlo dentro de la misma narrativa con conectores (primero, luego, además, por último), evitando viñetas o números explícitos.
    """).strip()

    return prompt


# Ejemplo local rápido (no se ejecuta en producción):
if __name__ == "__main__":
    sample_pdf_text = "Política de efectivo y equivalentes: Se consideran efectivo, depósitos a la vista y inversiones de alta liquidez con vencimiento menor a 90 días..."
    sample_question = "Según la política ¿Qué se considera como efectivo y equivalentes de efectivo?"
    print(generate_prompt(sample_pdf_text, sample_question)[:1200] + "\n...\n[Prompt truncado para vista previa]")
