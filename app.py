"""
EatWell - Personalized Nutrition App
A beautiful, interactive prototype for personalized nutrition planning with health equity focus.
"""

import streamlit as st
from typing import Optional
import os

# OpenAI import (optional - for AI chatbot)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Google Gemini import (optional - free AI chatbot)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Map visualization imports (optional)
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Geolocation support (optional)
try:
    from streamlit_js_eval import get_geolocation
    GEOLOCATION_AVAILABLE = True
except ImportError:
    GEOLOCATION_AVAILABLE = False

# Import app modules
from user_context import (
    UserContext, Financials, Logistics, MedicalHistory, LabResults,
    Demographics, create_sample_user
)
from bio_analyzer import analyze_lab_data, NutrientPriorityList
from resource_locator import resource_locator, ResourceMap, StoreType, get_base_coordinates
from shopping_planner import (
    generate_shopping_list, ShoppingList, ShoppingPriority,
    get_item_explanation
)

# Page config
st.set_page_config(
    page_title="EatWell - Personalized Nutrition",
    page_icon="🥕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished look
st.markdown("""
<style>
    /* Color Palette:
       Light Orange: #ffd09b
       Orange: #ec813b
       Light Green: #d1d69d
       Dark Green: #4f7e52
    */
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #4f7e52;
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        color: #666;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffd09b 0%, #d1d69d 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .priority-critical { 
        background-color: #ffebee; 
        border-left: 4px solid #c62828;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .priority-high { 
        background-color: #ffd09b; 
        border-left: 4px solid #ec813b;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .priority-moderate { 
        background-color: #ffefd6; 
        border-left: 4px solid #ec813b;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .priority-optional { 
        background-color: #d1d69d; 
        border-left: 4px solid #4f7e52;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .store-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(79,126,82,0.15);
        margin: 0.5rem 0;
        border: 1px solid #d1d69d;
    }
    .nutrient-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        background-color: #d1d69d;
        color: #4f7e52;
    }
    .explanation-box {
        background: linear-gradient(135deg, #ffffff 0%, #d1d69d40 100%);
        border: 1px solid #d1d69d;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .free-badge {
        background-color: #4f7e52;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .snap-badge {
        background-color: #ec813b;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .edu-card {
        background: linear-gradient(135deg, #ffd09b40 0%, #d1d69d60 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #4f7e52;
    }
    .edu-card h4 {
        color: #4f7e52;
        margin-bottom: 0.5rem;
    }
    .simple-explain {
        background: linear-gradient(135deg, #ffd09b40 0%, #ffd09b80 100%);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid #ffd09b;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .simple-explain strong {
        color: #4f7e52;
    }
    .glossary-term {
        background: #d1d69d;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4f7e52;
    }
    /* Streamlit overrides for cohesive theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #4f7e52;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        min-width: 140px;
        flex-grow: 1;
        border: 1px solid #d1d69d;
        border-bottom: none;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #d1d69d40;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f7e52 !important;
        color: white !important;
        border-color: #4f7e52 !important;
    }
    /* Wider content area for main tabs */
    .stMainBlockContainer {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* Make tab content panels wider */
    .stTabs [data-baseweb="tab-panel"] {
        width: 100%;
        padding: 1rem 0;
    }
    section[data-testid="stSidebar"] + section .stTabs {
        width: 100%;
    }
    .stButton>button {
        background-color: #ec813b;
        color: white;
        border: none;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #4f7e52;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        color: #4f7e52;
    }
    div[data-testid="stMetricDelta"] {
        color: #ec813b;
    }
    /* Feedback link - top right corner */
    .feedback-link {
        position: fixed;
        top: 0.75rem;
        right: 1rem;
        z-index: 1000;
        font-size: 0.9rem;
    }
    .feedback-link a {
        color: #4f7e52;
        text-decoration: none;
        padding: 0.4rem 0.8rem;
        background-color: #ffd09b;
        border-radius: 8px;
        transition: background-color 0.2s ease;
    }
    .feedback-link a:hover {
        background-color: #ec813b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Feedback link - appears on all pages
st.markdown(
    '<div class="feedback-link"><a href="https://forms.gle/yZB7c3rqnhvhgDBw9" target="_blank">Share your feedback here 🥕</a></div>',
    unsafe_allow_html=True
)


# =============================================================================
# TRANSLATIONS - Spanish language support
# =============================================================================

TRANSLATIONS = {
    # App header and navigation
    "app_title": {"en": "EatWell", "es": "ComesBien"},
    "personalized_nutrition": {"en": "Personalized Nutrition", "es": "Nutrición Personalizada"},
    "personalized_nutrition_planning": {"en": "Personalized nutrition planning for everyone.", "es": "Planificación nutricional personalizada para todos."},
    
    # Main tabs
    "my_plan": {"en": "My Plan", "es": "Mi Plan"},
    "where_to_shop": {"en": "Where to Shop", "es": "Dónde Comprar"},
    "why_this": {"en": "Why This?", "es": "¿Por Qué Esto?"},
    "help": {"en": "Help", "es": "Ayuda"},
    
    # Sidebar
    "start_over": {"en": "Start Over", "es": "Empezar de Nuevo"},
    "update_plan": {"en": "Update Plan", "es": "Actualizar Plan"},
    "adjust_budget": {"en": "Adjust Budget ($)", "es": "Ajustar Presupuesto ($)"},
    "spanish_mode": {"en": "Español", "es": "Español"},
    
    # Welcome page
    "budget_aware": {"en": "Budget-Aware", "es": "Consciente del Presupuesto"},
    "works_with_snap_wic": {"en": "Works with SNAP/WIC", "es": "Funciona con SNAP/WIC"},
    "science_based": {"en": "Science-Based", "es": "Basado en Ciencia"},
    "personalized_to_you": {"en": "Personalized to you", "es": "Personalizado para ti"},
    "location_smart": {"en": "Location-Smart", "es": "Ubicación Inteligente"},
    "finds_nearby_stores": {"en": "Finds nearby stores", "es": "Encuentra tiendas cercanas"},
    "quick_demo": {"en": "Quick Demo (Load Sample Data)", "es": "Demo Rápida (Cargar Datos de Ejemplo)"},
    
    # Wizard steps
    "step_of": {"en": "Step", "es": "Paso"},
    "of": {"en": "of", "es": "de"},
    "budget_location": {"en": "Budget & Location", "es": "Presupuesto y Ubicación"},
    "lets_start_basics": {"en": "Let's start with the basics to find affordable options near you.", "es": "Comencemos con lo básico para encontrar opciones económicas cerca de ti."},
    "your_name": {"en": "Your Name (optional)", "es": "Tu Nombre (opcional)"},
    "enter_your_name": {"en": "Enter your name", "es": "Ingresa tu nombre"},
    "weekly_grocery_budget": {"en": "Weekly Grocery Budget ($)", "es": "Presupuesto Semanal ($)"},
    "benefits": {"en": "Benefits", "es": "Beneficios"},
    "zip_code": {"en": "ZIP Code", "es": "Código Postal"},
    "transportation": {"en": "Transportation", "es": "Transporte"},
    "car_access": {"en": "Car Access", "es": "Acceso a Auto"},
    "public_transit": {"en": "Public Transit", "es": "Transporte Público"},
    "grocery_trips_week": {"en": "Grocery Trips/Week", "es": "Viajes al Supermercado/Semana"},
    "next": {"en": "Next", "es": "Siguiente"},
    "back": {"en": "Back", "es": "Atrás"},
    
    # Health info step
    "health_information": {"en": "Health Information", "es": "Información de Salud"},
    "health_needs_optional": {"en": "Help us understand your health needs (all optional).", "es": "Ayúdanos a entender tus necesidades de salud (todo opcional)."},
    "current_symptoms": {"en": "Current Symptoms", "es": "Síntomas Actuales"},
    "family_health_history": {"en": "Family Health History", "es": "Historial de Salud Familiar"},
    "food_allergies": {"en": "Food Allergies & Intolerances", "es": "Alergias e Intolerancias Alimentarias"},
    "skip_to_results": {"en": "Skip to Results", "es": "Saltar a Resultados"},
    
    # Lab results step
    "lab_results_optional": {"en": "Lab Results (Optional)", "es": "Resultados de Laboratorio (Opcional)"},
    "lab_results_help": {"en": "If you have recent bloodwork, entering it makes recommendations more precise.", "es": "Si tienes análisis de sangre recientes, ingresarlos hace las recomendaciones más precisas."},
    "no_lab_results": {"en": "No lab results? That's okay! Click 'Generate My Plan' to skip this step.", "es": "¿Sin resultados de laboratorio? ¡Está bien! Haz clic en 'Generar Mi Plan' para saltar este paso."},
    "vitamin_levels": {"en": "Vitamin Levels", "es": "Niveles de Vitaminas"},
    "health_markers": {"en": "Health Markers", "es": "Marcadores de Salud"},
    "genetic_markers": {"en": "Genetic Markers (from special tests)", "es": "Marcadores Genéticos (de pruebas especiales)"},
    "generate_my_plan": {"en": "Generate My Plan", "es": "Generar Mi Plan"},
    
    # Demographics (Step 1)
    "about_you": {"en": "About You (Optional)", "es": "Sobre Ti (Opcional)"},
    "age": {"en": "Age", "es": "Edad"},
    "biological_sex": {"en": "Biological Sex", "es": "Sexo Biológico"},
    "female": {"en": "Female", "es": "Femenino"},
    "male": {"en": "Male", "es": "Masculino"},
    "prefer_not_to_say": {"en": "Prefer not to say", "es": "Prefiero no decir"},
    "height": {"en": "Height", "es": "Altura"},
    "feet": {"en": "ft", "es": "pies"},
    "inches": {"en": "in", "es": "pulg"},
    "weight": {"en": "Weight (lbs)", "es": "Peso (lbs)"},
    "activity_level": {"en": "Activity Level", "es": "Nivel de Actividad"},
    "not_specified": {"en": "Not specified", "es": "No especificado"},
    "sedentary": {"en": "Sedentary", "es": "Sedentario"},
    "lightly_active": {"en": "Lightly Active", "es": "Ligeramente Activo"},
    "moderately_active": {"en": "Moderately Active", "es": "Moderadamente Activo"},
    "very_active": {"en": "Very Active", "es": "Muy Activo"},
    
    # Demographics (Step 2)
    "pregnancy_status": {"en": "Pregnancy/Nursing Status", "es": "Estado de Embarazo/Lactancia"},
    "not_applicable": {"en": "Not applicable", "es": "No aplica"},
    "pregnant": {"en": "Pregnant", "es": "Embarazada"},
    "breastfeeding": {"en": "Breastfeeding", "es": "Lactando"},
    "trying_to_conceive": {"en": "Trying to Conceive", "es": "Intentando Concebir"},
    "dietary_preference": {"en": "Dietary Preference", "es": "Preferencia Dietética"},
    "no_preference": {"en": "No specific preference", "es": "Sin preferencia específica"},
    "vegetarian": {"en": "Vegetarian", "es": "Vegetariano"},
    "vegan": {"en": "Vegan", "es": "Vegano"},
    "pescatarian": {"en": "Pescatarian", "es": "Pescetariano"},
    "keto": {"en": "Keto/Low-Carb", "es": "Keto/Bajo en Carbohidratos"},
    "mediterranean": {"en": "Mediterranean", "es": "Mediterránea"},
    "health_goals": {"en": "Health Goals", "es": "Metas de Salud"},
    "weight_loss": {"en": "Weight Loss", "es": "Pérdida de Peso"},
    "weight_gain": {"en": "Weight Gain", "es": "Aumento de Peso"},
    "maintain_weight": {"en": "Maintain Weight", "es": "Mantener Peso"},
    "build_muscle": {"en": "Build Muscle", "es": "Desarrollar Músculo"},
    "improve_energy": {"en": "Improve Energy", "es": "Mejorar Energía"},
    "better_sleep": {"en": "Better Sleep", "es": "Mejor Sueño"},
    
    # Dashboard
    "welcome_back": {"en": "Welcome back", "es": "Bienvenido de nuevo"},
    "heres_your_plan": {"en": "Here's your personalized EatWell nutrition plan.", "es": "Aquí está tu plan de nutrición personalizado."},
    "weekly_budget": {"en": "Weekly Budget", "es": "Presupuesto Semanal"},
    "left": {"en": "left", "es": "restante"},
    "over_budget": {"en": "Over budget", "es": "Sobre presupuesto"},
    "priority_nutrients": {"en": "Priority Nutrients", "es": "Nutrientes Prioritarios"},
    "critical": {"en": "critical", "es": "críticos"},
    "nearby_stores": {"en": "Nearby Stores", "es": "Tiendas Cercanas"},
    "pantries": {"en": "pantries", "es": "despensas"},
    "total_cost": {"en": "Total Cost", "es": "Costo Total"},
    "transport": {"en": "transport", "es": "transporte"},
    "no_transport_cost": {"en": "no transport cost", "es": "sin costo de transporte"},
    
    # Shopping list
    "your_shopping_list": {"en": "Your Curated Shopping List", "es": "Tu Lista de Compras Personalizada"},
    "total_budget_used": {"en": "Total Budget Used", "es": "Presupuesto Total Usado"},
    "food_cost": {"en": "Food Cost", "es": "Costo de Alimentos"},
    "transport_cost": {"en": "Transport Cost", "es": "Costo de Transporte"},
    "free": {"en": "Free", "es": "Gratis"},
    "remaining": {"en": "Remaining", "es": "Restante"},
    "over": {"en": "Over", "es": "Sobre"},
    "transport_breakdown": {"en": "Transportation Cost Breakdown", "es": "Desglose de Costos de Transporte"},
    "round_trip": {"en": "round trip", "es": "viaje redondo"},
    "tip_combine_trips": {"en": "Tip: Combine trips to save on transportation costs!", "es": "Consejo: ¡Combina viajes para ahorrar en transporte!"},
    "snap_applied": {"en": "SNAP Applied", "es": "SNAP Aplicado"},
    "wic_applied": {"en": "WIC Applied", "es": "WIC Aplicado"},
    "from_food_pantry": {"en": "From Food Pantry (FREE)", "es": "De la Despensa de Alimentos (GRATIS)"},
    "items_to_purchase": {"en": "Items to Purchase", "es": "Artículos para Comprar"},
    "critical_priority": {"en": "Critical", "es": "Crítico"},
    "high_priority": {"en": "High Priority", "es": "Alta Prioridad"},
    "moderate_priority": {"en": "Moderate", "es": "Moderado"},
    "optional_priority": {"en": "Optional", "es": "Opcional"},
    "nutrients": {"en": "Nutrients", "es": "Nutrientes"},
    "suggested": {"en": "Suggested", "es": "Sugerido"},
    "any_store": {"en": "Any store", "es": "Cualquier tienda"},
    
    # Nutrient analysis
    "your_nutrient_analysis": {"en": "Your Nutrient Analysis", "es": "Tu Análisis de Nutrientes"},
    "your_biomarkers": {"en": "Your Biomarkers", "es": "Tus Biomarcadores"},
    "prioritized_nutrient_needs": {"en": "Prioritized Nutrient Needs", "es": "Necesidades de Nutrientes Priorizadas"},
    "why_matters_for_you": {"en": "Why this matters for you:", "es": "Por qué esto te importa:"},
    "related_markers": {"en": "Related markers", "es": "Marcadores relacionados"},
    "best_food_sources": {"en": "Best food sources", "es": "Mejores fuentes de alimentos"},
    
    # Store finder
    "nearby_food_resources": {"en": "Nearby Food Resources", "es": "Recursos Alimentarios Cercanos"},
    "showing_results_for": {"en": "Showing results for ZIP", "es": "Mostrando resultados para código postal"},
    "mobility": {"en": "Mobility", "es": "Movilidad"},
    "store_locations_map": {"en": "Store Locations Map", "es": "Mapa de Ubicación de Tiendas"},
    "use_current_location": {"en": "Use my current location", "es": "Usar mi ubicación actual"},
    "location_not_saved": {"en": "Your location is used only for the map and is NOT saved or stored.", "es": "Tu ubicación solo se usa para el mapa y NO se guarda."},
    "getting_location": {"en": "Getting your location...", "es": "Obteniendo tu ubicación..."},
    "using_current_location": {"en": "Using your current location (not saved)", "es": "Usando tu ubicación actual (no guardada)"},
    "could_not_get_location": {"en": "Could not get location. Make sure location permissions are enabled.", "es": "No se pudo obtener la ubicación. Asegúrate de que los permisos de ubicación estén habilitados."},
    "food_pantries_free": {"en": "Food Pantries (FREE)", "es": "Despensas de Alimentos (GRATIS)"},
    "snap_authorized_stores": {"en": "SNAP-Authorized Stores", "es": "Tiendas Autorizadas SNAP"},
    "all_accessible_stores": {"en": "All Accessible Stores", "es": "Todas las Tiendas Accesibles"},
    "score": {"en": "Score", "es": "Puntuación"},
    "store": {"en": "Store", "es": "Tienda"},
    "type": {"en": "Type", "es": "Tipo"},
    "distance": {"en": "Distance", "es": "Distancia"},
    "travel": {"en": "Travel", "es": "Viaje"},
    "price": {"en": "Price", "es": "Precio"},
    
    # Why section
    "ask_why": {"en": "Ask Why", "es": "Pregunta Por Qué"},
    "understand_connection": {"en": "Understand the connection between your health markers and food recommendations.", "es": "Entiende la conexión entre tus marcadores de salud y las recomendaciones de alimentos."},
    "select_item_explain": {"en": "Select an item to understand why it was recommended:", "es": "Selecciona un artículo para entender por qué fue recomendado:"},
    "generate_list_first": {"en": "Generate a shopping list first to see explanations.", "es": "Genera una lista de compras primero para ver explicaciones."},
    "biological_connection": {"en": "Biological Connection", "es": "Conexión Biológica"},
    "nutrient_profile": {"en": "Nutrient Profile", "es": "Perfil de Nutrientes"},
    "this_food_provides": {"en": "This food provides", "es": "Este alimento proporciona"},
    "connected_to_symptoms": {"en": "Connected to your symptoms", "es": "Conectado a tus síntomas"},
    "nutrient_deep_dive": {"en": "Nutrient Deep Dive", "es": "Profundización en Nutrientes"},
    "select_nutrient_learn": {"en": "Select a nutrient to learn more:", "es": "Selecciona un nutriente para aprender más:"},
    "priority_level": {"en": "Priority Level", "es": "Nivel de Prioridad"},
    "why_it_matters": {"en": "Why it matters", "es": "Por qué importa"},
    
    # Learn section
    "learn": {"en": "Learn", "es": "Aprender"},
    "understanding_your_health": {"en": "Understanding Your Health", "es": "Entendiendo Tu Salud"},
    "health_literacy_intro": {"en": "We believe everyone deserves to understand their health. Here's what these terms mean in plain language.", "es": "Creemos que todos merecen entender su salud. Esto es lo que significan estos términos en lenguaje sencillo."},
    "terms_relevant_to_you": {"en": "Terms Relevant to You", "es": "Términos Relevantes para Ti"},
    "based_on_profile": {"en": "Based on your health profile, here are the most important concepts to understand:", "es": "Basado en tu perfil de salud, estos son los conceptos más importantes que debes entender:"},
    "what_is_it": {"en": "What is it?", "es": "¿Qué es?"},
    "why_matters_for_you_learn": {"en": "Why it matters for you:", "es": "Por qué te importa:"},
    "foods_that_help": {"en": "Foods that help", "es": "Alimentos que ayudan"},
    "understanding_symptoms": {"en": "Understanding Your Symptoms", "es": "Entendiendo Tus Síntomas"},
    "symptoms_explanation": {"en": "Here's what your symptoms might mean and how food can help:", "es": "Esto es lo que podrían significar tus síntomas y cómo la comida puede ayudar:"},
    "what_it_means": {"en": "What it means", "es": "Qué significa"},
    "common_causes": {"en": "Common causes", "es": "Causas comunes"},
    "foods_can_help": {"en": "Foods that can help", "es": "Alimentos que pueden ayudar"},
    "health_glossary": {"en": "Health Glossary", "es": "Glosario de Salud"},
    "browse_health_terms": {"en": "Browse all health terms explained in plain language", "es": "Explora todos los términos de salud explicados en lenguaje sencillo"},
    "search_term": {"en": "Search for a term:", "es": "Buscar un término:"},
    "eg_search": {"en": "e.g., B12, inflammation, SNAP", "es": "ej., B12, inflamación, SNAP"},
    "no_terms_found": {"en": "No terms found matching", "es": "No se encontraron términos que coincidan con"},
    "quick_tips": {"en": "Quick Tips for Healthy Eating on a Budget", "es": "Consejos Rápidos para Comer Saludable con Presupuesto"},
    "shopping_smart": {"en": "Shopping Smart:", "es": "Compras Inteligentes:"},
    "using_food_assistance": {"en": "Using Food Assistance:", "es": "Usando Asistencia Alimentaria:"},
    "cooking_tips": {"en": "Cooking Tips:", "es": "Consejos de Cocina:"},
    "reading_your_body": {"en": "Reading Your Body:", "es": "Escucha a Tu Cuerpo:"},
    
    # Chatbot
    "ask_nutrition_assistant": {"en": "Ask Your Nutrition Assistant", "es": "Pregunta a Tu Asistente de Nutrición"},
    "ai_settings": {"en": "AI Settings", "es": "Configuración de IA"},
    "ai_provider": {"en": "AI Provider", "es": "Proveedor de IA"},
    "type_question_here": {"en": "Type your question here...", "es": "Escribe tu pregunta aquí..."},
    "ask_ai": {"en": "Ask AI", "es": "Pregunta a IA"},
    
    # Disclaimer
    "disclaimer": {"en": "This app provides nutrition education, not medical advice. Consult a healthcare provider for medical decisions.", "es": "Esta aplicación proporciona educación nutricional, no consejo médico. Consulta a un profesional de salud para decisiones médicas."},
    "full_disclaimer": {"en": "This app provides general nutrition information for educational purposes. It is not medical advice. Always consult with a healthcare provider for personalized medical guidance.", "es": "Esta aplicación proporciona información nutricional general con fines educativos. No es consejo médico. Siempre consulta con un profesional de salud para orientación médica personalizada."},
    
    # Symptoms
    "Fatigue": {"en": "Fatigue", "es": "Fatiga"},
    "Brain Fog": {"en": "Brain Fog", "es": "Niebla Mental"},
    "Joint Pain": {"en": "Joint Pain", "es": "Dolor Articular"},
    "Anxiety": {"en": "Anxiety", "es": "Ansiedad"},
    "Poor Sleep": {"en": "Poor Sleep", "es": "Mal Sueño"},
    "Digestive Issues": {"en": "Digestive Issues", "es": "Problemas Digestivos"},
    "Weak Immunity": {"en": "Weak Immunity", "es": "Inmunidad Débil"},
    "Headaches": {"en": "Headaches", "es": "Dolores de Cabeza"},
    "Skin Problems": {"en": "Skin Problems", "es": "Problemas de Piel"},
    "Muscle Cramps": {"en": "Muscle Cramps", "es": "Calambres Musculares"},
    "Mood Swings": {"en": "Mood Swings", "es": "Cambios de Humor"},
    "Hair Loss": {"en": "Hair Loss", "es": "Pérdida de Cabello"},
    "Cold Hands/Feet": {"en": "Cold Hands/Feet", "es": "Manos/Pies Fríos"},
    "Dizziness": {"en": "Dizziness", "es": "Mareos"},
    "Shortness of Breath": {"en": "Shortness of Breath", "es": "Falta de Aliento"},
    
    # Family history
    "Diabetes": {"en": "Diabetes", "es": "Diabetes"},
    "Heart Disease": {"en": "Heart Disease", "es": "Enfermedad Cardíaca"},
    "Hypertension": {"en": "Hypertension", "es": "Hipertensión"},
    "Cancer": {"en": "Cancer", "es": "Cáncer"},
    "Obesity": {"en": "Obesity", "es": "Obesidad"},
    "Thyroid Issues": {"en": "Thyroid Issues", "es": "Problemas de Tiroides"},
    "Alzheimer's/Dementia": {"en": "Alzheimer's/Dementia", "es": "Alzheimer/Demencia"},
    "Autoimmune Disease": {"en": "Autoimmune Disease", "es": "Enfermedad Autoinmune"},
    "Mental Health Conditions": {"en": "Mental Health Conditions", "es": "Condiciones de Salud Mental"},
    
    # Allergies
    "Gluten": {"en": "Gluten", "es": "Gluten"},
    "Dairy": {"en": "Dairy", "es": "Lácteos"},
    "Shellfish": {"en": "Shellfish", "es": "Mariscos"},
    "Tree Nuts": {"en": "Tree Nuts", "es": "Frutos Secos"},
    "Peanuts": {"en": "Peanuts", "es": "Maní"},
    "Eggs": {"en": "Eggs", "es": "Huevos"},
    "Soy": {"en": "Soy", "es": "Soja"},
    "Fish": {"en": "Fish", "es": "Pescado"},
    "Corn": {"en": "Corn", "es": "Maíz"},
    "Sesame": {"en": "Sesame", "es": "Sésamo"},
    "Nightshades": {"en": "Nightshades", "es": "Solanáceas"},
    "Sulfites": {"en": "Sulfites", "es": "Sulfitos"},
    "Histamine": {"en": "Histamine", "es": "Histamina"},
    "FODMAPs": {"en": "FODMAPs", "es": "FODMAPs"},
    "Latex-Fruit": {"en": "Latex-Fruit", "es": "Látex-Frutas"},
}


def t(key: str, default: str = None) -> str:
    """Get translated text based on current language setting."""
    lang = "es" if st.session_state.get("spanish_mode", False) else "en"
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("en", default or key))
    return default or key


# =============================================================================
# HEALTH LITERACY CONTENT - Plain language explanations
# =============================================================================

HEALTH_GLOSSARY = {
    "MTHFR": {
        "simple": "A gene that helps your body use vitamins, especially folate (a B vitamin)",
        "detail": """MTHFR is like a factory worker in your body that converts folate into a usable form. Some people have gene variants that make this worker slower:

**Common MTHFR Mutations:**
• **C677T** - The most studied variant. Having one copy (heterozygous) reduces enzyme activity by ~35%. Having two copies (homozygous) reduces it by ~70%. This is the variant most associated with higher homocysteine levels.
• **A1298C** - Less impactful alone, but combined with C677T can significantly affect folate processing.
• **Compound heterozygous** (one C677T + one A1298C) - Similar effect to having two C677T copies.

**What this means for you:** If you have these variants, your body has a harder time converting regular folate into methylfolate (the active form). The solution? Eat more folate-rich foods or consider methylfolate supplements.

**How to check your MTHFR status:**
• **23andMe or AncestryDNA** - These consumer tests include MTHFR data in raw files (use free tools like Genetic Genie or Promethease to interpret)
• **Doctor-ordered test** - Ask your doctor for MTHFR genetic testing, especially if you have family history of heart disease, blood clots, or pregnancy complications
• **Specialized labs** - Labs like LabCorp, Quest, or specialty genetic testing companies offer MTHFR panels
• **Cost** - Consumer DNA tests: $99-199; Medical tests: $100-400 (often covered by insurance with medical necessity)""",
        "why_matters": "If you have an MTHFR variant, you may need MORE folate-rich foods than average. About 40% of people have at least one copy of C677T, so this is very common!",
        "food_connection": "spinach, lentils, asparagus, broccoli, avocado, fortified cereals"
    },
    "Methylation": {
        "simple": "A process your body uses to turn genes on/off and detoxify",
        "detail": "Think of methylation like light switches in your house. Your body is constantly flipping these switches to control which genes are active. Good methylation = smooth operation. Poor methylation = some lights stuck on or off, which can affect mood, energy, and health.",
        "why_matters": "Supporting methylation with the right nutrients helps your body run smoothly.",
        "food_connection": "eggs, leafy greens, beets"
    },
    "Vitamin B12": {
        "simple": "A vitamin needed for energy, brain function, and making red blood cells",
        "detail": "B12 is like fuel for your brain and blood cells. Without enough, you might feel tired, foggy, or weak. Your body can't make B12—you must get it from food (meat, eggs, fortified foods) or supplements.",
        "why_matters": "Low B12 is common and causes fatigue and brain fog. Many people don't get enough.",
        "food_connection": "eggs, sardines, fortified cereals, nutritional yeast"
    },
    "Vitamin D": {
        "simple": "The 'sunshine vitamin' that helps bones, immune system, and mood",
        "detail": "Your skin makes Vitamin D when you're in sunlight, but many people don't get enough sun (especially in winter or if you have darker skin). Low Vitamin D is linked to weak bones, getting sick often, and feeling down.",
        "why_matters": "Most people are low in Vitamin D without knowing it. It affects almost every part of your body.",
        "food_connection": "fortified milk, salmon, egg yolks, mushrooms"
    },
    "Iron": {
        "simple": "A mineral that carries oxygen in your blood",
        "detail": "Iron is like a delivery truck that carries oxygen to every cell in your body. Without enough iron, cells don't get the oxygen they need, making you feel exhausted, cold, or short of breath.",
        "why_matters": "Iron deficiency is the #1 nutritional deficiency worldwide, especially in women.",
        "food_connection": "spinach, lentils, beef, fortified cereals"
    },
    "CRP": {
        "simple": "A blood test that measures inflammation (swelling) in your body",
        "detail": "CRP (C-Reactive Protein) is like a smoke alarm for inflammation. When it's high, something in your body is irritated or fighting—even if you can't feel it. Chronic inflammation is linked to heart disease, diabetes, and many other conditions.",
        "why_matters": "High CRP means your body is stressed. Anti-inflammatory foods can help calm it down.",
        "food_connection": "berries, fatty fish, turmeric, leafy greens, olive oil"
    },
    "Homocysteine": {
        "simple": "An amino acid that can damage blood vessels when too high",
        "detail": "Homocysteine is a natural byproduct in your blood, but high levels scratch and damage your blood vessel walls—like sandpaper on a pipe. B vitamins (especially folate and B12) help keep it low.",
        "why_matters": "High homocysteine increases heart disease risk. B vitamins from food can lower it.",
        "food_connection": "leafy greens, eggs, fortified cereals"
    },
    "Fasting Glucose": {
        "simple": "Blood sugar level after not eating for 8+ hours",
        "detail": "This test shows how well your body manages sugar. High fasting glucose means your body is having trouble moving sugar from blood into cells—an early warning sign for diabetes.",
        "why_matters": "Catching high glucose early lets you make food changes before diabetes develops.",
        "food_connection": "fiber-rich foods: oats, beans, vegetables"
    },
    "Omega-3 Fatty Acids": {
        "simple": "Healthy fats that reduce inflammation and support brain health",
        "detail": "Omega-3s are like oil for a squeaky machine—they help everything run smoothly, especially your brain, heart, and joints. Most Americans don't get enough because we don't eat much fish.",
        "why_matters": "Omega-3s fight inflammation and support mental health. Very important for brain function.",
        "food_connection": "salmon, sardines, walnuts, flaxseed, chia seeds"
    },
    "SNAP": {
        "simple": "Government food assistance program (food stamps)",
        "detail": "SNAP (Supplemental Nutrition Assistance Program) provides money on an EBT card to buy groceries. It's accepted at most grocery stores and many farmers markets. There's no shame in using it—it's there to help.",
        "why_matters": "SNAP can significantly expand your food budget and access to healthy options.",
        "food_connection": "Most foods except hot prepared foods and alcohol"
    },
    "WIC": {
        "simple": "Nutrition program for pregnant women, new mothers, and young children",
        "detail": "WIC (Women, Infants, and Children) provides specific healthy foods plus nutrition education. It covers things like milk, eggs, whole grains, fruits, and vegetables.",
        "why_matters": "WIC ensures mothers and children get key nutrients during critical growth periods.",
        "food_connection": "milk, eggs, whole grain bread, fruits, vegetables, infant formula"
    },
    "Fiber": {
        "simple": "The part of plant foods your body can't digest—but it keeps you healthy!",
        "detail": "Fiber is like a broom for your insides. It sweeps through your digestive system, keeping things moving, feeding good gut bacteria, and helping control blood sugar. There are two types: soluble fiber (dissolves in water, lowers cholesterol) and insoluble fiber (adds bulk, prevents constipation).",
        "why_matters": "Most people only get half the fiber they need. Low fiber is linked to constipation, high cholesterol, and blood sugar problems.",
        "food_connection": "oats, beans, lentils, apples, berries, broccoli, whole grains"
    },
    "Protein": {
        "simple": "Building blocks your body needs to make muscles, skin, hormones, and more",
        "detail": "Protein is made of amino acids—like Lego pieces that your body rearranges to build and repair tissues. You need protein every day because your body can't store it. Complete proteins (from animal foods) have all the building blocks; plant proteins often need to be combined.",
        "why_matters": "Not getting enough protein can cause muscle loss, weakness, slow healing, and hair loss.",
        "food_connection": "eggs, chicken, fish, beans, lentils, tofu, Greek yogurt, nuts"
    },
    "Carbohydrates": {
        "simple": "Your body's main source of quick energy",
        "detail": "Carbs break down into glucose (sugar) that powers your brain and muscles. Not all carbs are equal: complex carbs (whole grains, vegetables) release energy slowly, while simple carbs (sugar, white bread) spike blood sugar fast. Choose complex carbs most of the time.",
        "why_matters": "Choosing the right carbs helps maintain steady energy and healthy blood sugar levels.",
        "food_connection": "whole grains (oats, brown rice), vegetables, fruits, beans, sweet potatoes"
    },
    "Calcium": {
        "simple": "A mineral that builds strong bones and teeth",
        "detail": "Calcium is the main building material for your skeleton. Your body also uses it for muscle movement, nerve signals, and heart rhythm. If you don't eat enough calcium, your body takes it from your bones, making them weaker over time.",
        "why_matters": "Low calcium over time leads to weak, brittle bones (osteoporosis), especially in women.",
        "food_connection": "dairy (milk, yogurt, cheese), fortified plant milks, leafy greens, canned fish with bones"
    },
    "Magnesium": {
        "simple": "A mineral that helps muscles relax, supports sleep, and calms the nervous system",
        "detail": "Magnesium is involved in over 300 body processes! It helps muscles relax after they contract, supports deep sleep, and keeps your heart rhythm steady. Many people are low in magnesium without knowing it.",
        "why_matters": "Low magnesium is linked to muscle cramps, anxiety, poor sleep, and heart palpitations.",
        "food_connection": "pumpkin seeds, almonds, spinach, black beans, dark chocolate, avocado"
    },
    "Zinc": {
        "simple": "A mineral that supports your immune system and wound healing",
        "detail": "Zinc is like a security guard for your immune system. It helps fight off viruses and bacteria, heals wounds, and even affects your sense of taste and smell. Your body can't store much zinc, so you need it regularly from food.",
        "why_matters": "Low zinc makes you more likely to get sick and slows down healing.",
        "food_connection": "oysters, beef, pumpkin seeds, chickpeas, cashews, fortified cereals"
    },
    "Folate": {
        "simple": "A B vitamin essential for cell growth and making DNA",
        "detail": "Folate (also called B9) helps your body make new cells and is especially critical during pregnancy for the baby's brain and spine development. 'Folic acid' is the synthetic form in supplements; 'folate' is the natural form in food.",
        "why_matters": "Getting enough folate is crucial for preventing birth defects and supporting overall cell health.",
        "food_connection": "leafy greens, lentils, asparagus, broccoli, fortified cereals, avocado"
    },
    "Potassium": {
        "simple": "A mineral that helps control blood pressure and muscle function",
        "detail": "Potassium works opposite to sodium—it helps lower blood pressure by relaxing blood vessel walls. It also helps muscles contract properly, including your heart. Most Americans get too little potassium and too much sodium.",
        "why_matters": "Low potassium can cause muscle weakness, cramps, and high blood pressure.",
        "food_connection": "bananas, potatoes, sweet potatoes, beans, spinach, yogurt"
    },
    "Antioxidants": {
        "simple": "Substances that protect your cells from damage",
        "detail": "Antioxidants are like bodyguards for your cells. They neutralize 'free radicals'—harmful molecules that damage cells and contribute to aging and disease. Different antioxidants (vitamin C, vitamin E, beta-carotene) protect different parts of cells.",
        "why_matters": "Eating antioxidant-rich foods helps prevent cell damage linked to cancer, heart disease, and aging.",
        "food_connection": "berries, colorful vegetables, green tea, dark chocolate, tomatoes, citrus fruits"
    },
    "Anti-inflammatory": {
        "simple": "Foods that calm down irritation and swelling in your body",
        "detail": "Inflammation is your body's response to injury or stress—helpful short-term, harmful long-term. Anti-inflammatory foods are like a fire extinguisher, calming down chronic inflammation that causes disease.",
        "why_matters": "Chronic inflammation underlies most modern diseases. Food is powerful medicine here.",
        "food_connection": "berries, turmeric, ginger, fatty fish, olive oil, leafy greens"
    },
}

SYMPTOM_EXPLANATIONS = {
    "fatigue": {
        "what_it_means": "Feeling tired even after rest",
        "common_causes": "Low iron, low B12, poor sleep, thyroid issues, inflammation",
        "food_help": "Iron-rich foods (spinach, lentils), B12 foods (eggs, fortified cereals), anti-inflammatory foods"
    },
    "brain_fog": {
        "what_it_means": "Difficulty concentrating, memory issues, feeling 'cloudy'",
        "common_causes": "Low B12, poor methylation, inflammation, blood sugar swings",
        "food_help": "Omega-3s (salmon, walnuts), B vitamins (eggs, greens), stable protein/fiber meals"
    },
    "joint_pain": {
        "what_it_means": "Aching, stiffness, or swelling in joints",
        "common_causes": "Inflammation, omega-3 deficiency, vitamin D deficiency",
        "food_help": "Fatty fish, turmeric, ginger, berries, leafy greens"
    },
    "anxiety": {
        "what_it_means": "Excessive worry, nervousness, or unease",
        "common_causes": "Magnesium deficiency, B vitamin deficiency, blood sugar swings, gut issues",
        "food_help": "Magnesium foods (pumpkin seeds, spinach), complex carbs, fermented foods"
    },
    "digestive_issues": {
        "what_it_means": "Bloating, constipation, diarrhea, or stomach pain",
        "common_causes": "Low fiber, food sensitivities, poor gut bacteria balance",
        "food_help": "Fiber (oats, beans, vegetables), fermented foods (yogurt), plenty of water"
    },
    "weak_immunity": {
        "what_it_means": "Getting sick often, slow healing",
        "common_causes": "Low vitamin D, low zinc, low vitamin C, poor nutrition overall",
        "food_help": "Citrus fruits, bell peppers, mushrooms, fortified milk, pumpkin seeds"
    }
}


def init_session_state():
    """Initialize session state variables."""
    if 'user_context' not in st.session_state:
        st.session_state.user_context = None
    if 'nutrient_priorities' not in st.session_state:
        st.session_state.nutrient_priorities = None
    if 'resource_map' not in st.session_state:
        st.session_state.resource_map = None
    if 'shopping_list' not in st.session_state:
        st.session_state.shopping_list = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'spanish_mode' not in st.session_state:
        st.session_state.spanish_mode = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your EatWell nutrition assistant. 🥕 Ask me anything about health terms, nutrients, foods, or how to use this app. I'm here to help you understand your health in plain language!"}
        ]
    if 'openai_api_key' not in st.session_state:
        # Check environment variable first
        st.session_state.openai_api_key = os.environ.get('OPENAI_API_KEY', '')
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
    if 'ai_provider' not in st.session_state:
        # Auto-select based on available keys
        if st.session_state.gemini_api_key:
            st.session_state.ai_provider = 'gemini'
        elif st.session_state.openai_api_key:
            st.session_state.ai_provider = 'openai'
        else:
            st.session_state.ai_provider = 'gemini'  # Default to Gemini (free)
    
    # Wizard state
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 1
    if 'wizard_data' not in st.session_state:
        st.session_state.wizard_data = {
            'name': '',
            'weekly_budget': 75,
            'snap_status': False,
            'wic_status': False,
            'zip_code': '77001',
            'has_vehicle': False,
            'has_transit': True,
            'trips_per_week': 2,
            # Demographics (all optional)
            'age': None,
            'biological_sex': 'Prefer not to say',
            'height_feet': None,
            'height_inches': None,
            'weight_lbs': None,
            'activity_level': 'Not specified',
            'pregnancy_status': 'None',
            'dietary_preference': 'None',
            'health_goals': [],
            # Health info
            'family_history': [],
            'current_symptoms': [],
            'allergies': [],
            'mthfr_variant': 'Not Tested',
            'comt_variant': 'Not Tested',
            'b12_level': 0,
            'vit_d_level': 0,
            'iron_level': 0,
            'crp_level': 0.0,
            'homocysteine': 0.0,
            'glucose': 0
        }


# =============================================================================
# CHATBOT LOGIC
# =============================================================================

def build_system_prompt() -> str:
    """Build a system prompt for the AI chatbot with health context."""
    # Check if Spanish mode is enabled
    spanish_mode = st.session_state.get("spanish_mode", False)
    
    if spanish_mode:
        base_prompt = """Eres un asistente de nutrición amigable y servicial para EatWell, una aplicación enfocada en la equidad en salud. IMPORTANTE: Responde SIEMPRE en español. Tu rol es:

1. Explicar conceptos de salud y nutrición en lenguaje simple y claro que cualquiera pueda entender
2. Ayudar a los usuarios a entender sus resultados de laboratorio, síntomas y necesidades de nutrientes
3. Proporcionar recomendaciones alimentarias para problemas de salud
4. Ser especialmente útil para personas con poca educación en salud - evita jerga técnica, usa ejemplos
5. Ser sensible a las restricciones de presupuesto y los desafíos de acceso a alimentos
6. Enfocarte en consejos prácticos y aplicables

Términos de salud clave para explicar de forma simple cuando se pregunte:
- MTHFR: Un gen que afecta cómo tu cuerpo usa las vitaminas B (folato, B12). Algunas personas tienen variaciones que significan que necesitan más de estas vitaminas.
- Metilación: Cómo tu cuerpo activa las vitaminas y procesa los nutrientes. Piensa en ello como el "sistema de procesamiento" de tu cuerpo.
- Homocisteína: Un aminoácido en la sangre. Niveles altos pueden indicar que necesitas más vitaminas B.
- CRP: Un marcador de inflamación en el cuerpo. Mayor = más inflamación.
- Ferritina: Muestra cuánto hierro tiene almacenado tu cuerpo.
- B12: Vitamina esencial para la energía, función cerebral y salud de la sangre.
- Folato: Una vitamina B necesaria para el crecimiento celular, especialmente importante durante el embarazo.
- Vitamina D: La "vitamina del sol" - importante para los huesos, el estado de ánimo y el sistema inmunológico.

Consejos de nutrición económicos:
- Los huevos, frijoles y lentejas son fuentes de proteína económicas
- Las verduras congeladas son igual de nutritivas que las frescas
- El pescado enlatado (sardinas, salmón) proporciona omega-3 de forma económica
- La avena es un desayuno económico y llenador
- ¡Los beneficios de SNAP se pueden usar en mercados de agricultores (a menudo se duplican!)

Siempre sé alentador y sin juzgar. Encuentra a las personas donde están. RECUERDA: Responde siempre en español."""
    else:
        base_prompt = """You are a friendly, helpful nutrition assistant for EatWell, an app focused on health equity. Your role is to:

1. Explain health and nutrition concepts in simple, plain language that anyone can understand
2. Help users understand their lab results, symptoms, and nutrient needs
3. Provide food-based recommendations for health concerns
4. Be especially helpful to people with low health literacy - avoid jargon, use examples
5. Be sensitive to budget constraints and food access challenges
6. Focus on practical, actionable advice

Key health terms to explain simply when asked:
- MTHFR: A gene that affects how your body uses B vitamins (folate, B12). Some people have variations that mean they need more of these vitamins.
- Methylation: How your body activates vitamins and processes nutrients. Think of it as your body's "processing system."
- Homocysteine: An amino acid in blood. High levels can indicate you need more B vitamins.
- CRP: A marker of inflammation in the body. Higher = more inflammation.
- Ferritin: Shows how much iron your body has stored.
- B12: Essential vitamin for energy, brain function, and blood health.
- Folate: A B vitamin needed for cell growth, especially important during pregnancy.
- Vitamin D: The "sunshine vitamin" - important for bones, mood, and immune system.

Budget-friendly nutrition tips:
- Eggs, beans, and lentils are affordable protein sources
- Frozen vegetables are just as nutritious as fresh
- Canned fish (sardines, salmon) provides omega-3s cheaply
- Oats are an economical, filling breakfast
- SNAP benefits can be used at farmers markets (often doubled!)

Always be encouraging and non-judgmental. Meet people where they are."""
    
    # Add user context if available
    if st.session_state.analysis_complete and st.session_state.user_context:
        user = st.session_state.user_context
        nutrients = st.session_state.nutrient_priorities
        
        context_info = "\n\nCurrent user context:\n"
        context_info += f"- Budget: ${user.financials.weekly_budget}/week\n"
        context_info += f"- SNAP: {'Yes' if user.financials.snap_status else 'No'}\n"
        
        if user.medical.current_symptoms:
            context_info += f"- Symptoms: {', '.join(user.medical.current_symptoms)}\n"
        
        if nutrients and nutrients.needs:
            top_nutrients = [n.nutrient for n in nutrients.needs[:5]]
            context_info += f"- Top nutrient needs: {', '.join(top_nutrients)}\n"
        
        base_prompt += context_info
    
    return base_prompt


def get_ai_response(user_message: str) -> Optional[str]:
    """Get a response from AI (Gemini or OpenAI)."""
    provider = st.session_state.ai_provider
    
    # Try Gemini first if selected
    if provider == 'gemini' and GEMINI_AVAILABLE and st.session_state.gemini_api_key:
        try:
            genai.configure(api_key=st.session_state.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')  # Free, fast model
            
            # Build prompt with system context and conversation history
            system_prompt = build_system_prompt()
            
            # Build conversation history
            history = ""
            recent_messages = st.session_state.chat_messages[-10:]
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                history += f"{role}: {msg['content']}\n\n"
            
            full_prompt = f"""{system_prompt}

Conversation so far:
{history}

User: {user_message}

Assistant:"""
            
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            st.session_state.ai_error = str(e)
            return None
    
    # Try OpenAI if selected
    if provider == 'openai' and OPENAI_AVAILABLE and st.session_state.openai_api_key:
        try:
            client = OpenAI(api_key=st.session_state.openai_api_key)
            
            # Build messages with conversation history (last 10 messages)
            messages = [{"role": "system", "content": build_system_prompt()}]
            
            # Add recent conversation history
            recent_messages = st.session_state.chat_messages[-10:]
            for msg in recent_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective, fast model
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            st.session_state.ai_error = str(e)
            return None
    
    return None


def get_chatbot_response(user_message: str) -> str:
    """
    Generate a response to the user's message.
    Uses AI if available, falls back to rule-based responses.
    """
    # Try AI first
    ai_response = get_ai_response(user_message)
    if ai_response:
        return ai_response
    
    # Fall back to rule-based responses
    return get_rule_based_response(user_message)


def get_rule_based_response(user_message: str) -> str:
    """
    Generate a rule-based response using the health knowledge base.
    This is the fallback when AI is not available.
    """
    message_lower = user_message.lower().strip()
    spanish_mode = st.session_state.get("spanish_mode", False)
    
    # Spanish responses when spanish mode is on
    if spanish_mode:
        # Check for greetings in Spanish or English
        greetings = ['hi', 'hello', 'hey', 'help', 'start', 'hola', 'ayuda', 'comenzar']
        if any(message_lower == g or message_lower.startswith(g + ' ') for g in greetings):
            return """¡Hola! Estoy aquí para ayudarte a entender la nutrición y la salud. Aquí hay algunas cosas que puedes preguntarme:

• **"¿Qué es MTHFR?"** - Aprende sobre términos de salud
• **"¿Por qué necesito B12?"** - Entiende los nutrientes
• **"¿Qué alimentos ayudan con la fatiga?"** - Obtén sugerencias de alimentos
• **"¿Cómo uso esta aplicación?"** - Obtén orientación
• **"¿Qué es SNAP?"** - Aprende sobre asistencia alimentaria

¿Qué te gustaría saber?"""
        
        # Default Spanish response
        return """No estoy seguro de haber entendido eso. Aquí hay algunas cosas que puedes preguntarme:

• **Términos de salud:** "¿Qué es MTHFR?" "¿Qué significa CRP?"
• **Síntomas:** "¿Por qué estoy cansado?" "¿Qué ayuda con la niebla mental?"
• **Consejos de alimentos:** "¿Qué alimentos reducen la inflamación?"
• **Ayuda con la app:** "¿Cómo uso esta aplicación?"
• **Beneficios:** "¿Qué es SNAP?" "¿Cómo funciona WIC?"

¡O simplemente describe lo que te interesa y trataré de ayudar!"""
    
    # English responses (original logic)
    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'help', 'start']
    if any(message_lower == g or message_lower.startswith(g + ' ') for g in greetings):
        return """Hello! I'm here to help you understand nutrition and health. Here are some things you can ask me:

• **"What is MTHFR?"** - Learn about health terms
• **"Why do I need B12?"** - Understand nutrients
• **"What foods help with fatigue?"** - Get food suggestions
• **"How do I use this app?"** - Get guidance
• **"What is SNAP?"** - Learn about food assistance

What would you like to know?"""
    
    # Check for app usage questions
    app_questions = ['how do i use', 'how does this work', 'what do i do', 'getting started', 'how to start']
    if any(q in message_lower for q in app_questions):
        return """**How to use this app:**

1️⃣ **Fill out the sidebar form** (on the left) with your:
   - Budget and food assistance status
   - Location and transportation
   - Health symptoms and family history
   - Lab results (optional but helpful)

2️⃣ **Click "Generate My Plan"** to get personalized recommendations

3️⃣ **Explore your results** in the tabs:
   - 🛒 Shopping List - What to buy
   - 🔬 Nutrient Analysis - Why you need it
   - 📍 Store Finder - Where to shop
   - ❓ Ask Why - Understand the science
   - 📚 Learn - Health education

💡 **Tip:** Click "Load Demo Data" to see an example first!"""
    
    # Check for glossary terms
    for term, info in HEALTH_GLOSSARY.items():
        term_lower = term.lower()
        if term_lower in message_lower or (len(term_lower) > 3 and term_lower[:4] in message_lower):
            return f"""**{term}**

📝 **Simple explanation:** {info['simple']}

📖 **More detail:** {info['detail']}

💡 **Why it matters:** {info['why_matters']}

🥗 **Foods that help:** {info['food_connection']}"""
    
    # Check for symptom questions
    symptom_keywords = {
        'fatigue': 'fatigue', 'tired': 'fatigue', 'exhausted': 'fatigue', 'no energy': 'fatigue',
        'brain fog': 'brain_fog', 'foggy': 'brain_fog', 'concentrate': 'brain_fog', 'memory': 'brain_fog',
        'joint': 'joint_pain', 'joints': 'joint_pain', 'arthritis': 'joint_pain',
        'anxiety': 'anxiety', 'anxious': 'anxiety', 'nervous': 'anxiety', 'worry': 'anxiety',
        'digest': 'digestive_issues', 'stomach': 'digestive_issues', 'bloat': 'digestive_issues', 'gut': 'digestive_issues',
        'sick': 'weak_immunity', 'immunity': 'weak_immunity', 'immune': 'weak_immunity', 'cold': 'weak_immunity'
    }
    
    for keyword, symptom_key in symptom_keywords.items():
        if keyword in message_lower:
            if symptom_key in SYMPTOM_EXPLANATIONS:
                info = SYMPTOM_EXPLANATIONS[symptom_key]
                return f"""**About {symptom_key.replace('_', ' ').title()}:**

🤔 **What it means:** {info['what_it_means']}

⚠️ **Common causes:** {info['common_causes']}

🥗 **Foods that can help:** {info['food_help']}

💡 Fill out the sidebar form and I can give you personalized food recommendations for this!"""
    
    # Check for food questions
    food_questions = ['what should i eat', 'what foods', 'best foods', 'food for', 'foods for', 'what to eat']
    if any(q in message_lower for q in food_questions):
        # Check if they mentioned a specific condition
        if 'inflam' in message_lower:
            return """**Anti-inflammatory foods:**

🥗 **Best choices:**
• Fatty fish (salmon, sardines)
• Berries (blueberries, strawberries)
• Leafy greens (spinach, kale)
• Turmeric and ginger
• Olive oil
• Nuts (walnuts, almonds)

❌ **Foods to limit:**
• Processed foods
• Sugary drinks
• Refined carbs
• Fried foods

💡 Fill out the form with your symptoms to get personalized recommendations!"""
        
        if 'energy' in message_lower or 'tired' in message_lower:
            return """**Foods for energy:**

🥗 **Best choices:**
• Iron-rich: spinach, lentils, beans, fortified cereals
• B12-rich: eggs, fortified cereals, nutritional yeast
• Complex carbs: oats, brown rice, quinoa
• Healthy fats: nuts, avocado, olive oil

💧 Also make sure you're drinking enough water!

💡 Low energy often signals low iron or B vitamins. Fill out the sidebar form to get personalized recommendations!"""
        
        return """To give you the best food recommendations, I need to know more about your health needs!

**Please fill out the sidebar form** with your symptoms and any lab results you have.

Or ask me about a specific condition, like:
- 'What foods help with inflammation?'
- 'What should I eat for more energy?'
- 'What foods are good for brain health?'"""
    
    # Check for budget/assistance questions
    if 'snap' in message_lower or 'food stamp' in message_lower:
        return HEALTH_GLOSSARY['SNAP']['detail'] + "\n\n" + "✅ This app shows you which stores accept SNAP and prioritizes SNAP-eligible foods in your shopping list!"
    
    if 'wic' in message_lower:
        return HEALTH_GLOSSARY['WIC']['detail'] + "\n\n" + "✅ This app marks WIC-eligible foods and shows WIC-authorized stores near you!"
    
    if 'budget' in message_lower or 'cheap' in message_lower or 'afford' in message_lower or 'money' in message_lower:
        return """**Eating healthy on a budget:**

💰 **Budget-friendly nutritious foods:**
• Eggs - cheap protein with B12
• Canned beans - protein and fiber for ~$1
• Frozen vegetables - just as nutritious as fresh
• Oats - filling breakfast for pennies
• Bananas - cheapest fruit, good nutrition
• Peanut butter - protein that lasts

🆓 **Free resources:**
• Food pantries (we'll show you nearby ones!)
• SNAP doubles at many farmers markets

💡 Set your budget in the sidebar and we'll prioritize affordable options for you!"""
    
    # Check for lab result questions
    lab_keywords = ['lab', 'blood test', 'bloodwork', 'test result', 'numbers']
    if any(k in message_lower for k in lab_keywords):
        return """**Understanding your lab results:**

Common tests and what they mean:

🔬 **Vitamin B12** (pg/mL)
• Below 300 = deficient
• 300-500 = low-normal
• 500-900 = optimal

☀️ **Vitamin D** (ng/mL)
• Below 20 = deficient
• 20-30 = insufficient
• 30-60 = optimal

🩸 **Iron** (mcg/dL)
• Below 60 = low
• 60-170 = normal

🔥 **CRP** (mg/L) - inflammation
• Below 1 = low inflammation
• 1-3 = moderate
• Above 3 = high

💡 Enter your lab values in the sidebar form and I'll explain what they mean for YOUR health!"""
    
    # Personalized responses if user data is available
    if st.session_state.analysis_complete and st.session_state.user_context:
        user = st.session_state.user_context
        nutrients = st.session_state.nutrient_priorities
        
        # Check if asking about their specific results
        if 'my' in message_lower or 'mine' in message_lower or 'for me' in message_lower:
            if nutrients and nutrients.needs:
                top_needs = nutrients.needs[:3]
                response = "**Based on your health profile:**\n\n"
                response += "Your top nutrient priorities are:\n"
                for need in top_needs:
                    response += f"• **{need.nutrient}** - {need.reason[:80]}...\n"
                response += "\n💡 Check the 🛒 Shopping List tab to see foods that address these needs!"
                return response
    
    # Default response
    return """I'm not sure I understood that. Here are some things you can ask me:

• **Health terms:** "What is MTHFR?" "What does CRP mean?"
• **Symptoms:** "Why am I tired?" "What helps with brain fog?"
• **Food advice:** "What foods reduce inflammation?"
• **App help:** "How do I use this app?"
• **Benefits:** "What is SNAP?" "How does WIC work?"

Or just describe what you're curious about and I'll try to help!"""


def render_chatbot():
    """Render the chatbot interface."""
    st.markdown(f"### 💬 {t('ask_nutrition_assistant')}")
    
    # Simple AI status indicator (API keys come from environment variables)
    if st.session_state.gemini_api_key:
        st.caption("✨ Powered by Gemini AI")
    elif st.session_state.openai_api_key:
        st.caption("✨ Powered by GPT-4")
    else:
        st.caption("Ask me about health terms, nutrients, or how to use this app!")
    
    # Update the initial greeting based on language
    spanish_mode = st.session_state.get("spanish_mode", False)
    if st.session_state.chat_messages and len(st.session_state.chat_messages) == 1:
        if spanish_mode:
            st.session_state.chat_messages[0]["content"] = "¡Hola! Soy tu asistente de nutrición de EatWell. 🥕 Pregúntame sobre términos de salud, nutrientes, alimentos o cómo usar esta aplicación. ¡Estoy aquí para ayudarte a entender tu salud en un lenguaje sencillo!"
        else:
            st.session_state.chat_messages[0]["content"] = "Hi! I'm your EatWell nutrition assistant. 🥕 Ask me anything about health terms, nutrients, foods, or how to use this app. I'm here to help you understand your health in plain language!"
    
    # Chat container (taller now that it's in a tab)
    chat_container = st.container(height=450)
    
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(t("type_question_here"), key="chat_input"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get response
        response = get_chatbot_response(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        st.rerun()


def render_sidebar():
    """Render a minimal sidebar."""
    with st.sidebar:
        st.markdown('<h2 style="color: #4f7e52; margin-bottom: 0.5rem;">🥕 EatWell</h2>', unsafe_allow_html=True)
        st.caption(t("personalized_nutrition"))
        
        # Spanish language toggle
        st.session_state.spanish_mode = st.checkbox(
            "🇪🇸 Español",
            value=st.session_state.spanish_mode,
            help="Toggle Spanish translation / Activar traducción al español"
        )
        
        st.markdown("---")
        
        if st.session_state.analysis_complete:
            # Minimal sidebar after analysis is complete
            user = st.session_state.user_context
            
            st.markdown(f"**👤 {user.name}**")
            st.caption(f"📍 {user.logistics.zip_code}")
            st.caption(f"💰 ${user.financials.weekly_budget:.0f}/{t('weekly_budget').lower()}")
            
            if user.financials.snap_status:
                st.caption("✅ SNAP")
            if user.financials.wic_status:
                st.caption("✅ WIC")
            
            st.markdown("---")
            
            # Quick budget adjustment
            new_budget = st.slider(
                t("adjust_budget"), 
                20, 300, 
                int(user.financials.weekly_budget), 
                step=5,
                help="Quickly adjust budget and regenerate plan"
            )
            
            if new_budget != user.financials.weekly_budget:
                if st.button(f"🔄 {t('update_plan')}", use_container_width=True):
                    user.financials.weekly_budget = float(new_budget)
                    run_analysis()
                    st.rerun()
            
            st.markdown("---")
            
            # Start over option
            if st.button(f"🔄 {t('start_over')}", use_container_width=True):
                st.session_state.analysis_complete = False
                st.session_state.user_context = None
                st.session_state.wizard_step = 1
                st.session_state.wizard_data = {
                    'name': '',
                    'weekly_budget': 75,
                    'snap_status': False,
                    'wic_status': False,
                    'zip_code': '77001',
                    'has_vehicle': False,
                    'has_transit': True,
                    'trips_per_week': 2,
                    # Demographics (all optional)
                    'age': None,
                    'biological_sex': 'Prefer not to say',
                    'height_feet': None,
                    'height_inches': None,
                    'weight_lbs': None,
                    'activity_level': 'Not specified',
                    'pregnancy_status': 'None',
                    'dietary_preference': 'None',
                    'health_goals': [],
                    # Health info
                    'family_history': [],
                    'current_symptoms': [],
                    'allergies': [],
                    'mthfr_variant': 'Not Tested',
                    'comt_variant': 'Not Tested',
                    'b12_level': 0,
                    'vit_d_level': 0,
                    'iron_level': 0,
                    'crp_level': 0.0,
                    'homocysteine': 0.0,
                    'glucose': 0
                }
                # Clear multiselect keys
                for key in ['wizard_symptoms', 'wizard_family_history', 'wizard_allergies', 'wizard_health_goals']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        else:
            # Before analysis: minimal sidebar, wizard is in main area
            st.info("👉 Use the form in the main area to get started!")


def run_analysis():
    """Run the full analysis pipeline."""
    user = st.session_state.user_context
    if user:
        st.session_state.nutrient_priorities = analyze_lab_data(user)
        st.session_state.resource_map = resource_locator(user)
        st.session_state.shopping_list = generate_shopping_list(
            user,
            st.session_state.nutrient_priorities,
            st.session_state.resource_map
        )
        st.session_state.analysis_complete = True


def build_user_from_wizard():
    """Build UserContext from wizard data."""
    data = st.session_state.wizard_data
    
    name = data['name'] if data['name'] else "User"
    
    financials = Financials(
        weekly_budget=float(data['weekly_budget']),
        snap_status=data['snap_status'],
        wic_status=data['wic_status']
    )
    
    logistics = Logistics(
        zip_code=data['zip_code'],
        has_vehicle=data['has_vehicle'],
        has_public_transit=data['has_transit'],
        grocery_trips_per_week=data['trips_per_week'],
        max_travel_distance_miles=15.0 if data['has_vehicle'] else (5.0 if data['has_transit'] else 2.0)
    )
    
    medical = MedicalHistory(
        family_history=[h.lower().replace(" ", "_") for h in data['family_history']],
        current_symptoms=[s.lower().replace(" ", "_") for s in data['current_symptoms']],
        known_allergies=[a.lower() for a in data['allergies']]
    )
    
    lab_results = None
    if any([data['b12_level'], data['vit_d_level'], data['iron_level'], data['crp_level'], 
            data['homocysteine'], data['glucose'],
            data['mthfr_variant'] != "Not Tested", data['comt_variant'] != "Not Tested"]):
        lab_results = LabResults(
            mthfr_variant=data['mthfr_variant'] if data['mthfr_variant'] not in ["Not Tested", "Normal"] else None,
            comt_variant=data['comt_variant'].lower() if data['comt_variant'] not in ["Not Tested", "Normal"] else None,
            vitamin_b12_level=float(data['b12_level']) if data['b12_level'] > 0 else None,
            vitamin_d_level=float(data['vit_d_level']) if data['vit_d_level'] > 0 else None,
            iron_level=float(data['iron_level']) if data['iron_level'] > 0 else None,
            crp_level=float(data['crp_level']) if data['crp_level'] > 0 else None,
            homocysteine_level=float(data['homocysteine']) if data['homocysteine'] > 0 else None,
            glucose_fasting=float(data['glucose']) if data['glucose'] > 0 else None
        )
    
    # Build demographics (all optional)
    demographics = None
    has_demographics = any([
        data.get('age'),
        data.get('biological_sex') not in [None, 'Prefer not to say', t('prefer_not_to_say')],
        data.get('height_feet'),
        data.get('weight_lbs'),
        data.get('activity_level') not in [None, 'Not specified', t('not_specified')],
        data.get('pregnancy_status') not in [None, 'None', t('not_applicable')],
        data.get('dietary_preference') not in [None, 'None', t('no_preference')],
        data.get('health_goals')
    ])
    
    if has_demographics:
        # Map UI values to stored values
        sex_map = {t('female'): 'female', t('male'): 'male', t('prefer_not_to_say'): None, 'Female': 'female', 'Male': 'male'}
        activity_map = {
            t('sedentary'): 'sedentary', t('lightly_active'): 'lightly_active',
            t('moderately_active'): 'moderately_active', t('very_active'): 'very_active',
            t('not_specified'): None, 'Sedentary': 'sedentary', 'Lightly Active': 'lightly_active',
            'Moderately Active': 'moderately_active', 'Very Active': 'very_active'
        }
        preg_map = {
            t('pregnant'): 'pregnant', t('breastfeeding'): 'breastfeeding',
            t('trying_to_conceive'): 'trying_to_conceive', t('not_applicable'): None,
            'Pregnant': 'pregnant', 'Breastfeeding': 'breastfeeding', 'Trying to Conceive': 'trying_to_conceive'
        }
        diet_map = {
            t('vegetarian'): 'vegetarian', t('vegan'): 'vegan', t('pescatarian'): 'pescatarian',
            t('keto'): 'keto', t('mediterranean'): 'mediterranean', t('no_preference'): None,
            'Vegetarian': 'vegetarian', 'Vegan': 'vegan', 'Pescatarian': 'pescatarian',
            'Keto/Low-Carb': 'keto', 'Mediterranean': 'mediterranean'
        }
        
        demographics = Demographics(
            age=data.get('age'),
            biological_sex=sex_map.get(data.get('biological_sex')),
            height_feet=data.get('height_feet'),
            height_inches=data.get('height_inches') if data.get('height_inches') else 0,
            weight_lbs=data.get('weight_lbs'),
            activity_level=activity_map.get(data.get('activity_level')),
            pregnancy_status=preg_map.get(data.get('pregnancy_status')),
            dietary_preference=diet_map.get(data.get('dietary_preference')),
            health_goals=[g.lower().replace(" ", "_") for g in data.get('health_goals', [])]
        )
    
    return UserContext(
        user_id=f"user_{name.lower().replace(' ', '_')}",
        name=name,
        financials=financials,
        logistics=logistics,
        medical=medical,
        lab_results=lab_results,
        demographics=demographics
    )


def render_wizard():
    """Render the 3-step wizard for data entry."""
    step = st.session_state.wizard_step
    data = st.session_state.wizard_data
    
    # Progress indicator
    st.markdown(f"### {t('step_of')} " + str(step) + f" {t('of')} 3")
    progress = step / 3
    st.progress(progress)
    
    st.markdown("---")
    
    if step == 1:
        # Step 1: Budget & Location
        st.markdown(f"## 💰 {t('budget_location')}")
        st.caption(t("lets_start_basics"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            data['name'] = st.text_input(t("your_name"), value=data['name'], placeholder=t("enter_your_name"))
            data['weekly_budget'] = st.slider(t("weekly_grocery_budget"), 20, 300, data['weekly_budget'], step=5)
            
            st.markdown(f"**{t('benefits')}**")
            col_snap, col_wic = st.columns(2)
            with col_snap:
                data['snap_status'] = st.checkbox("SNAP", value=data['snap_status'])
            with col_wic:
                data['wic_status'] = st.checkbox("WIC", value=data['wic_status'])
        
        with col2:
            data['zip_code'] = st.text_input(t("zip_code"), value=data['zip_code'], max_chars=5)
            
            st.markdown(f"**{t('transportation')}**")
            col_car, col_bus = st.columns(2)
            with col_car:
                data['has_vehicle'] = st.checkbox(t("car_access"), value=data['has_vehicle'])
            with col_bus:
                data['has_transit'] = st.checkbox(t("public_transit"), value=data['has_transit'])
            
            data['trips_per_week'] = st.slider(t("grocery_trips_week"), 1, 7, data['trips_per_week'])
        
        # Demographics section (optional)
        with st.expander(f"📋 {t('about_you')}", expanded=False):
            demo_col1, demo_col2 = st.columns(2)
            
            with demo_col1:
                # Age (optional)
                age_value = data['age'] if data['age'] is not None else 0
                age_input = st.number_input(t("age"), min_value=0, max_value=120, value=age_value, 
                                           help="Leave at 0 to skip")
                data['age'] = age_input if age_input > 0 else None
                
                # Biological sex
                sex_options = [t("prefer_not_to_say"), t("female"), t("male")]
                sex_index = sex_options.index(data['biological_sex']) if data['biological_sex'] in sex_options else 0
                data['biological_sex'] = st.selectbox(t("biological_sex"), sex_options, index=sex_index)
                
                # Activity level
                activity_options = [t("not_specified"), t("sedentary"), t("lightly_active"), 
                                   t("moderately_active"), t("very_active")]
                activity_index = activity_options.index(data['activity_level']) if data['activity_level'] in activity_options else 0
                data['activity_level'] = st.selectbox(t("activity_level"), activity_options, index=activity_index)
            
            with demo_col2:
                # Height (feet and inches)
                st.markdown(f"**{t('height')}**")
                height_col1, height_col2 = st.columns(2)
                with height_col1:
                    feet_value = data['height_feet'] if data['height_feet'] is not None else 0
                    feet_input = st.number_input(t("feet"), min_value=0, max_value=8, value=feet_value)
                    data['height_feet'] = feet_input if feet_input > 0 else None
                with height_col2:
                    inches_value = data['height_inches'] if data['height_inches'] is not None else 0
                    data['height_inches'] = st.number_input(t("inches"), min_value=0, max_value=11, value=inches_value)
                
                # Weight
                weight_value = data['weight_lbs'] if data['weight_lbs'] is not None else 0
                weight_input = st.number_input(t("weight"), min_value=0, max_value=500, value=int(weight_value),
                                              help="Leave at 0 to skip")
                data['weight_lbs'] = float(weight_input) if weight_input > 0 else None
        
        st.markdown("---")
        
        col_back, col_next = st.columns([1, 1])
        with col_next:
            if st.button(f"{t('next')} →", type="primary", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
    
    elif step == 2:
        # Step 2: Health Concerns
        st.markdown(f"## 🩺 {t('health_information')}")
        st.caption(t("health_needs_optional"))
        
        # Initialize multiselect keys from wizard_data if not already set
        if 'wizard_symptoms' not in st.session_state:
            st.session_state.wizard_symptoms = data['current_symptoms']
        if 'wizard_family_history' not in st.session_state:
            st.session_state.wizard_family_history = data['family_history']
        if 'wizard_allergies' not in st.session_state:
            st.session_state.wizard_allergies = data['allergies']
        
        # Use key parameter for proper Streamlit state management (no default when using key)
        current_symptoms = st.multiselect(
            t("current_symptoms"),
            [t("Fatigue"), t("Brain Fog"), t("Joint Pain"), t("Anxiety"), t("Poor Sleep"), t("Digestive Issues"), 
             t("Weak Immunity"), t("Headaches"), t("Skin Problems"), t("Muscle Cramps"), t("Mood Swings"),
             t("Hair Loss"), t("Cold Hands/Feet"), t("Dizziness"), t("Shortness of Breath")],
            key="wizard_symptoms",
            help="Select symptoms you experience regularly"
        )
        data['current_symptoms'] = current_symptoms
        
        family_history = st.multiselect(
            t("family_health_history"),
            [t("Diabetes"), t("Heart Disease"), t("Hypertension"), t("Cancer"), t("Obesity"), t("Thyroid Issues"), 
             t("Alzheimer's/Dementia"), t("Autoimmune Disease"), t("Mental Health Conditions")],
            key="wizard_family_history",
            help="Conditions in parents, grandparents, siblings"
        )
        data['family_history'] = family_history
        
        allergies = st.multiselect(
            t("food_allergies"),
            [t("Gluten"), t("Dairy"), t("Shellfish"), t("Tree Nuts"), t("Peanuts"), t("Eggs"), t("Soy"), t("Fish"), t("Corn"),
             t("Sesame"), t("Nightshades"), t("Sulfites"), t("Histamine"), t("FODMAPs"), t("Latex-Fruit")],
            key="wizard_allergies"
        )
        data['allergies'] = allergies
        
        # Additional lifestyle/dietary preferences
        st.markdown("---")
        
        pref_col1, pref_col2 = st.columns(2)
        
        with pref_col1:
            # Dietary preference
            diet_options = [t("no_preference"), t("vegetarian"), t("vegan"), t("pescatarian"), 
                          t("keto"), t("mediterranean")]
            diet_index = diet_options.index(data['dietary_preference']) if data['dietary_preference'] in diet_options else 0
            data['dietary_preference'] = st.selectbox(t("dietary_preference"), diet_options, index=diet_index)
            
            # Pregnancy/breastfeeding status (show only if biological sex is Female)
            if data.get('biological_sex') == t("female"):
                preg_options = [t("not_applicable"), t("pregnant"), t("breastfeeding"), t("trying_to_conceive")]
                preg_index = preg_options.index(data['pregnancy_status']) if data['pregnancy_status'] in preg_options else 0
                data['pregnancy_status'] = st.selectbox(t("pregnancy_status"), preg_options, index=preg_index)
        
        with pref_col2:
            # Health goals - initialize multiselect key
            if 'wizard_health_goals' not in st.session_state:
                st.session_state.wizard_health_goals = data['health_goals']
            
            health_goals = st.multiselect(
                t("health_goals"),
                [t("weight_loss"), t("weight_gain"), t("maintain_weight"), t("build_muscle"), 
                 t("improve_energy"), t("better_sleep")],
                key="wizard_health_goals",
                help="Select your primary health goals"
            )
            data['health_goals'] = health_goals
        
        st.markdown("---")
        
        col_back, col_skip, col_next = st.columns([1, 1, 1])
        with col_back:
            if st.button(f"← {t('back')}", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with col_skip:
            if st.button(t("skip_to_results"), use_container_width=True):
                user = build_user_from_wizard()
                st.session_state.user_context = user
                run_analysis()
                st.rerun()
        with col_next:
            if st.button(f"{t('next')} →", type="primary", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()
    
    elif step == 3:
        # Step 3: Lab Results (Optional)
        st.markdown(f"## 🧬 {t('lab_results_optional')}")
        st.caption(t("lab_results_help"))
        
        st.info(f"💡 **{t('no_lab_results')}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{t('vitamin_levels')}**")
            data['b12_level'] = st.number_input("Vitamin B12 (pg/mL)", 0, 2000, data['b12_level'], 
                                                 help="Normal: 300-900")
            data['vit_d_level'] = st.number_input("Vitamin D (ng/mL)", 0, 150, data['vit_d_level'], 
                                                   help="Optimal: 30-60")
            data['iron_level'] = st.number_input("Iron (mcg/dL)", 0, 300, data['iron_level'], 
                                                  help="Normal: 60-170")
        
        with col2:
            st.markdown(f"**{t('health_markers')}**")
            data['crp_level'] = st.number_input("CRP (mg/L)", 0.0, 50.0, data['crp_level'], 
                                                 help="Optimal: <1.0")
            data['homocysteine'] = st.number_input("Homocysteine (umol/L)", 0.0, 50.0, data['homocysteine'], 
                                                    help="Optimal: <10")
            data['glucose'] = st.number_input("Fasting Glucose (mg/dL)", 0, 400, data['glucose'], 
                                               help="Normal: <100")
        
        with st.expander(t("genetic_markers")):
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                data['mthfr_variant'] = st.selectbox("MTHFR Variant", 
                    ["Not Tested", "Normal", "C677T", "A1298C", "Compound"],
                    index=["Not Tested", "Normal", "C677T", "A1298C", "Compound"].index(data['mthfr_variant']))
            with col_g2:
                data['comt_variant'] = st.selectbox("COMT Variant", 
                    ["Not Tested", "Normal", "Slow", "Fast"],
                    index=["Not Tested", "Normal", "Slow", "Fast"].index(data['comt_variant']))
        
        st.markdown("---")
        
        col_back, col_generate = st.columns([1, 2])
        with col_back:
            if st.button(f"← {t('back')}", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
        with col_generate:
            if st.button(f"✨ {t('generate_my_plan')}", type="primary", use_container_width=True):
                user = build_user_from_wizard()
                st.session_state.user_context = user
                run_analysis()
                st.rerun()


def render_welcome():
    """Render welcome screen with wizard."""
    # Clean header
    st.markdown('<h1 class="main-header">🥕 EatWell</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{t("personalized_nutrition_planning")}</p>', unsafe_allow_html=True)
    
    # Feature highlights (compact)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"💰 **{t('budget_aware')}** — {t('works_with_snap_wic')}")
    with col2:
        st.markdown(f"🧬 **{t('science_based')}** — {t('personalized_to_you')}")
    with col3:
        st.markdown(f"📍 **{t('location_smart')}** — {t('finds_nearby_stores')}")
    
    st.markdown("---")
    
    # Quick start options
    col_demo, col_spacer = st.columns([1, 2])
    with col_demo:
        if st.button(f"🚀 {t('quick_demo')}", use_container_width=True):
            user = create_sample_user()
            st.session_state.user_context = user
            run_analysis()
            st.rerun()
    
    st.markdown("---")
    
    # Render the wizard
    render_wizard()
    
    # Compact disclaimer at bottom
    st.markdown("---")
    st.caption(f"⚠️ {t('disclaimer')}")


def render_dashboard():
    """Render the main dashboard with analysis results."""
    user = st.session_state.user_context
    nutrients = st.session_state.nutrient_priorities
    resources = st.session_state.resource_map
    shopping = st.session_state.shopping_list
    
    # Header
    st.markdown(f'<h1 class="main-header">🥕 {t("welcome_back")}, {user.name}!</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{t("heres_your_plan")}</p>', unsafe_allow_html=True)
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            t("weekly_budget"),
            f"${user.financials.weekly_budget:.0f}",
            delta=f"${user.financials.weekly_budget - shopping.total_with_transport:.0f} {t('left')}" if shopping.total_with_transport <= user.financials.weekly_budget else t("over_budget")
        )
    
    with col2:
        st.metric(
            t("priority_nutrients"),
            len(nutrients.needs),
            delta=f"{len([n for n in nutrients.needs if n.priority <= 2])} {t('critical')}"
        )
    
    with col3:
        st.metric(
            t("nearby_stores"),
            len(resources.accessible_stores),
            delta=f"{len(resources.food_pantries)} {t('pantries')}"
        )
    
    with col4:
        transport_note = f"+${shopping.estimated_transport_cost:.0f} {t('transport')}" if shopping.estimated_transport_cost > 0 else t("no_transport_cost")
        st.metric(
            t("total_cost"),
            f"${shopping.total_with_transport:.0f}",
            delta=transport_note
        )
    
    st.markdown("---")
    
    # 4 tabs for cleaner navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🛒 {t('my_plan')}", 
        f"📍 {t('where_to_shop')}",
        f"🔬 {t('why_this')}", 
        f"💬 {t('help')}"
    ])
    
    with tab1:
        render_shopping_list(shopping, user, nutrients)
    
    with tab2:
        render_store_finder(resources, user)
    
    with tab3:
        # Nutrient analysis + Why section combined
        render_nutrient_analysis(nutrients, user)
        st.markdown("---")
        render_why_section(shopping, nutrients, user)
    
    with tab4:
        # Learn + AI chat combined
        col_learn, col_chat = st.columns([1, 1])
        with col_learn:
            st.markdown(f"### 📚 {t('learn')}")
            render_learn_section(user, nutrients)
        with col_chat:
            st.markdown(f"### 🤖 {t('ask_ai')}")
            render_chatbot()


def render_shopping_list(shopping: ShoppingList, user: UserContext, nutrients: NutrientPriorityList):
    """Render the shopping list tab."""
    st.markdown(f"## 🛒 {t('your_shopping_list')}")
    
    # Budget bar - now includes transportation
    budget = user.financials.weekly_budget
    food_cost = shopping.total_estimated_cost
    transport_cost = shopping.estimated_transport_cost
    total_cost = shopping.total_with_transport
    pct = min(100, (total_cost / budget) * 100) if budget > 0 else 0
    
    st.progress(pct / 100, text=f"{t('total_budget_used')}: ${total_cost:.2f} / ${budget:.2f}")
    
    # Cost breakdown
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"🛒 {t('food_cost')}", f"${food_cost:.2f}")
    with col2:
        st.metric(f"🚌 {t('transport_cost')}", f"${transport_cost:.2f}" if transport_cost > 0 else t("free"))
    with col3:
        remaining = budget - total_cost
        st.metric(f"💰 {t('remaining')}", f"${remaining:.2f}", delta=f"{t('over') if remaining < 0 else ''}")
    
    # Transport cost breakdown by store
    if shopping.transport_details and any(cost > 0 for cost in shopping.transport_details.values()):
        with st.expander(f"🚌 {t('transport_breakdown')}"):
            for store_name, cost in shopping.transport_details.items():
                if cost > 0:
                    st.markdown(f"• **{store_name}**: ${cost:.2f} ({t('round_trip')})")
            st.caption(f"💡 {t('tip_combine_trips')}")
    
    # Benefits badges
    badges = []
    if user.financials.snap_status:
        badges.append(f"✓ {t('snap_applied')}")
    if user.financials.wic_status:
        badges.append(f"✓ {t('wic_applied')}")
    if badges:
        st.success(" | ".join(badges))
    
    # Food Pantry recommendations
    if shopping.pantry_items:
        st.markdown(f"### 🆓 {t('from_food_pantry')}")
        for item in shopping.pantry_items:
            st.markdown(f"""
            <div class="store-card">
                <span class="free-badge">{t('free').upper()}</span>
                <strong>{item.food.name}</strong><br>
                <small>📍 {item.suggested_store}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Main shopping list by priority
    st.markdown(f"### 📋 {t('items_to_purchase')}")
    
    priority_items = {
        ShoppingPriority.CRITICAL: [],
        ShoppingPriority.HIGH: [],
        ShoppingPriority.MODERATE: [],
        ShoppingPriority.OPTIONAL: []
    }
    
    for item in shopping.items:
        priority_items[item.priority].append(item)
    
    priority_config = {
        ShoppingPriority.CRITICAL: (f"🔴 {t('critical_priority')}", "priority-critical"),
        ShoppingPriority.HIGH: (f"🟠 {t('high_priority')}", "priority-high"),
        ShoppingPriority.MODERATE: (f"🟡 {t('moderate_priority')}", "priority-moderate"),
        ShoppingPriority.OPTIONAL: (f"🟢 {t('optional_priority')}", "priority-optional")
    }
    
    for priority, items in priority_items.items():
        if items:
            label, css_class = priority_config[priority]
            st.markdown(f"**{label}**")
            
            for item in items:
                snap_badge = ' <span class="snap-badge">SNAP✓</span>' if item.food.snap_eligible else ''
                nutrients_str = ", ".join(item.nutrients_addressed[:3])
                
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>{item.food.name}</strong> — ${item.estimated_cost:.2f}{snap_badge}<br>
                    <small>🎯 {t('nutrients')}: {nutrients_str}</small><br>
                    <small>🏪 {t('suggested')}: {item.suggested_store or t('any_store')}</small>
                </div>
                """, unsafe_allow_html=True)


def render_nutrient_analysis(nutrients: NutrientPriorityList, user: UserContext):
    """Render the nutrient analysis tab."""
    st.markdown(f"## 🔬 {t('your_nutrient_analysis')}")
    
    # Warnings
    if nutrients.warnings:
        for warning in nutrients.warnings:
            st.warning(warning)
    
    # Lab results summary
    if user.lab_results:
        st.markdown(f"### 🧬 {t('your_biomarkers')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if user.lab_results.mthfr_variant:
                st.error(f"**MTHFR:** {user.lab_results.mthfr_variant}")
            if user.lab_results.vitamin_b12_level:
                status = "🔴" if user.lab_results.vitamin_b12_level < 500 else "🟢"
                st.info(f"{status} **B12:** {user.lab_results.vitamin_b12_level} pg/mL")
        
        with col2:
            if user.lab_results.vitamin_d_level:
                status = "🔴" if user.lab_results.vitamin_d_level < 30 else "🟢"
                st.info(f"{status} **Vitamin D:** {user.lab_results.vitamin_d_level} ng/mL")
            if user.lab_results.iron_level:
                status = "🔴" if user.lab_results.iron_level < 60 else "🟢"
                st.info(f"{status} **Iron:** {user.lab_results.iron_level} mcg/dL")
        
        with col3:
            if user.lab_results.crp_level:
                status = "🔴" if user.lab_results.crp_level > 1 else "🟢"
                st.info(f"{status} **CRP:** {user.lab_results.crp_level} mg/L")
            if user.lab_results.glucose_fasting:
                status = "🔴" if user.lab_results.glucose_fasting > 100 else "🟢"
                st.info(f"{status} **Glucose:** {user.lab_results.glucose_fasting} mg/dL")
    
    st.markdown("---")
    
    # Nutrient priorities
    st.markdown(f"### 📊 {t('prioritized_nutrient_needs')}")
    
    priority_labels = {1: f"🔴 {t('critical_priority')}", 2: f"🟠 {t('high_priority')}", 3: f"🟡 {t('moderate_priority')}", 4: "🟢 Preventive", 5: "⚪ Supportive"}
    
    for need in nutrients.needs:
        with st.expander(f"{priority_labels.get(need.priority, '⚪')} **{need.nutrient}**"):
            st.markdown(f"**{t('why_matters_for_you')}**")
            st.write(need.reason)
            
            if need.related_markers:
                st.markdown(f"**{t('related_markers')}:** {', '.join(need.related_markers[:4])}")
            
            if need.food_sources:
                st.markdown(f"**{t('best_food_sources')}:**")
                st.write(", ".join(need.food_sources[:6]))


def render_store_finder(resources: ResourceMap, user: UserContext):
    """Render the store finder tab with map visualization."""
    st.markdown(f"## 📍 {t('nearby_food_resources')}")
    
    st.info(f"📍 {t('showing_results_for')}: **{resources.user_zip}** | 🚗 {t('mobility')}: **{user.logistics.mobility_level.upper()}**")
    
    # Map visualization
    if FOLIUM_AVAILABLE and resources.accessible_stores:
        st.markdown(f"### 🗺️ {t('store_locations_map')}")
        
        # Get valid stores for markers
        valid_stores = [tf for tf in resources.accessible_stores 
                       if tf.store.latitude != 0 and tf.store.longitude != 0]
        
        if valid_stores:
            # Center map on the user's zip code
            center_lat, center_lon = get_base_coordinates(resources.user_zip)
            
            # Option to use current location (not stored)
            user_lat, user_lon = None, None
            if GEOLOCATION_AVAILABLE:
                use_current_location = st.checkbox(
                    f"📍 {t('use_current_location')}", 
                    value=False,
                    help=t("location_not_saved")
                )
                
                if use_current_location:
                    with st.spinner(f"{t('getting_location')}"):
                        location = get_geolocation()
                        if location and 'coords' in location:
                            user_lat = location['coords']['latitude']
                            user_lon = location['coords']['longitude']
                            st.success(f"✅ {t('using_current_location')}")
                        else:
                            st.warning(t("could_not_get_location"))
            
            # Create the map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
            
            # Add user location marker only if they opted in
            if user_lat and user_lon:
                folium.Marker(
                    [user_lat, user_lon],
                    popup="📍 Your Current Location (not saved)",
                    tooltip="You are here",
                    icon=folium.Icon(color='blue', icon='user', prefix='fa')
                ).add_to(m)
            
            # Color mapping for store types
            store_colors = {
                StoreType.FOOD_PANTRY: 'green',
                StoreType.GROCERY: 'red',
                StoreType.DISCOUNT: 'orange',
                StoreType.FARMERS_MARKET: 'purple',
                StoreType.SPECIALTY: 'darkblue'
            }
            
            store_icons = {
                StoreType.FOOD_PANTRY: 'heart',
                StoreType.GROCERY: 'shopping-cart',
                StoreType.DISCOUNT: 'tag',
                StoreType.FARMERS_MARKET: 'leaf',
                StoreType.SPECIALTY: 'star'
            }
            
            # Add store markers
            for tf in valid_stores:
                store = tf.store
                color = store_colors.get(store.store_type, 'gray')
                icon = store_icons.get(store.store_type, 'info-sign')
                
                # Build popup content
                price_display = "FREE" if store.store_type == StoreType.FOOD_PANTRY else "$" * store.price_tier
                snap_badge = "✓ SNAP" if store.snap_accepted else ""
                wic_badge = "✓ WIC" if store.wic_accepted else ""
                badges = " | ".join(filter(None, [snap_badge, wic_badge]))
                
                popup_html = f"""
                <div style="width: 200px;">
                    <h4 style="margin: 0 0 5px 0;">{store.name}</h4>
                    <p style="margin: 2px 0;"><b>Price:</b> {price_display}</p>
                    <p style="margin: 2px 0;"><b>Distance:</b> {store.distance_miles} mi</p>
                    <p style="margin: 2px 0;"><b>Travel:</b> {tf.travel_method} (~{tf.estimated_time_minutes} min)</p>
                    <p style="margin: 2px 0;"><b>Transport Cost:</b> ${tf.transit_cost:.2f}</p>
                    <p style="margin: 2px 0;"><b>Hours:</b> {store.hours}</p>
                    {f'<p style="margin: 2px 0; color: green;"><b>{badges}</b></p>' if badges else ''}
                </div>
                """
                
                folium.Marker(
                    [store.latitude, store.longitude],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{store.name} ({store.store_type.value.replace('_', ' ').title()})",
                    icon=folium.Icon(color=color, icon=icon, prefix='fa')
                ).add_to(m)
            
            # Display map
            st_folium(m, width=700, height=400)
            
            # Map legend
            st.markdown("""
            **Map Legend:** 
            🟢 Food Pantry (FREE) | 🔴 Grocery | 🟠 Discount | 🟣 Farmers Market | 🔵 Specialty
            """)
        else:
            st.warning("Store locations not available for map display.")
    elif not FOLIUM_AVAILABLE:
        st.info("💡 Install `folium` and `streamlit-folium` for interactive map visualization.")
    
    st.markdown("---")
    
    # Food Pantries
    if resources.food_pantries:
        st.markdown(f"### 🆓 {t('food_pantries_free')}")
        
        for tf in resources.food_pantries:
            col1, col2 = st.columns([3, 1])
            with col1:
                transport_note = f" | 🚌 ${tf.transit_cost:.2f} transit" if tf.transit_cost > 0 else ""
                st.markdown(f"""
                <div class="store-card">
                    <span class="free-badge">{t('free').upper()}</span>
                    <strong>{tf.store.name}</strong><br>
                    📍 {tf.store.distance_miles} miles ({tf.travel_method}, ~{tf.estimated_time_minutes} min){transport_note}<br>
                    🕐 {tf.store.hours}<br>
                    📦 Items: {', '.join(tf.store.specialty_items[:3])}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.metric(t("score"), f"{tf.accessibility_score:.0%}")
    
    st.markdown("---")
    
    # SNAP Stores
    if user.financials.snap_status and resources.snap_stores:
        st.markdown(f"### 🏪 {t('snap_authorized_stores')}")
        
        for tf in resources.snap_stores[:5]:
            if tf.store.store_type != StoreType.FOOD_PANTRY:
                price_tier = "💲" * tf.store.price_tier
                transport_note = f" | 🚌 ${tf.transit_cost:.2f}" if tf.transit_cost > 0 else ""
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    wic_badge = ' <span style="background:#9c27b0;color:white;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.7rem;">WIC</span>' if tf.store.wic_accepted else ''
                    st.markdown(f"""
                    <div class="store-card">
                        <span class="snap-badge">SNAP</span>{wic_badge}
                        <strong>{tf.store.name}</strong> {price_tier}<br>
                        📍 {tf.store.distance_miles} miles ({tf.travel_method}{transport_note})<br>
                        📦 Inventory: {tf.store.inventory_level.value}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.metric(t("score"), f"{tf.accessibility_score:.0%}")
    
    st.markdown("---")
    
    # All stores with transportation costs
    st.markdown(f"### 🗺️ {t('all_accessible_stores')}")
    
    store_data = []
    for tf in resources.accessible_stores[:8]:
        store_data.append({
            t("store"): tf.store.name,
            t("type"): tf.store.store_type.value.replace("_", " ").title(),
            t("distance"): f"{tf.store.distance_miles} mi",
            t("travel"): f"{tf.travel_method} ({tf.estimated_time_minutes} min)",
            f"{t('transport')} $": f"${tf.transit_cost:.2f}" if tf.transit_cost > 0 else t("free"),
            t("price"): t("free").upper() if tf.store.store_type == StoreType.FOOD_PANTRY else "💲" * tf.store.price_tier,
            "SNAP": "✓" if tf.store.snap_accepted else "—",
            t("score"): f"{tf.accessibility_score:.0%}"
        })
    
    st.dataframe(store_data, use_container_width=True, hide_index=True)


def render_why_section(shopping: ShoppingList, nutrients: NutrientPriorityList, user: UserContext):
    """Render the interactive 'Why' explanation section."""
    st.markdown(f"## ❓ {t('ask_why')}")
    st.markdown(f"*{t('understand_connection')}*")
    
    # Select an item to explain
    item_names = [item.food.name for item in shopping.items]
    
    if not item_names:
        st.warning(t("generate_list_first"))
        return
    
    selected_item = st.selectbox(
        t("select_item_explain"),
        item_names,
        index=0
    )
    
    # Find the item
    selected = None
    for item in shopping.items:
        if item.food.name == selected_item:
            selected = item
            break
    
    if selected:
        st.markdown("---")
        
        # Visual explanation
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"### 📦 {selected.food.name}")
            st.metric(t("price"), f"${selected.estimated_cost:.2f}")
            st.metric(t("priority_level"), selected.priority.name)
            
            if selected.food.snap_eligible:
                st.success("✓ SNAP Eligible")
        
        with col2:
            st.markdown(f"### 🔬 {t('biological_connection')}")
            
            for nutrient in selected.nutrients_addressed:
                # Find the matching nutrient need
                for need in nutrients.needs:
                    if need.nutrient == nutrient:
                        st.markdown(f"""
                        <div class="explanation-box">
                            <strong>➤ {nutrient}</strong><br>
                            {need.reason}<br><br>
                            <small><strong>Related markers:</strong> {', '.join(need.related_markers[:3])}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        break
        
        # Full nutrient profile
        st.markdown(f"### 🥗 {t('nutrient_profile')}")
        st.write(f"**{t('this_food_provides')}:** {', '.join(selected.food.nutrients_provided)}")
        
        # Symptoms connection
        if user.medical.current_symptoms:
            matching = []
            for symptom in user.medical.current_symptoms:
                for nutrient in selected.nutrients_addressed:
                    if any(symptom.lower() in marker.lower() for need in nutrients.needs 
                          if need.nutrient == nutrient for marker in need.related_markers):
                        matching.append(symptom)
            
            if matching:
                st.info(f"🩺 **{t('connected_to_symptoms')}:** {', '.join(set(matching))}")
    
    st.markdown("---")
    
    # Quick nutrient lookup
    st.markdown(f"### 🔍 {t('nutrient_deep_dive')}")
    
    nutrient_names = [need.nutrient for need in nutrients.needs]
    selected_nutrient = st.selectbox(t("select_nutrient_learn"), nutrient_names)
    
    for need in nutrients.needs:
        if need.nutrient == selected_nutrient:
            st.markdown(f"""
            <div class="explanation-box">
                <h4>{need.nutrient}</h4>
                <p><strong>{t('priority_level')}:</strong> {need.priority}</p>
                <p><strong>{t('why_it_matters')}:</strong> {need.reason}</p>
                <p><strong>{t('related_markers')}:</strong> {', '.join(need.related_markers)}</p>
                <p><strong>{t('best_food_sources')}:</strong> {', '.join(need.food_sources[:6])}</p>
            </div>
            """, unsafe_allow_html=True)
            break


def render_learn_section(user: UserContext, nutrients: NutrientPriorityList):
    """Render the health education/literacy section."""
    st.markdown(f"## 📚 {t('learn')}: {t('understanding_your_health')}")
    st.markdown(f"*{t('health_literacy_intro')}*")
    
    # Personalized learning based on user's conditions
    st.markdown("---")
    
    # Section 1: Terms relevant to YOUR results
    st.markdown(f"### 🎯 {t('terms_relevant_to_you')}")
    st.caption(t("based_on_profile"))
    
    relevant_terms = []
    
    # Add terms based on user's lab results
    if user.lab_results:
        if user.lab_results.mthfr_variant:
            relevant_terms.extend(["MTHFR", "Methylation"])
        if user.lab_results.vitamin_b12_level:
            relevant_terms.append("Vitamin B12")
        if user.lab_results.vitamin_d_level:
            relevant_terms.append("Vitamin D")
        if user.lab_results.iron_level:
            relevant_terms.append("Iron")
        if user.lab_results.crp_level:
            relevant_terms.extend(["CRP", "Anti-inflammatory"])
        if user.lab_results.homocysteine_level:
            relevant_terms.append("Homocysteine")
        if user.lab_results.glucose_fasting:
            relevant_terms.append("Fasting Glucose")
    
    # Add terms based on nutrients identified
    for need in nutrients.needs[:5]:
        if "Omega" in need.nutrient:
            relevant_terms.append("Omega-3 Fatty Acids")
        if "inflammatory" in need.nutrient.lower():
            relevant_terms.append("Anti-inflammatory")
    
    # Add benefit terms
    if user.financials.snap_status:
        relevant_terms.append("SNAP")
    if user.financials.wic_status:
        relevant_terms.append("WIC")
    
    # Remove duplicates while preserving order
    relevant_terms = list(dict.fromkeys(relevant_terms))
    
    if relevant_terms:
        for term in relevant_terms[:6]:
            if term in HEALTH_GLOSSARY:
                info = HEALTH_GLOSSARY[term]
                with st.expander(f"📖 **{term}** — {info['simple']}"):
                    st.markdown(f"""
                    <div class="edu-card">
                        <h4>🤔 {t('what_is_it')}</h4>
                        <p>{info['detail']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="simple-explain">
                        <strong>💡 {t('why_matters_for_you_learn')}</strong><br>
                        {info['why_matters']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success(f"🥗 **{t('foods_that_help')}:** {info['food_connection']}")
    else:
        st.info("Fill out the sidebar form to see personalized health education!")
    
    st.markdown("---")
    
    # Section 2: Understanding your symptoms
    if user.medical.current_symptoms:
        st.markdown(f"### 🩺 {t('understanding_symptoms')}")
        st.caption(t("symptoms_explanation"))
        
        for symptom in user.medical.current_symptoms[:4]:
            symptom_key = symptom.lower().replace(" ", "_")
            if symptom_key in SYMPTOM_EXPLANATIONS:
                info = SYMPTOM_EXPLANATIONS[symptom_key]
                with st.expander(f"💭 **{symptom.replace('_', ' ').title()}**"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{t('what_it_means')}:** {info['what_it_means']}")
                        st.markdown(f"**{t('common_causes')}:** {info['common_causes']}")
                    with col2:
                        st.success(f"**🥗 {t('foods_can_help')}:**\n\n{info['food_help']}")
    
    st.markdown("---")
    
    # Section 3: Full glossary
    st.markdown(f"### 📖 {t('health_glossary')}")
    st.caption(t("browse_health_terms"))
    
    search_term = st.text_input(f"🔍 {t('search_term')}", placeholder=t("eg_search"))
    
    # Filter glossary
    filtered_terms = HEALTH_GLOSSARY
    if search_term:
        filtered_terms = {k: v for k, v in HEALTH_GLOSSARY.items() 
                        if search_term.lower() in k.lower() or search_term.lower() in v['simple'].lower()}
    
    if filtered_terms:
        cols = st.columns(2)
        for idx, (term, info) in enumerate(filtered_terms.items()):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="glossary-term">
                    <strong>{term}</strong><br>
                    <small>{info['simple']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Learn more"):
                    st.write(info['detail'])
                    st.caption(f"🥗 {t('foods_that_help')}: {info['food_connection']}")
    else:
        st.warning(f"{t('no_terms_found')} '{search_term}'")
    
    st.markdown("---")
    
    # Section 4: Quick tips
    st.markdown(f"### 💡 {t('quick_tips')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **🛒 {t('shopping_smart')}**
        - Buy frozen vegetables — just as nutritious, last longer, often cheaper
        - Canned beans/lentils are excellent protein sources
        - Store brands are usually the same quality as name brands
        - Shop the perimeter of the store for whole foods
        - Buy in-season produce for best prices
        """)
        
        st.markdown(f"""
        **🏪 {t('using_food_assistance')}**
        - SNAP can be used at most farmers markets (often doubled!)
        - Food pantries are there to help — no shame in using them
        - WIC provides nutritious staples for families
        """)
    
    with col2:
        st.markdown(f"""
        **🍳 {t('cooking_tips')}**
        - Batch cook on weekends to save time and money
        - One-pot meals (soups, stews) stretch ingredients further
        - Eggs are cheap, versatile, and nutritious
        - Beans + rice = complete protein for pennies
        """)
        
        st.markdown(f"""
        **🧠 {t('reading_your_body')}**
        - Fatigue often = need more iron or B vitamins
        - Joint pain often = need more omega-3s and anti-inflammatory foods
        - Getting sick a lot = might need more vitamin D and zinc
        - Listen to your body — cravings sometimes signal deficiencies
        """)
    
    # Disclaimer
    st.markdown("---")
    st.caption(f"⚠️ **Disclaimer:** {t('full_disclaimer')}")


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    # Full-width main content area (chatbot is now a tab)
    if st.session_state.analysis_complete:
        render_dashboard()
    else:
        render_welcome()


if __name__ == "__main__":
    main()
