"""Reglas locales de la demo pública V1.

La demo funciona sin un modelo externo. Más adelante se puede añadir una capa
de explicación con IA sin cambiar este contrato de salida.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AREA_LABELS = {
    "Ventas": "ventas",
    "Marketing": "marketing",
    "Administración": "administración",
    "Finanzas": "finanzas",
    "Atención al cliente": "atención al cliente",
    "Operaciones": "operaciones",
}


@dataclass(frozen=True)
class Assessment:
    area: str
    process: str
    frequency: int
    time: int
    repetition: int
    rules: int
    review: int
    impact: int
    risk: str
    task_types: tuple[str, ...]
    goal: str
    area_details: dict[str, Any] = field(default_factory=dict)


def _readiness(total: int, rules: int, review: int, risk: str) -> tuple[str, str, str]:
    if rules <= 2:
        return "Primero hay que ordenar", "Estandarizar antes de automatizar", "Tu proceso puede tener potencial, pero las reglas aún no están suficientemente claras."
    if review <= 2 or risk == "alto":
        return "Necesita revisión", "Asistencia con control humano", "Hay impacto o riesgo suficiente para que la revisión humana sea parte del diseño desde el principio."
    if total >= 23:
        return "Buen candidato", "Asistir con IA", "El proceso parece repetible y revisable: merece un piloto pequeño y medido."
    return "En observación", "Aclarar y probar", "Hay una oportunidad posible, pero conviene concretar mejor el proceso antes de elegir una herramienta."


def _next_step(role: str, task_types: tuple[str, ...]) -> str:
    if role == "Estandarizar antes de automatizar":
        return "Documenta una versión mínima del proceso: entrada, pasos, reglas, responsable y resultado esperado."
    if "Decidir" in task_types or "Revisar o aprobar" in task_types:
        return "Separa la preparación que puede asistir la IA de la decisión y aprobación que debe seguir bajo responsabilidad humana."
    if "Redactar" in task_types:
        return "Prueba primero un borrador interno con una plantilla y una revisión humana antes de automatizar envíos."
    if "Buscar información" in task_types:
        return "Ordena las fuentes autorizadas y comprueba que la información vigente se pueda localizar y revisar."
    return "Elige una tarea concreta, repetitiva y revisable para un primer piloto de una semana."


def _goal_focus(goal: str) -> str:
    """Conserva el objetivo del usuario como foco visible del diagnóstico."""
    cleaned = " ".join(goal.split())
    if not cleaned:
        return ""
    return cleaned[:240] + ("…" if len(cleaned) > 240 else "")


def _sales_analysis(details: dict[str, Any], role: str) -> dict[str, Any]:
    """Devuelve un análisis comercial más rico sin necesidad de un LLM."""
    stage = details.get("stage", "No indicado")
    notes = details.get("notes", "No indicado")
    crm = details.get("crm", "No indicado")
    approvals = details.get("approvals", "No indicado")
    bottlenecks = details.get("bottlenecks", [])
    proposal = details.get("proposal", "No indicado")
    source = details.get("lead_source", "No indicado")
    flow = [
        "reunión o contacto comercial",
        "recopilar información",
        "cualificar oportunidad",
        "preparar propuesta",
        "revisar alcance y condiciones",
        "hacer seguimiento",
    ]
    findings: list[str] = []
    gaps: list[str] = []
    if notes in {"Dispersas en varios sitios", "Notas y correos sin estructura fija"}:
        findings.append("La primera oportunidad está en ordenar las notas antes de pedir a la IA que redacte.")
        gaps.append("Definir una plantilla mínima de reunión con campos obligatorios.")
    if crm in {"No usamos CRM", "CRM, pero no siempre actualizado"}:
        findings.append("La trazabilidad comercial puede perderse aunque el borrador se genere más rápido.")
        gaps.append("Decidir dónde se registra el siguiente paso y quién mantiene el dato.")
    if approvals in {"Dirección comercial", "Dirección comercial y operaciones"}:
        findings.append("El output debe quedar como borrador: la aprobación comercial no se delega.")
    if "Precio o descuentos" in bottlenecks:
        findings.append("El precio debe aparecer como dato consultado y trazable, nunca como una invención del modelo.")
        gaps.append("Documentar reglas de tarifa, descuentos y excepciones.")
    if "Seguimiento" in bottlenecks:
        findings.append("El seguimiento puede ser una segunda oportunidad, pero conviene empezar por el borrador de propuesta.")
    if not findings:
        findings.append("El flujo tiene una base suficiente para elegir una tarea concreta y observarla antes de automatizar.")
    pilot = [
        "ordenar notas de la reunión",
        "detectar información comercial ausente",
        "preparar un borrador interno de propuesta",
    ]
    controls = [
        "No enviar mensajes al cliente automáticamente.",
        "No aprobar precios, descuentos ni compromisos de calendario.",
        "Mostrar fuentes, supuestos y preguntas pendientes.",
        "Mantener una revisión humana antes de compartir la propuesta.",
    ]
    return {
        "stage": stage,
        "lead_source": source,
        "notes_location": notes,
        "crm": crm,
        "proposal_type": proposal,
        "approvals": approvals,
        "bottlenecks": bottlenecks,
        "current_flow": flow,
        "findings": findings,
        "gaps_to_clarify": gaps or ["Registrar el tiempo actual y el número de correcciones."],
        "pilot_scope": pilot,
        "pilot": pilot,
        "controls": controls,
        "metrics": [
            "Tiempo desde la reunión hasta el primer borrador",
            "Número de correcciones importantes",
            "Propuestas con información o compromisos no respaldados",
            "Tiempo de revisión de dirección comercial",
        ],
        "recommended_role": role,
        "context_facts": {
            "Momento analizado": stage,
            "Origen de oportunidades": source,
            "Registro actual": crm,
            "Resultado buscado": proposal,
        },
    }


def _area_analysis(area: str, details: dict[str, Any], role: str) -> dict[str, Any]:
    """Análisis específico de las áreas de la demo pública."""
    if area == "Ventas":
        return _sales_analysis(details, role)

    configurations = {
        "Marketing": {
            "context_facts": {
                "Momento analizado": details.get("stage", "No indicado"),
                "Canal principal": details.get("channel", "No indicado"),
                "Aprobación": details.get("approval", "No indicado"),
                "Resultado buscado": details.get("output", "No indicado"),
            },
            "flow": ["brief", "investigar", "crear", "revisar", "publicar", "medir"],
            "pilot": ["convertir un brief en checklist", "reutilizar contenidos aprobados", "preparar un primer borrador interno"],
            "findings": ["La IA puede ayudar a transformar un brief y preparar borradores, pero la aprobación editorial y de marca siguen siendo humanas."],
            "metrics": ["Tiempo desde brief hasta primer borrador", "Número de rondas de revisión", "Piezas reutilizadas sin rehacer trabajo"],
            "controls": ["Usar solo fuentes y mensajes aprobados.", "Revisar tono, datos y claims antes de publicar.", "No publicar automáticamente en la primera prueba."],
        },
        "Finanzas": {
            "context_facts": {
                "Momento analizado": details.get("stage", "No indicado"),
                "Documento principal": details.get("document", "No indicado"),
                "Aprobación": details.get("approval", "No indicado"),
                "Resultado buscado": details.get("output", "No indicado"),
            },
            "flow": ["recibir documento", "extraer datos", "validar", "resolver excepción", "aprobar", "registrar"],
            "pilot": ["extraer campos de documentos ficticios", "señalar datos ausentes o inconsistentes", "preparar una bandeja de revisión"],
            "findings": ["La primera oportunidad suele estar en preparación y validación documental, no en aprobar o ejecutar pagos."],
            "metrics": ["Tiempo por documento", "Porcentaje de campos correctamente extraídos", "Número de excepciones detectadas"],
            "controls": ["No ejecutar pagos ni asientos automáticamente.", "Revisar importes, proveedores y fechas.", "Probar primero con datos ficticios o anonimizados."],
        },
        "Administración": {
            "context_facts": {
                "Momento analizado": details.get("stage", "No indicado"),
                "Entrada principal": details.get("input", "No indicado"),
                "Herramienta actual": details.get("tool", "No indicado"),
                "Resultado buscado": details.get("output", "No indicado"),
            },
            "flow": ["recibir petición", "comprobar datos", "registrar", "tramitar", "revisar", "confirmar"],
            "pilot": ["detectar datos faltantes", "clasificar peticiones", "preparar respuestas internas o checklists"],
            "findings": ["La asistencia puede reducir copia y búsqueda, siempre que exista una fuente única y un responsable claro."],
            "metrics": ["Tiempo por petición", "Peticiones devueltas por falta de datos", "Trabajo duplicado"],
            "controls": ["No modificar registros críticos sin revisión.", "Mantener trazabilidad de la petición.", "Definir qué información puede consultar la IA."],
        },
        "Operaciones": {
            "context_facts": {
                "Momento analizado": details.get("stage", "No indicado"),
                "Sistema principal": details.get("system", "No indicado"),
                "Intervinientes": details.get("handoffs", "No indicado"),
                "Resultado buscado": details.get("output", "No indicado"),
            },
            "flow": ["recibir orden", "planificar", "coordinar", "ejecutar", "resolver incidencia", "cerrar"],
            "pilot": ["resumir órdenes y prioridades", "detectar bloqueos", "preparar un parte operativo para revisión"],
            "findings": ["La IA puede ayudar a hacer visibles bloqueos y preparar información, pero no debe ocultar dependencias ni comprometer capacidad."],
            "metrics": ["Tiempo de ciclo", "Incidencias o bloqueos", "Retrabajos", "Tiempo de coordinación"],
            "controls": ["Mantener una persona responsable del plan.", "Validar cambios antes de afectar al trabajo operativo.", "Registrar excepciones y causas."],
        },
        "Atención al cliente": {
            "context_facts": {
                "Momento analizado": details.get("stage", "No indicado"),
                "Canal principal": details.get("channel", "No indicado"),
                "Documentación": details.get("knowledge", "No indicado"),
                "Resultado buscado": details.get("output", "No indicado"),
            },
            "flow": ["recibir consulta", "clasificar", "buscar información", "preparar respuesta", "escalar", "registrar"],
            "pilot": ["clasificar consultas", "detectar datos ausentes", "preparar borradores con fuentes visibles"],
            "findings": ["La asistencia puede acelerar clasificación y borradores, pero reclamaciones y excepciones deben escalarse."],
            "metrics": ["Tiempo hasta el primer borrador", "Correcciones", "Escalados", "Reenvíos por error"],
            "controls": ["No enviar respuestas automáticamente.", "Escalar reclamaciones y asuntos sensibles.", "Usar documentación vigente y autorizada."],
        },
    }
    selected = configurations.get(area, configurations["Administración"])
    return {
        **selected,
        "role": role,
        "details": details,
        "gaps_to_clarify": details.get("gaps", ["Registrar el tiempo actual y el número de correcciones."]),
        "recommended_role": role,
    }


def evaluate(assessment: Assessment) -> dict[str, Any]:
    total = sum((assessment.frequency, assessment.time, assessment.repetition, assessment.rules, assessment.review, assessment.impact))
    label, role, explanation = _readiness(total, assessment.rules, assessment.review, assessment.risk)
    blockers: list[str] = []
    if assessment.rules <= 2:
        blockers.append("Las reglas del proceso todavía no están suficientemente claras.")
    if assessment.review <= 2:
        blockers.append("El resultado no parece fácil de revisar sin experiencia especializada.")
    if assessment.risk == "alto":
        blockers.append("El nivel de riesgo exige mantener decisiones y controles bajo responsabilidad humana.")
    if not blockers:
        blockers.append("No aparece un bloqueo estructural en esta primera revisión.")
    result = {
        "area": assessment.area,
        "process": assessment.process.strip(),
        "score": total,
        "max_score": 30,
        "score_percent": round(total / 30, 2),
        "readiness_label": label,
        "ai_role": role,
        "explanation": explanation,
        "blockers": blockers,
        "next_step": _next_step(role, assessment.task_types),
        "goal_focus": _goal_focus(assessment.goal),
        "task_types": list(assessment.task_types),
        "risk": assessment.risk,
        "goal": assessment.goal.strip(),
        "disclaimer": "Orientación educativa basada en tus respuestas. No sustituye un diagnóstico de un proceso real.",
    }
    result["area_analysis"] = _area_analysis(assessment.area, assessment.area_details, role)
    if assessment.area == "Ventas":
        result["sales_analysis"] = result["area_analysis"]
    return result
