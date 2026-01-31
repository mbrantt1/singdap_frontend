import json
import re
import os

# Config paths
base_file = 'src/config/formularios/rat.json'
output_file = 'src/config/formularios/rat_institucional.json'

# Load base config
with open(base_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Update Form Settings
config["title_new"] = "RAT_Institucional - Nuevo Registro"
config["title_edit"] = "RAT_Institucional - Editar Registro"

# Define Institucional Sections
sections = [
    {
        "title": "2. Finalidad y Licitud",
        "description": "Detalle del propósito y base legal del tratamiento.",
        "fields": [
            {
                "key": "finalidad_tratamiento_inst",
                "label": "Finalidad del tratamiento",
                "description": "Describa el motivo o propósito específico por el que se recolectan y tratan los datos.",
                "type": "textarea",
                "required": True
            },
            {
                "key": "base_licitud_inst",
                "label": "Base de licitud",
                "description": "Indique el fundamento legal que habilita el tratamiento.",
                "type": "combo_static",
                "options": [
                    {"id": "ley", "nombre": "Ley"},
                    {"id": "decreto", "nombre": "Decreto"},
                    {"id": "reglamento", "nombre": "Reglamento"},
                    {"id": "consentimiento", "nombre": "Consentimiento"},
                    {"id": "contrato", "nombre": "Contrato"},
                    {"id": "interes_legitimo", "nombre": "Interés legítimo"},
                    {"id": "otra", "nombre": "Otra (especifique)"}
                ],
                "required": True
            }
        ]
    },
    {
        "title": "3. Datos Personales Recolectados",
        "description": "Categorización de los datos tratados.",
        "fields": [
            {
                "key": "categorias_datos_inst",
                "label": "Categorías de datos",
                "description": "Seleccione qué tipos de datos se recolectan.",
                "type": "combo_static",
                "multiple": True,
                "options": [
                    {"id": "identificacion", "nombre": "Datos de identificación (nombre, RUT, etc.)"},
                    {"id": "contacto", "nombre": "Datos de contacto"},
                    {"id": "patrimoniales", "nombre": "Datos patrimoniales"},
                    {"id": "salud", "nombre": "Datos de salud"},
                    {"id": "biometricos", "nombre": "Datos biométricos"},
                    {"id": "sensibles", "nombre": "Otros datos sensibles"}
                ],
                "required": True
            },
            {
                "key": "poblaciones_vulnerables_inst",
                "label": "Poblaciones especiales o grupos vulnerables",
                "description": "Indique si el tratamiento incluye datos de poblaciones especiales.",
                "type": "combo_static",
                "options": [
                    {"id": "no_aplica", "nombre": "No aplica"},
                    {"id": "nna", "nombre": "Niños, Niñas y Adolescentes (NNA)"},
                    {"id": "adultos_mayores", "nombre": "Adultos mayores"},
                    {"id": "pueblos_originarios", "nombre": "Pueblos originarios"},
                    {"id": "discapacidad", "nombre": "Personas con discapacidad"},
                    {"id": "datos_sensibles", "nombre": "Datos sensibles (especificar)"}
                ],
                "required": True
            },
            {
                "key": "detalle_datos_sensibles_inst",
                "label": "Tipos de datos sensibles",
                "description": "Especifique las categorías de datos sensibles tratadas.",
                "type": "combo_static",
                "multiple": True,
                "options": [
                    {"id": "origen_racial", "nombre": "Origen racial o étnico"},
                    {"id": "opiniones_politicas", "nombre": "Opiniones políticas"},
                    {"id": "convicciones_religiosas", "nombre": "Convicciones religiosas o filosóficas"},
                    {"id": "afiliacion_sindical", "nombre": "Afiliación sindical"},
                    {"id": "datos_geneticos", "nombre": "Datos genéticos"},
                    {"id": "datos_biometricos", "nombre": "Datos biométricos para identificación única"},
                    {"id": "datos_salud", "nombre": "Datos relativos a la salud"},
                    {"id": "vida_sexual", "nombre": "Vida sexual"},
                    {"id": "orientacion_sexual", "nombre": "Orientación sexual"}
                ],
                "visible_if": {
                    "field": "poblaciones_vulnerables_inst",
                    "value": "datos_sensibles"
                },
                "required": True # Technically required if visible, but standard validation might trip if hidden. Logic needs to handle this.
            }
        ]
    },
    {
        "title": "4. Origen de los datos",
        "description": "Fuente y mecanismo de recolección.",
        "fields": [
            {
                "key": "fuente_obtencion_inst",
                "label": "Fuente de obtención",
                "description": "Indique de dónde provienen los datos.",
                "type": "combo_static",
                "options": [
                    {"id": "titular", "nombre": "Titular (directamente)"},
                    {"id": "publico", "nombre": "Fuente accesible al público"},
                    {"id": "transferencia", "nombre": "Transferencia de otro organismo"},
                    {"id": "privada", "nombre": "Base de datos privada"},
                    {"id": "otro", "nombre": "Otro"}
                ],
                "required": True
            },
            {
                "key": "mecanismo_recoleccion_inst",
                "label": "Mecanismo de recolección",
                "description": "¿Cómo se capturan los datos? (Formulario web, papel, API, etc.)",
                "type": "text",
                "required": True
            }
        ]
    },
    {
        "title": "5. Transferencias y Destinatarios",
        "description": "Cesión de datos a terceros y flujos internacionales.",
        "fields": [
            {
                "key": "realiza_transferencias_inst",
                "label": "¿Realiza transferencias?",
                "description": "Indique si comparte datos con terceros.",
                "type": "combo_static",
                "options": [
                    {"id": "si", "nombre": "Si"},
                    {"id": "no", "nombre": "No"}
                ],
                "required": True
            },
            {
                "key": "destinatarios_inst",
                "label": "Destinatarios",
                "description": "Identifique quién recibe los datos.",
                "type": "textarea",
                "visible_if": {
                    "field": "realiza_transferencias_inst",
                    "value": "si"
                },
                "required": True
            },
            {
                "key": "transferencias_internacionales_inst",
                "label": "Transferencias internacionales",
                "description": "¿Los datos salen del país?",
                "type": "combo_static",
                "options": [
                    {"id": "si", "nombre": "Si"},
                    {"id": "no", "nombre": "No"}
                ],
                "required": True
            },
            {
                "key": "pais_destino_inst",
                "label": "País destino",
                "description": "Indique país(es) de destino.",
                "type": "text",
                "visible_if": {
                    "field": "transferencias_internacionales_inst",
                    "value": "si"
                },
                "required": True
            }
        ]
    },
    {
        "title": "6. Medidas de Seguridad",
        "description": "Resguardos técnicos y organizativos.",
        "fields": [
            {
                "key": "medidas_tecnicas_inst",
                "label": "Medidas técnicas",
                "description": "Cifrado, control de acceso, logs, etc.",
                "type": "textarea",
                "required": True
            },
            {
                "key": "medidas_organizativas_inst",
                "label": "Medidas organizativas",
                "description": "Políticas, capacitación, NDA, etc.",
                "type": "textarea",
                "required": True
            }
        ]
    },
    {
        "title": "7. Plazos de Conservación",
        "description": "Ciclo de vida y disposición final.",
        "fields": [
            {
                "key": "plazo_retencion_inst",
                "label": "Plazo de retención",
                "description": "¿Cuánto tiempo se guardarán los datos?",
                "type": "text",
                "required": True
            },
            {
                "key": "disposicion_final_inst",
                "label": "Disposición final",
                "description": "¿Qué ocurre al finalizar el plazo?",
                "type": "combo_static",
                "options": [
                    {"id": "eliminacion", "nombre": "Eliminación"},
                    {"id": "anonimizacion", "nombre": "Anonimización"},
                    {"id": "bloqueo", "nombre": "Bloqueo"},
                    {"id": "historico", "nombre": "Archivo Histórico"}
                ],
                "required": True
            }
        ]
    }
]

# Insert Sections
for i, section in enumerate(sections):
    config["sections"].insert(2 + i, section)

# Renumber sections (starting from 0)
for i, section in enumerate(config["sections"]):
    title_parts = section["title"].split('.', 1)
    if len(title_parts) >= 2:
        text = title_parts[1].strip()
    else:
        text = section["title"]
    section["title"] = f"{i}. {text}"

# Save
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("RAT_Institucional generated successfully.")
