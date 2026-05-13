import os
import io
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()


def _get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        raise RuntimeError("GEMINI_API_KEY niet gevonden in .env of st.secrets")


genai.configure(api_key=_get_api_key())

JSON_STRUCTUUR = """Schat ook de portiegrootte in (in gram of stuks). De macronutriënten moeten gebaseerd zijn op die geschatte portie.

Geef ALLEEN geldige JSON terug met deze structuur (geen extra tekst):
{
  "samenvatting": "korte zin over de maaltijd",
  "portie_schatting": "bv. 'ongeveer 250 gram' of '1 bord van ~300g'",
  "calorieen_kcal": getal,
  "eiwitten_g": getal,
  "koolhydraten_g": getal,
  "vetten_g": getal,
  "vezels_g": getal,
  "suikers_g": getal,
  "vitamines_mineralen": {
    "vitamine_c_mg": getal,
    "calcium_mg": getal,
    "ijzer_mg": getal,
    "kalium_mg": getal
  },
  "nutri_score": "A, B, C, D of E (officiële Nutri-Score volgens Europees systeem)",
  "nutrient_score": getal van 1 tot 10,
  "score_uitleg": "korte uitleg waarom deze score (zowel Nutri-Score als 1-10)",
  "gezondere_alternatieven": ["alternatief 1", "alternatief 2", "alternatief 3"]
}"""

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={"response_mime_type": "application/json"},
)

def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
        raise

def vraag_gemini(maaltijd: str) -> dict:
    prompt = (
        f'Je bent een voedingsdeskundige. Schat de voedingswaardes van deze maaltijd:\n"{maaltijd}"\n\n'
        + JSON_STRUCTUUR
    )
    response = model.generate_content(prompt)
    return _parse_json(response.text)

def vraag_gemini_met_foto(foto_bytes: bytes, extra_tekst: str = "") -> dict:
    image = Image.open(io.BytesIO(foto_bytes))
    extra = f"\nExtra context van de gebruiker: {extra_tekst}" if extra_tekst.strip() else ""
    prompt = (
        f"Je bent een voedingsdeskundige. Bekijk de foto en schat de voedingswaardes van wat je ziet.{extra}\n\n"
        + JSON_STRUCTUUR
    )
    response = model.generate_content([prompt, image])
    return _parse_json(response.text)
