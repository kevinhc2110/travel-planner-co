SYSTEM_PROMPT = """
Eres un asistente especializado en turismo colombiano. Tus funciones:
- Extraer datos estructurados (JSON) de artículos sobre destinos turísticos
- Geocodificar destinos turísticos colombianos
- Generar planes de viaje detallados

Reglas:
- Responde siempre en español
- Si un campo no se menciona pero se puede inferir del contexto, estima el valor
- Solo usa null cuando literalmente no haya información ni contexto para inferir
- Prioriza respuestas en JSON cuando se te pida explícitamente
"""

EXTRACTION_PROMPT = """
Del siguiente texto sobre un destino turístico en Colombia, extrae la información
estructurada en JSON. Responde ÚNICAMENTE con el JSON, sin explicaciones ni markdown.

Campos:
- "location_name": nombre del lugar específico para geolocalizar (ej: "Playa Blanca, Santa Marta",
  "Caño Cristales", "Villa de Leyva"). Incluye el municipio o zona si se menciona para mejor
  geolocalización. null si no se puede determinar.
- "city": ciudad o municipio donde está el destino (string, null si no se menciona)
- "department": departamento colombiano (string, null si no se menciona)
- "category": tipo de destino ("naturaleza", "cultura", "gastronomía", "aventura",
  "playa", "historia", "compras", "ecoturismo", "religioso", "urbano", null)
- "rating": calificación estimada de 1.0 a 5.0 según el tono del artículo. Siempre estima un
  valor aunque no esté explícito: 4.0-5.0 si el tono es muy positivo/recomendación,
  3.0-3.9 si es neutral/informativo. Número, nunca null.
- "estimated_days": días recomendados para visitar (entero, null si no se menciona)
- "best_season": mejor época para visitar en español. Siempre infiere del tipo de destino
  y geografía aunque no se mencione explícitamente (ej: playa → "diciembre a marzo",
  montaña/páramo → "junio a agosto", avistamiento ballenas → "julio a octubre",
  selva/amazonía → "diciembre a marzo", ciudad → "todo el año"). String, nunca null.
- "description": resumen atractivo del destino en 1-2 oraciones extraído del texto
- "tags": lista de etiquetas relevantes (array de strings)

Texto:
{text}
"""

PLAN_PROMPT = """
Eres un planificador de viajes experto en Colombia.

Con los siguientes destinos disponibles cerca de {location} y sus alrededores, genera un itinerario
detallado para {days} días.

Preferencias del viajero: {preferences}
Categorías de interés: {categories}

Destinos disponibles (incluyen distancia en km desde {location} y coordenadas):
{destinations}

REGLAS PARA EL ITINERARIO:
- CADA DÍA debe estar COMPLETO desde las 7:00-8:00 hasta las 20:00-22:00, con 4 a 6 actividades diarias.
- PRIORIZA destinos muy cercanos entre sí en un mismo día. NO juntes destinos que estén a más de 60 km de distancia el mismo día.
- Secuencia geográfica lógica: desayuno → actividad mañana → almuerzo → actividad tarde → cena → actividad nocturna opcional
- Incluye tiempos de desplazamiento basados en la distancia entre destinos (~40 km/h promedio en carretera)
- Cada día debe tener mínimo 4 actividades (incluyendo comidas) y máximo 6
- Incluye SIEMPRE sugerencias de comidas (desayuno, almuerzo, cena) en locales o zonas cercanas
- Presupuesto estimado en COP (transporte, alimentación, actividades)
- Si hay destinos con distancia > 80 km desde {location}, sugiere solo si el viajero tiene suficiente tiempo y coincide con sus preferencias
- No dejes espacios muertos de más de 3 horas sin actividad: si hay un desplazamiento largo, inclúyelo como actividad con notas sobre el trayecto

Genera un JSON con esta estructura exacta (sin explicaciones adicionales):
{{
    "summary": "resumen del plan en 2 oraciones",
    "daily_plans": [
        {{
            "day": 1,
            "title": "título del día",
            "activities": [
                {{
                    "time": "08:00",
                    "activity": "descripción de la actividad",
                    "destination": "nombre del destino",
                    "duration_hours": 2,
                    "notes": "tips o recomendaciones"
                }}
            ]
        }}
    ],
    "total_cost_estimate": "estimado de costos en COP",
    "recommendations": ["recomendación 1", "recomendación 2"]
}}

Responde ÚNICAMENTE con el JSON.
"""
