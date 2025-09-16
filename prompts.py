# prompts.py
from __future__ import annotations
import re
from textwrap import dedent


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


def generate_prompt(pdf_text: str, question: str) -> str:
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


# Ejemplo local rápido (no se ejecuta en producción):
if __name__ == "__main__":
    sample_pdf_text = "Política de efectivo y equivalentes: Se consideran efectivo, depósitos a la vista y inversiones de alta liquidez con vencimiento menor a 90 días..."
    sample_question = "Según la política ¿Qué se considera como efectivo y equivalentes de efectivo?"
    print(generate_prompt(sample_pdf_text, sample_question)[:1200] + "\n...\n[Prompt truncado para vista previa]")
