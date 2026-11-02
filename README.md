# LYVIRA · Diagnóstico express de procesos

Aplicación Streamlit para realizar una primera evaluación educativa de un proceso de trabajo y detectar qué parte podría beneficiarse de una mejora asistida por IA.

La demo funciona con reglas locales: no requiere modelos externos, claves, cuentas privadas ni servicios de terceros. No solicita datos personales, no almacena leads y genera el diagnóstico y el PDF durante la sesión del usuario.

## Funcionalidades

- Cuestionario guiado sobre un proceso concreto.
- Evaluación de frecuencia, esfuerzo, repetición, reglas, revisión, impacto y riesgo.
- Recomendación del papel adecuado para la IA.
- Orientaciones específicas por área.
- Generación y previsualización de una ficha PDF.
- Descarga del resultado en PDF y JSON.

## Requisitos

- Python 3.10 o posterior.
- `pip`.

## Ejecución local

Crear y activar un entorno virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
py -m pip install -r requirements.txt
```

Iniciar la aplicación:

```powershell
py -m streamlit run public_demo.py --server.port 8501
```

Abrir `http://localhost:8501`.

## Docker

```bash
docker compose up --build
```

Abrir `http://localhost:8501`. Para detenerla, ejecutar `docker compose down`.

## Pruebas

```powershell
py -m unittest discover -s tests -v
```

## Privacidad

Esta versión no solicita nombre ni correo, no almacena información personal, no sincroniza contactos, no envía emails, no requiere credenciales y no llama a modelos externos. Evita introducir información confidencial o datos personales. El resultado es orientativo y no sustituye un análisis profesional.

## Marca

LYVIRA es un laboratorio de IA aplicada. Más información en [lyvira.com](https://lyvira.com).