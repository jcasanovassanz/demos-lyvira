"""Demo pública V1: Diagnóstico express de procesos con IA."""
from __future__ import annotations

import json

import streamlit as st

from public_demo_engine import Assessment, evaluate
from public_demo_pdf import build_result_pdf


st.set_page_config(
    page_title="LYVIRA · Diagnóstico express de procesos",
    page_icon=":material/route:",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#172A3A; --teal:#237C7B; --mint:#E6F2EF; --coral:#E77B62; --sand:#F6F2EA; --slate:#506273; --line:#D8E0E1; }
        .block-container { max-width: 1040px; padding-top: 2.2rem; padding-bottom: 4rem; }
        .hero { background: linear-gradient(135deg, #172A3A 0%, #214B58 100%); border-radius: 22px; padding: 2.3rem 2.4rem 2rem; margin-bottom: 1.4rem; color: white; position: relative; overflow: hidden; }
        .hero:after { content: ''; position:absolute; width:220px; height:220px; right:-70px; top:-90px; border:35px solid rgba(230,242,239,.16); border-radius:50%; }
        .eyebrow { color:#A9D9D0; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; margin-bottom:.7rem; }
        .brand-title { color:#D4EEE9; font-size:.92rem; font-weight:700; letter-spacing:.02em; margin-bottom:.9rem; }
        .hero h1 { color:white; font-size: clamp(2rem, 5vw, 3.4rem); line-height:1.04; margin:0 0 1rem; letter-spacing:-.04em; max-width:720px; }
        .hero p { color:#E6F2EF; font-size:1.08rem; line-height:1.55; max-width:690px; margin:0; }
        .micro { color:#B8C5CC; font-size:.82rem; margin-top:1.3rem; }
        .stepbar { display:flex; gap:.45rem; align-items:center; margin:1rem 0 1.8rem; color:var(--slate); font-size:.82rem; }
        .stepbar .dot { width:9px; height:9px; border-radius:50%; background:var(--line); }
        .stepbar .dot.active { background:var(--coral); box-shadow:0 0 0 5px #fbe6e1; }
        .stepbar .line { flex:1; height:1px; background:var(--line); }
        .soft-card { background:var(--mint); border-left:5px solid var(--coral); border-radius:12px; padding:1rem 1.15rem; margin:1rem 0 1.5rem; color:var(--ink); }
        .result-card { background:var(--ink); border-radius:18px; padding:1.5rem; color:white; margin:1rem 0; }
        .result-card h2 { color:white; margin:.25rem 0 .6rem; }
        .result-card p { color:#E6F2EF; }
        .badge { display:inline-block; background:#A9D9D0; color:var(--ink); padding:.35rem .65rem; border-radius:999px; font-size:.75rem; font-weight:700; }
        .kicker { text-transform:uppercase; letter-spacing:.1em; font-size:.7rem; color:var(--teal); font-weight:800; }
        .muted { color:var(--slate); font-size:.9rem; }
        .metric-card { background:white; border:1px solid var(--line); border-radius:14px; padding:1rem; min-height:115px; }
        .metric-card .value { color:var(--ink); font-size:1.35rem; font-weight:750; margin-top:.35rem; }
        .metric-card .label { color:var(--slate); font-size:.83rem; }
        .flow { display:flex; flex-wrap:wrap; align-items:center; gap:.5rem; margin:.8rem 0; }
        .flow span { background:var(--sand); border:1px solid #eadfce; border-radius:999px; color:var(--ink); padding:.45rem .7rem; font-size:.82rem; }
        .flow b { color:var(--coral); }
        [data-testid="stForm"] { border:1px solid var(--line); border-radius:18px; padding:1.2rem 1.25rem; background:#fff; }
        [data-testid="stFormSubmitButton"] button { background:var(--teal); border-color:var(--teal); color:white; border-radius:10px; padding:.6rem 1rem; font-weight:700; }
        [data-testid="stFormSubmitButton"] button:hover { background:var(--ink); border-color:var(--ink); color:white; }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">LYVIRA · laboratorio de IA aplicada</div>
      <div class="brand-title">LYVIRA · Diagnóstico express de procesos</div>
      <h1>¿Qué parte de tu proceso merece la pena mejorar con IA?</h1>
      <p>Responde unas preguntas y obtén una orientación rápida. No empezamos por la herramienta: empezamos por entender el trabajo.</p>
      <div class="micro">3 minutos · sin subir documentos · resultado educativo</div>
    </section>
    """,
    unsafe_allow_html=True,
)

has_result = "public_result" in st.session_state
st.markdown(
    f"""
    <div class="stepbar"><span class="dot active"></span><span>Describe</span><span class="line"></span><span class="dot {'active' if has_result else ''}"></span><span>Descubre</span><span class="line"></span><span class="dot"></span><span>Decide el siguiente paso</span></div>
    """,
    unsafe_allow_html=True,
)

if not has_result:
    st.markdown(
        '<div class="soft-card"><strong>La pregunta correcta no es “¿dónde puedo meter IA?”</strong><br>Es “¿qué proceso repetimos, dónde pierde valor y qué parte podemos mejorar de forma segura?”.</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Haz una primera revisión")
    st.caption("Usa un proceso concreto, no un área completa. Por ejemplo: preparar propuestas, revisar facturas o responder solicitudes.")

    # Este selector debe quedar fuera del formulario: así el subformulario
    # específico se actualiza inmediatamente al cambiar de área.
    area = st.segmented_control(
        "Área del proceso",
        ["Ventas", "Marketing", "Administración", "Finanzas", "Atención al cliente", "Operaciones"],
        default="Ventas",
        key="area",
    )

    with st.form("public_assessment"):
        process = st.text_input("¿Qué proceso quieres mejorar?", placeholder="Ej.: preparar propuestas después de una reunión comercial")
        goal = st.text_area("¿Qué te gustaría mejorar?", placeholder="Ej.: tardamos mucho en preparar el primer borrador y cada persona lo hace de forma distinta.", height=100)

        st.markdown("**Sobre cómo funciona hoy**")
        frequency = st.select_slider("¿Con qué frecuencia ocurre?", options=[1, 2, 3, 4, 5], value=4, format_func=lambda value: {1: "Ocasional", 2: "Mensual", 3: "Semanal", 4: "Diaria", 5: "Varias veces al día"}[value])
        time = st.select_slider("¿Cuánto tiempo consume?", options=[1, 2, 3, 4, 5], value=3, format_func=lambda value: {1: "Muy poco", 2: "Poco", 3: "Moderado", 4: "Bastante", 5: "Mucho"}[value])
        repetition = st.select_slider("¿Cuánto se repite?", options=[1, 2, 3, 4, 5], value=4, format_func=lambda value: {1: "Muy variable", 2: "Variable", 3: "Algo repetible", 4: "Bastante repetible", 5: "Muy repetible"}[value])
        rules = st.select_slider("¿Las reglas están claras y documentadas?", options=[1, 2, 3, 4, 5], value=3, format_func=lambda value: {1: "No", 2: "Poco", 3: "A medias", 4: "Bastante", 5: "Sí"}[value])
        review = st.select_slider("¿El resultado se puede revisar fácilmente?", options=[1, 2, 3, 4, 5], value=4, format_func=lambda value: {1: "Es difícil", 2: "Cuesta", 3: "Depende", 4: "Sí", 5: "Muy fácil"}[value])
        impact = st.select_slider("¿Qué impacto tiene el problema?", options=[1, 2, 3, 4, 5], value=4, format_func=lambda value: {1: "Menor", 2: "Bajo", 3: "Moderado", 4: "Importante", 5: "Crítico"}[value])
        risk = st.selectbox("¿Qué riesgo tendría un error?", ["bajo", "medio", "alto"], index=1, format_func=lambda value: {"bajo": "Bajo: se puede corregir fácilmente", "medio": "Medio: requiere revisión", "alto": "Alto: puede afectar a dinero, clientes o decisiones"}[value])
        task_types = st.pills("¿Qué tipo de trabajo predomina?", ["Buscar información", "Clasificar", "Redactar", "Copiar datos", "Decidir", "Revisar o aprobar"], selection_mode="multi", default=["Redactar"], key="task_types")
        area_details = {}
        if area == "Ventas":
            st.markdown("**Amplía el contexto comercial**")
            st.caption("Estas preguntas hacen que el resultado sea más útil para un flujo de ventas. No introduzcas nombres de clientes ni importes reales.")
            sales_stage = st.selectbox("¿En qué momento del proceso quieres intervenir?", ["Captación y primer contacto", "Cualificación", "Después de una reunión", "Preparación de propuesta", "Seguimiento", "Cierre"], index=2)
            sales_source = st.selectbox("¿De dónde llegan normalmente las oportunidades?", ["Web o formulario", "Referencias", "Redes sociales", "Prospección", "Varios canales"], index=4)
            sales_notes = st.selectbox("¿Dónde quedan las notas y la información?", ["CRM estructurado", "CRM, pero no siempre actualizado", "Notas y correos sin estructura fija", "Dispersas en varios sitios"], index=2)
            sales_crm = st.selectbox("¿Cómo registráis la oportunidad?", ["CRM actualizado", "CRM, pero no siempre actualizado", "Hoja de cálculo", "No usamos CRM", "Otro sistema"], index=1)
            sales_proposal = st.selectbox("¿Qué resultado comercial quieres mejorar?", ["Resumen de oportunidad", "Cualificación", "Propuesta comercial", "Seguimiento", "Previsión de cierre"], index=2)
            sales_approvals = st.selectbox("¿Quién debe revisar o aprobar?", ["La persona comercial", "Dirección comercial", "Dirección comercial y operaciones", "Depende del caso"], index=1)
            sales_bottlenecks = st.pills("¿Dónde se atasca más el proceso?", ["Buscar información", "Cualificar", "Redactar propuesta", "Precio o descuentos", "Calendario", "Seguimiento"], selection_mode="multi", default=["Redactar propuesta"], key="sales_bottlenecks")
            area_details = {
                "stage": sales_stage,
                "lead_source": sales_source,
                "notes": sales_notes,
                "crm": sales_crm,
                "proposal": sales_proposal,
                "approvals": sales_approvals,
                "bottlenecks": list(sales_bottlenecks or []),
            }
        elif area == "Marketing":
            st.markdown("**Amplía el contexto de marketing**")
            st.caption("Estas preguntas ayudan a distinguir creación, aprobación, publicación y medición.")
            marketing_stage = st.selectbox("¿Qué momento quieres mejorar?", ["Brief y planificación", "Investigación", "Creación de contenidos", "Aprobación", "Publicación", "Medición"], index=2)
            marketing_channel = st.selectbox("¿Qué canal concentra el trabajo?", ["Blog", "LinkedIn", "Email", "Redes sociales", "Campañas de pago", "Varios canales"], index=5)
            marketing_output = st.selectbox("¿Qué resultado quieres mejorar?", ["Brief", "Calendario", "Piezas de contenido", "Campaña", "Informe de resultados"], index=2)
            marketing_approval = st.selectbox("¿Quién aprueba antes de publicar?", ["Una persona", "Dirección", "Cliente o equipo externo", "Depende de la pieza"], index=0)
            marketing_sources = st.selectbox("¿Cómo están las fuentes y mensajes?", ["Centralizados y aprobados", "En varios documentos", "Dependen de cada persona", "No hay una biblioteca clara"], index=1)
            marketing_bottlenecks = st.pills("¿Dónde se atasca más?", ["Investigación", "Redacción", "Diseño", "Aprobaciones", "Reutilización", "Medición"], selection_mode="multi", default=["Redacción"], key="marketing_bottlenecks")
            marketing_details = {"stage": marketing_stage, "channel": marketing_channel, "output": marketing_output, "approval": marketing_approval, "sources": marketing_sources, "bottlenecks": list(marketing_bottlenecks or []), "gaps": ["Definir qué mensajes, fuentes y piezas están aprobados para reutilizar."]}
            area_details = marketing_details
        elif area == "Finanzas":
            st.markdown("**Amplía el contexto financiero**")
            st.caption("No introduzcas importes reales, datos bancarios ni información identificable.")
            finance_stage = st.selectbox("¿Qué momento quieres mejorar?", ["Recepción de documentos", "Extracción de datos", "Validación", "Conciliación", "Aprobación", "Informe"], index=1)
            finance_document = st.selectbox("¿Qué documento o proceso analizas?", ["Facturas", "Gastos", "Cobros", "Pagos", "Conciliación bancaria", "Informe financiero"], index=0)
            finance_output = st.selectbox("¿Qué resultado quieres mejorar?", ["Datos estructurados", "Detección de errores", "Bandeja de revisión", "Informe", "Previsión"], index=1)
            finance_approval = st.selectbox("¿Quién debe aprobar o revisar?", ["Administración", "Dirección financiera", "Dirección", "Depende del importe"], index=1)
            finance_source = st.selectbox("¿De dónde llegan los datos?", ["ERP o sistema contable", "Email", "Carpeta de documentos", "Varios canales"], index=1)
            finance_exceptions = st.pills("¿Qué excepciones aparecen?", ["Datos ausentes", "Importes inconsistentes", "Duplicados", "Fechas", "Proveedor", "Impuestos"], selection_mode="multi", default=["Datos ausentes"], key="finance_exceptions")
            finance_details = {"stage": finance_stage, "document": finance_document, "output": finance_output, "approval": finance_approval, "source": finance_source, "exceptions": list(finance_exceptions or []), "gaps": ["Definir qué validaciones son obligatorias y qué errores exigen revisión humana."]}
            area_details = finance_details
        elif area == "Administración":
            st.markdown("**Amplía el contexto administrativo**")
            st.caption("Piensa en una petición concreta y repetitiva, no en toda la administración.")
            admin_stage = st.selectbox("¿Qué momento quieres mejorar?", ["Recepción de peticiones", "Comprobación de datos", "Registro", "Tramitación", "Respuesta", "Archivo"], index=1)
            admin_input = st.selectbox("¿Cuál es la entrada principal?", ["Email", "Formulario", "Documento", "Hoja de cálculo", "Varias fuentes"], index=0)
            admin_tool = st.selectbox("¿Dónde se gestiona actualmente?", ["ERP o gestor", "Hoja de cálculo", "Email", "Carpeta compartida", "Varios sistemas"], index=1)
            admin_output = st.selectbox("¿Qué resultado quieres mejorar?", ["Registro completo", "Respuesta", "Documento", "Seguimiento", "Archivo"], index=0)
            admin_approval = st.selectbox("¿Hay una aprobación necesaria?", ["No", "Responsable del área", "Dirección", "Depende del caso"], index=1)
            admin_bottlenecks = st.pills("¿Dónde se atasca más?", ["Datos incompletos", "Copiar información", "Buscar documentos", "Esperas", "Aprobaciones", "Archivo"], selection_mode="multi", default=["Copiar información"], key="admin_bottlenecks")
            admin_details = {"stage": admin_stage, "input": admin_input, "tool": admin_tool, "output": admin_output, "approval": admin_approval, "bottlenecks": list(admin_bottlenecks or []), "gaps": ["Definir el registro único del proceso y los campos obligatorios."]}
            area_details = admin_details
        elif area == "Operaciones":
            st.markdown("**Amplía el contexto operativo**")
            st.caption("Describe un flujo de coordinación o ejecución que se pueda observar de principio a fin.")
            ops_stage = st.selectbox("¿Qué momento quieres mejorar?", ["Entrada de la orden", "Planificación", "Coordinación", "Ejecución", "Incidencias", "Cierre"], index=1)
            ops_system = st.selectbox("¿Dónde se registra el trabajo?", ["ERP o sistema operativo", "Hoja de cálculo", "Gestor de proyectos", "Email y mensajes", "Varios sistemas"], index=2)
            ops_handoffs = st.selectbox("¿Cuántos equipos intervienen?", ["Una persona", "Dos personas", "Varios equipos", "Depende del caso"], index=2)
            ops_output = st.selectbox("¿Qué resultado quieres mejorar?", ["Plan de trabajo", "Parte operativo", "Coordinación", "Detección de bloqueos", "Informe"], index=3)
            ops_bottlenecks = st.pills("¿Qué bloquea más el flujo?", ["Información incompleta", "Esperas", "Cambios de prioridad", "Dependencias", "Incidencias", "Retrabajo"], selection_mode="multi", default=["Esperas"], key="ops_bottlenecks")
            ops_details = {"stage": ops_stage, "system": ops_system, "handoffs": ops_handoffs, "output": ops_output, "bottlenecks": list(ops_bottlenecks or []), "gaps": ["Definir quién puede cambiar prioridades y cómo se registran las excepciones."]}
            area_details = ops_details
        elif area == "Atención al cliente":
            st.markdown("**Amplía el contexto de atención al cliente**")
            st.caption("No introduzcas nombres, correos ni conversaciones reales. Usa una descripción general del flujo.")
            support_stage = st.selectbox("¿Qué momento quieres mejorar?", ["Entrada de consultas", "Clasificación", "Búsqueda de información", "Redacción", "Escalado", "Seguimiento"], index=3)
            support_channel = st.selectbox("¿Por qué canal entran?", ["Email", "Formulario", "Chat", "Teléfono", "Varios canales"], index=0)
            support_knowledge = st.selectbox("¿Dónde está la información de respuesta?", ["Base de conocimiento", "Documentos", "CRM", "Experiencia del equipo", "Dispersa en varios sitios"], index=1)
            support_output = st.selectbox("¿Qué resultado quieres mejorar?", ["Clasificación", "Respuesta", "Tiempo de primera respuesta", "Escalado", "Registro"], index=1)
            support_escalation = st.selectbox("¿Cómo se gestionan las excepciones?", ["Reglas claras", "Lo decide cada persona", "Se escalan al responsable", "No está definido"], index=2)
            support_bottlenecks = st.pills("¿Dónde se atasca más?", ["Clasificar", "Buscar información", "Redactar", "Esperar respuesta interna", "Reclamaciones", "Registrar"], selection_mode="multi", default=["Buscar información"], key="support_bottlenecks")
            support_details = {"stage": support_stage, "channel": support_channel, "knowledge": support_knowledge, "output": support_output, "escalation": support_escalation, "bottlenecks": list(support_bottlenecks or []), "gaps": ["Definir qué consultas puede preparar la IA y cuáles deben escalarse siempre."]}
            area_details = support_details
        submitted = st.form_submit_button("Analizar mi proceso", type="primary", icon=":material/arrow_forward:", width="stretch")

    if submitted:
        if not process or len(process.strip()) < 8:
            st.error("Describe un proceso concreto para poder analizarlo.", icon=":material/edit:")
        elif not task_types:
            st.error("Selecciona al menos un tipo de trabajo.", icon=":material/checklist:")
        else:
            assessment = Assessment(area or "Ventas", process, frequency, time, repetition, rules, review, impact, risk, tuple(task_types), goal, area_details)
            st.session_state.public_result = evaluate(assessment)
            st.rerun()
else:
    result = st.session_state.public_result
    score = result["score"]
    st.markdown(f'<span class="badge">{result["area"]} · {result["readiness_label"]}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-card"><div class="kicker" style="color:#A9D9D0">Resultado de tu primera revisión</div><h2>{safe_name(result["process"])}</h2><p>{result["explanation"]}</p></div>', unsafe_allow_html=True)
    if result.get("goal_focus"):
        st.markdown(f'<div class="soft-card"><strong>Objetivo que has declarado</strong><br>{safe_name(result["goal_focus"])}</div>', unsafe_allow_html=True)
    st.progress(result["score_percent"], text=f"Índice de oportunidad: {score}/30")

    metric_cols = st.columns(3)
    with metric_cols[0].container(border=True):
        st.markdown('<div class="label">Papel recomendado</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="value">{result["ai_role"]}</div>', unsafe_allow_html=True)
    with metric_cols[1].container(border=True):
        st.markdown('<div class="label">Riesgo declarado</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="value">{result["risk"].capitalize()}</div>', unsafe_allow_html=True)
    with metric_cols[2].container(border=True):
        st.markdown('<div class="label">Tipo de trabajo</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="value">{len(result["task_types"])} señales</div>', unsafe_allow_html=True)

    st.subheader("Qué haría primero")
    st.markdown(f'<div class="soft-card"><strong>{result["next_step"]}</strong></div>', unsafe_allow_html=True)

    st.subheader("Qué conviene tener en cuenta")
    for blocker in result["blockers"]:
        st.markdown(f"- {blocker}")

    with st.container(border=True):
        st.markdown("**Un flujo prudente para empezar**")
        st.markdown('<div class="flow"><span>Entrada</span><b>→</b><span>IA prepara</span><b>→</b><span>Persona revisa</span><b>→</b><span>Se mide</span></div>', unsafe_allow_html=True)
        st.caption("La demo no recomienda enviar comunicaciones ni tomar decisiones sensibles automáticamente.")

    if result.get("area_analysis"):
        area_analysis = result["area_analysis"]
        st.subheader(f"Lectura específica de {result['area']}")
        st.caption("Esta capa adapta las preguntas y el piloto al área elegida. La puntuación común permite comparar oportunidades sin perder el contexto de cada departamento.")
        with st.container(border=True):
            fact_cols = st.columns(min(4, max(1, len(area_analysis.get("context_facts", {})))))
            for column, (label, value) in zip(fact_cols, area_analysis.get("context_facts", {}).items()):
                with column:
                    st.markdown(f"**{label}**")
                    st.write(value)
        flow_items = area_analysis.get("current_flow", [])
        flow_html = "<div class='flow'>" + "<b>→</b>".join(f"<span>{item}</span>" for item in flow_items) + "</div>"
        with st.expander(f"Ver el flujo de {result['area'].lower()} detectado", expanded=True, icon=":material/account_tree:"):
            st.markdown(flow_html, unsafe_allow_html=True)
            if result["area"] == "Ventas":
                st.caption(f"La aplicación ha situado el análisis en: **{area_analysis['stage']}**. El resultado comercial seleccionado es: **{area_analysis['proposal_type']}**.")
            else:
                st.caption(f"La aplicación ha situado el análisis en: **{area_analysis['context_facts'].get('Momento analizado', 'el flujo seleccionado')}**.")
        with st.container(border=True):
            st.markdown("**Qué está viendo la herramienta**")
            for finding in area_analysis["findings"]:
                st.markdown(f"- {finding}")
        with st.container(border=True):
            st.markdown("**Preguntas que conviene resolver antes de automatizar**")
            for gap in area_analysis["gaps_to_clarify"]:
                st.markdown(f"- {gap}")
        with st.container(border=True):
            st.markdown(f"**Piloto sugerido para {result['area'].lower()}**")
            for item in area_analysis["pilot"]:
                st.markdown(f"- {item}")
            st.markdown("**Métricas:** " + " · ".join(area_analysis["metrics"]))
        with st.expander("Controles que deberían mantenerse", icon=":material/shield:"):
            for control in area_analysis["controls"]:
                st.markdown(f"- {control}")

    pdf_data = build_result_pdf(result)
    st.subheader("Tu ficha de diagnóstico")
    st.caption("Puedes revisarla aquí y descargarla en PDF para compartirla o guardarla.")
    with st.expander("Ver la ficha PDF", expanded=True, icon=":material/picture_as_pdf:"):
        st.pdf(pdf_data, height=720, alt="Ficha PDF del diagnóstico de proceso")
    pdf_col, json_col = st.columns(2)
    with pdf_col:
        st.download_button(
            "Descargar ficha en PDF",
            data=pdf_data,
            file_name="lyvira-diagnostico-proceso.pdf",
            mime="application/pdf",
            icon=":material/picture_as_pdf:",
            width="stretch",
        )
    with json_col:
        st.download_button(
            "Descargar datos JSON",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="lyvira-diagnostico-proceso.json",
            mime="application/json",
            icon=":material/download:",
            width="stretch",
        )

    st.info(
        "Esta versión pública no solicita datos personales, no almacena leads y no se conecta a servicios externos. "
        "El diagnóstico y el PDF se generan localmente durante la sesión.",
        icon=":material/privacy_tip:",
    )

    with st.expander("Ver cómo se ha calculado", icon=":material/visibility:"):
        st.write("La puntuación suma frecuencia, tiempo, repetición, claridad de reglas, facilidad de revisión e impacto. El riesgo no suma puntos: actúa como filtro de seguridad.")
        st.json(result)
    if st.button("Analizar otro proceso", icon=":material/refresh:"):
        del st.session_state.public_result
        st.rerun()
