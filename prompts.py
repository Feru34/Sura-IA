# prompts.py
from __future__ import annotations
import re
from textwrap import dedent
import os

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

----------------------------------------------------------------------
COASEGURO, REASEGURO E IMPAIRMENT DE ACTIVOS POR REASEGURO/COASEGURO
Grupo SURA considera el coaseguro como la concurrencia acordada de dos o más entidades aseguradoras en
la cobertura de un mismo riesgo; para los contratos de coaseguros la responsabilidad de cada aseguradora 
frente al asegurado es limitada a su porcentaje de participación en el negocio. 
Grupos SURA reconoce en el estado de situación financiera el saldo derivado de las operaciones de coaseguro 
con base en el porcentaje de participación pactado en el contrato de seguro. 
Grupo SURA considera que un activo por reaseguro y coaseguro se encuentra deteriorado y reducirá su valor en 
libros y reconocerá los efectos en el resultado, sí y sólo si: 
- Existe evidencia objetiva, a consecuencia de un evento que haya ocurrido después del reconocimiento inicial 
  del activo por reaseguro, de que el cedente puede no recibir todos los importes que se le adeuden en función 
  de los términos del contrato, y 
- Ese evento tenga un efecto que se puede medir con fiabilidad sobre los importes que el cedente vaya a 
  recibir de la compañía reaseguradora. 
Los activos por contratos de reaseguro son evaluados por deterioro mínimo una vez al año para detectar
cualquier evento que pueda provocar deterioro al valor de estos. Los factores desencadenantes pueden incluir 
disputas legales con terceras partes, cambios en el capital y en los niveles de superávit, modificaciones a las 
calificaciones de crédito de contraparte y una experiencia histórica respecto al cobro de las respectivas 
compañías reaseguradoras. 

----------------------------------------------------------------------
PASIVOS ESTIMADOS DE CONTRATOS DE SEGUROS 
Los pasivos estimados por contratos de seguros representan para Grupo SURA la mejor estimación sobre los 
pagos futuros a efectuar por los riesgos asumidos en las obligaciones de seguro, los cuales se miden y se 
reconocen como un pasivo. 
Los pasivos estimados de contratos de seguro para Grupo SURA son: 
a) Pasivos estimados de contratos de seguros por reclamos. Son provisiones constituidas para reflejar el costo 
   estimado de siniestros que han ocurrido y no han sido pagados. En esta categoría se incluyen: 
   - Pasivos estimados de contratos de seguros de siniestros avisados no liquidados. Corresponde a las 
     provisiones y gastos directos de liquidación por siniestros avisados. El pasivo se reconoce en la fecha en 
     que el asegurado y/o beneficiario notifica la ocurrencia del siniestro cubierto y es sometida a un recálculo 
     mensual; 
   - Pasivos estimados de siniestros ocurridos no avisados (IBNR). Corresponde a las provisiones para reflejar 
     aquellos siniestros que han ocurrido pero que a la fecha del periodo sobre el que se informa no han sido 
     reportados por el asegurado y/o beneficiario. 
   La estimación de la reserva de siniestros ocurridos no avisados se determina utilizando una variedad de 
   técnicas estándar de proyección de siniestros actuariales. 
   La suposición principal subyacente a estas técnicas es la experiencia del desarrollo de siniestros pasados 
   de las compañías de Grupo SURA que se puedan utilizar para proyectar el desarrollo futuro de los 
   siniestros y su costo final. Estos métodos extrapolan el desarrollo de pérdidas pagadas e incurridas, el 
   costo promedio por reclamo y los números de reclamación basados en el desarrollo observado de años 
   anteriores y las relaciones de pérdidas esperadas. 
   El desarrollo histórico de siniestros se analiza principalmente por años de ocurrencia, pero también puede 
   ser analizado por ramos, productos y tipos de reclamación. Los grandes siniestros suelen ser tratados por 
   separado, ya sea reservándose por el valor estimado de los ajustadores de siniestros o proyectándose por 
   separado para reflejar su desarrollo futuro. 
   Un juicio cualitativo adicional se utiliza para evaluar hasta qué punto las tendencias pasadas pueden no 
   aplicarse en el futuro, (por ejemplo, para reflejar ocurrencias únicas, cambios en factores externos o de 
   mercado, condiciones económicas, niveles de inflación de siniestros, decisiones judiciales y legislación, 
   así como factores internos como la mezcla de cartera, características de la política y procedimientos de 
   manejo de siniestros) con el fin de llegar al costo final estimado de las siniestros que representa el valor 
   esperado de las reclamaciones. 
- Pasivos estimados por compromisos futuros. Son provisiones constituidas para reflejar los compromisos 
  futuros esperados con los asegurados. 
- Pasivo estimado de riesgos en curso. Es la provisión que se constituye para el cumplimiento de las 
  obligaciones futuras derivadas de los compromisos asumidos en las pólizas vigentes a la fecha de cálculo. 
  El pasivo estimado de riesgos en curso está compuesto por el pasivo de prima no devengada y el pasivo 
  por la insuficiencia de primas. 
  El pasivo estimado de prima no devengada representa la porción de las primas emitidas de las pólizas 
  vigentes y de las primas emitidas de las pólizas con inicio de vigencia futura. 
  El pasivo estimado por insuficiencia de primas complementará el pasivo de prima no devengada en la 
  medida en que la prima no resulte suficiente para cubrir el riesgo en curso y los gastos no causados. 
b) Pasivo actuarial. Es la provisión que se constituye para atender el pago de las obligaciones asumidas en los 
   seguros de vida individual y en los amparos cuya prima se ha calculado en forma nivelada. También son 
   seguros cuyo beneficio se paga en forma de renta. 
c) Pasivo actuarial para seguros (excluye rentas vitalicias). Son provisiones calculadas sobre la base del método 
   actuarial, tomando las condiciones actuales de los contratos de seguros. La provisión se determina como la 
   suma del valor presente de los beneficios futuros esperados, el manejo de reclamaciones y los gastos de 
   administración de las pólizas, las opciones y las garantías y la utilidad de las inversiones de activos que 
   respaldan los pasivos, los cuales están directamente relacionados con el contrato, menos el valor 
   descontado de las primas que se espera que se requieren para cumplir con los pagos futuros basados en las 
   hipótesis de valoración utilizadas. 
d) Pasivo actuarial para rentas vitalicias. La provisión es calculada sobre la base del valor presente de los 
   beneficios futuros comprometidos según el contrato y los gastos operacionales directos en los que la 
   compañía incurrirá para el pago de los compromisos del contrato. 
e) Pasivos estimados de primas no devengadas. Son provisiones constituidas para los seguros de corto plazo, 
   tanto colectivos como individuales, en los que la periodicidad de pago de prima difiere de la vigencia de la 
   cobertura y en consecuencia, se ha recibido una prima por el riesgo futuro, la cual debe ser provisionada. La 
   provisión es determinada como la prima ingresada neta de gastos y es amortizada en el plazo de cobertura. 
f) Pasivos estimados por componentes de depósito (ahorro) en seguros de vida o reserva de valor del fondo. 
   Es una provisión, que se reconoce inicialmente a valor razonable con cambios a resultados (precio de la 
   póliza excluyendo los gastos de emisión de esta) y posteriormente los depósitos y retiros son reconocidos 
   como ajustes a la provisión. El valor razonable de los contratos con unidades (unit-linked) son determinados 
   como el producto de la cantidad de unidades alocadas a cada fondo a la fecha de reporte y el precio unitario 
   de las unidades de cada fondo a la misma fecha. 
g) Pasivos estimados de insuficiencia de activos. Es una provisión que se constituye para compensar la
   insuficiencia que puede surgir al cubrir los flujos de pasivos esperados que conforman el pasivo actuarial con 
   los flujos de activos de la entidad aseguradora. 
h) Pasivos estimados de siniestros pendientes. Es la provisión que se constituye para atender el pago de los 
   siniestros ocurridos una vez avisados o para garantizar la cobertura de los no avisados, a la fecha de cálculo. 
   El pasivo estimado de siniestros pendientes está compuesto por el pasivo de siniestros avisados y el pasivo 
   de siniestros ocurridos no avisados. 
   El pasivo de siniestros avisados corresponde al monto de recursos que se debe destinar para atender los 
   pagos de los siniestros ocurridos una vez estos hayan sido avisados, así como los gastos asociados a estos, 
   a la fecha de cálculo de este pasivo. 
   El pasivo de siniestros ocurridos no avisados representa una estimación del monto de recursos que se debe 
   destinar para atender los futuros pagos de siniestros que ya han ocurrido, a la fecha de cálculo de este pasivo, 
   pero que todavía no han sido avisados a la entidad aseguradora o para los cuales no se cuenta con suficiente 
   información. 
i) Derivados implícitos. Los derivados implícitos en contratos de seguro son separados si no se considera que 
   están estrechamente relacionados con el contrato de seguro principal y no cumplen con la definición de un 
   contrato de seguro. 
   Estos derivados implícitos se presentan por separado en la categoría de instrumentos financieros y se miden 
   a valor razonable con cambios en resultados. 

Prueba de adecuación de pasivos estimados de contratos de seguro 
Las provisiones técnicas registradas son sujetas a una prueba de razonabilidad como mínimo una vez al año, 
con el objetivo de determinar su suficiencia sobre la base de proyecciones de todos los flujos de caja futuros de 
los contratos vigentes. Si como consecuencia de esta prueba se pone de manifiesto que las mismas son 
insuficientes, son ajustadas con cargo a resultados del ejercicio.
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
