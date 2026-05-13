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

JSON_STRUCTUUR = """BELANGRIJK: ALLE velden zijn VERPLICHT. Sla geen velden over, laat niets leeg.

Schat ook de portiegrootte in (in gram of stuks). De macronutriënten moeten gebaseerd zijn op die geschatte portie.

Geef ALLEEN geldige JSON terug met EXACT deze structuur (geen extra tekst):
{
  "product_naam": "VERPLICHT - korte naam van het gerecht/product (max 40 tekens, bv. 'Appel' of 'Boterhammen met kaas')",
  "emoji": "VERPLICHT - één emoji die het product het beste representeert (bv. 🍎 of 🥪)",
  "samenvatting": "korte zin over de maaltijd (VERPLICHT)",
  "portie_schatting": "bv. 'ongeveer 250 gram' of '1 bord van ~300g' (VERPLICHT)",
  "calorieen_kcal": getal (VERPLICHT),
  "eiwitten_g": getal (VERPLICHT),
  "koolhydraten_g": getal (VERPLICHT),
  "vetten_g": getal (VERPLICHT),
  "vezels_g": getal (VERPLICHT),
  "suikers_g": getal (VERPLICHT),
  "vitamines_mineralen": {
    "vitamine_c_mg": getal,
    "calcium_mg": getal,
    "ijzer_mg": getal,
    "kalium_mg": getal
  },
  "nutri_score": "VERPLICHT - kies ALTIJD een letter: A, B, C, D of E (officiële Nutri-Score)",
  "nutrient_score": "VERPLICHT - geheel getal van 1 tot 10, geef ALTIJD een cijfer (1=zeer ongezond, 10=optimaal)",
  "score_uitleg": "korte uitleg waarom deze scores (VERPLICHT)",
  "gezondere_alternatieven": ["alternatief 1", "alternatief 2", "alternatief 3"]
}"""

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={"response_mime_type": "application/json"},
)

def _parse_json(text: str) -> dict:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise
        data = json.loads(text[start:end + 1])
    return _zorg_voor_scores(data)


def _zorg_voor_scores(data: dict) -> dict:
    letter_naar_score = {"A": 9, "B": 7, "C": 5, "D": 3, "E": 1}
    score_naar_letter = lambda s: "A" if s >= 9 else "B" if s >= 7 else "C" if s >= 5 else "D" if s >= 3 else "E"

    nutri = (data.get("nutri_score") or "").strip().upper()
    if nutri not in letter_naar_score:
        nutri = ""

    score_raw = data.get("nutrient_score")
    try:
        score = int(round(float(score_raw)))
    except (TypeError, ValueError):
        score = None

    if score is None and nutri:
        score = letter_naar_score[nutri]
    elif score is None:
        score = 5
        nutri = "C"

    if not nutri:
        nutri = score_naar_letter(score)

    data["nutri_score"] = nutri
    data["nutrient_score"] = max(1, min(10, score))

    naam = (data.get("product_naam") or "").strip()
    if not naam:
        naam = (data.get("samenvatting") or "Maaltijd").split(".")[0][:40].strip()
    data["product_naam"] = naam[:40]

    if not (data.get("emoji") or "").strip():
        data["emoji"] = "🍽️"
    return data

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
