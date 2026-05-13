import base64
import streamlit as st
from gemini_client import vraag_gemini, vraag_gemini_met_foto
from recepten import toon_recepten

st.set_page_config(page_title="Voeding-app", page_icon="🥗", layout="centered")

# ── State ──────────────────────────────────────────────────────────────
if "resultaat" not in st.session_state:
    st.session_state.resultaat = None
if "bron" not in st.session_state:
    st.session_state.bron = None
if "laatste_foto" not in st.session_state:
    st.session_state.laatste_foto = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "analyse"


def reset_resultaat():
    st.session_state.resultaat = None
    st.session_state.bron = None
    st.session_state.laatste_foto = None


# ── Styling ────────────────────────────────────────────────────────────
st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0e1f12;
        --card: #162a18;
        --card-2: #1d3520;
        --line: #25402b;
        --line-soft: #1f3623;
        --text: #ecf3ed;
        --muted: #a8bdad;
        --accent: #c89c70;
        --accent-2: #a67c52;
        --accent-soft: #2a2620;
        --good: #66bb6a;
        --warn: #d4925a;
        --bad: #c75450;
    }

    html, body, .stApp, button, input, textarea, select {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    body, .stApp { color: var(--text); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.2rem; padding-bottom: 4rem; max-width: 560px; }

    .stApp {
        background:
            radial-gradient(900px 500px at -10% -20%, #1a3520 0%, transparent 60%),
            radial-gradient(700px 400px at 110% 10%, #2a2620 0%, transparent 55%),
            linear-gradient(180deg, #0a1a0d 0%, #0e1f12 100%);
    }

    /* Hero ─ compact, functional */
    .hero {
        display: flex; align-items: center; gap: 0.8rem;
        padding: 0.4rem 0 1.2rem 0;
    }
    .hero-logo {
        width: 44px; height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        box-shadow: 0 4px 14px rgba(200,156,112,0.3);
    }
    .hero-text .hero-name { font-size: 1.15rem; font-weight: 800; letter-spacing: -0.01em; }
    .hero-text .hero-tag { font-size: 0.82rem; color: var(--muted); margin-top: 0.1rem; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
        background: var(--card);
        padding: 0.3rem;
        border-radius: 14px;
        border: 1px solid var(--line);
        margin-bottom: 0.8rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        color: var(--muted);
        flex: 1;
        justify-content: center;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important;
        color: #1a1410 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* Buttons */
    [data-testid="stButton"] > button {
        border-radius: 14px;
        font-weight: 700;
        padding: 0.85rem 1rem;
        border: none;
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    }
    [data-testid="stButton"] > button[kind="primary"] {
        background: var(--accent);
        color: #1a1410;
        box-shadow: 0 6px 20px rgba(200,156,112,0.25);
    }
    [data-testid="stButton"] > button[kind="primary"]:hover {
        background: var(--accent-2);
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(200,156,112,0.35);
        color: #1a1410;
    }
    [data-testid="stButton"] > button[kind="secondary"] {
        background: transparent;
        color: var(--muted);
        border: 1px solid var(--line);
    }
    [data-testid="stButton"] > button[kind="secondary"]:hover {
        background: var(--card);
        color: var(--text);
        border-color: var(--accent);
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background: var(--card) !important;
        color: var(--text) !important;
        border-radius: 14px !important;
        border: 1px solid var(--line) !important;
        padding: 0.9rem 1rem !important;
        font-size: 0.95rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(200,156,112,0.15) !important;
    }

    /* File / camera input */
    [data-testid="stFileUploader"] section, [data-testid="stCameraInput"] {
        background: var(--card);
        border: 1px dashed var(--line);
        border-radius: 14px;
    }

    /* Cards */
    .card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        margin-bottom: 0.8rem;
    }

    .summary-head {
        display: flex; align-items: flex-start; justify-content: space-between;
        gap: 0.8rem; margin-bottom: 0.8rem;
    }
    .summary-title { font-size: 1.1rem; font-weight: 700; line-height: 1.35; }
    .thumb {
        width: 64px; height: 64px;
        border-radius: 12px;
        object-fit: cover;
        border: 1px solid var(--line);
        flex-shrink: 0;
    }

    .pill-row { display: flex; gap: 0.4rem; flex-wrap: wrap; }
    .pill {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .pill-accent { background: var(--accent-soft); color: var(--accent); border: 1px solid rgba(200,156,112,0.25); }
    .pill-muted { background: var(--card-2); color: var(--muted); border: 1px solid var(--line); }

    /* Nutri-Score letterbalk */
    .nutriscore {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.25rem;
        margin: 0.2rem 0 1rem 0;
    }
    .ns-letter {
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: 800;
        border-radius: 6px;
        opacity: 0.3;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    .ns-letter.active {
        opacity: 1;
        transform: scale(1.35);
        box-shadow: 0 4px 14px rgba(0,0,0,0.4);
        font-size: 1.15rem;
        border-radius: 8px;
        margin: 0 0.25rem;
    }

    /* Score gauge */
    .gauge-wrap { display: flex; align-items: center; gap: 1.1rem; }
    .gauge-text { font-size: 0.92rem; color: var(--muted); line-height: 1.55; flex: 1; }

    /* Macros */
    .macro-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.65rem 0;
        border-bottom: 1px solid var(--line-soft);
        font-size: 0.95rem;
    }
    .macro-row:last-of-type { border-bottom: none; }
    .macro-label { color: var(--muted); font-weight: 500; }
    .macro-value { font-weight: 700; color: var(--text); }
    .macro-value .unit { color: var(--muted); font-weight: 500; font-size: 0.82rem; margin-left: 0.2rem; }

    .macro-mix {
        display: flex; height: 28px;
        border-radius: 10px; overflow: hidden;
        margin: 0.8rem 0 0.4rem 0;
        border: 1px solid var(--line);
    }
    .macro-seg {
        display: flex; align-items: center; justify-content: center;
        font-size: 0.72rem; font-weight: 700;
        color: rgba(20,20,16,0.85);
    }
    .seg-protein { background: var(--accent); }
    .seg-carb { background: var(--good); }
    .seg-fat { background: var(--warn); }
    .macro-legend {
        display: flex; gap: 0.9rem; flex-wrap: wrap;
        font-size: 0.78rem; color: var(--muted);
        margin-bottom: 0.2rem;
    }
    .macro-legend .dot {
        display: inline-block; width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 0.35rem; vertical-align: middle;
    }

    /* Vitamins */
    .vm-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.55rem;
    }
    .vm-item {
        background: var(--card-2);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    .vm-name { color: var(--muted); font-size: 0.82rem; }
    .vm-val { font-weight: 700; color: var(--accent); font-size: 0.95rem; }

    /* Alternatives */
    .alt-card {
        background: var(--card);
        border: 1px solid var(--line);
        border-left: 3px solid var(--accent);
        padding: 0.85rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.45rem;
        font-size: 0.93rem;
        line-height: 1.45;
    }

    /* Section headers */
    .section-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--accent);
        margin: 1.4rem 0 0.6rem 0;
    }

    /* Disclaimer */
    .disclaimer {
        text-align: center;
        font-size: 0.75rem;
        color: var(--muted);
        margin-top: 2rem;
        opacity: 0.7;
    }

    /* Recipes page */
    .recipe-count { color: var(--muted); font-size: 0.85rem; margin: 0.2rem 0 1rem 0; }
    .recipe-empty {
        text-align: center; padding: 2rem; color: var(--muted);
        border: 1px dashed var(--line); border-radius: 14px;
    }
    .recipe-grid { display: grid; grid-template-columns: 1fr; gap: 0.6rem; }
    .recipe-card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        text-decoration: none;
        color: var(--text);
        display: block;
        transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
    }
    .recipe-card:hover {
        border-color: var(--accent);
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.25);
    }
    .recipe-name { font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem; color: var(--text); }
    .recipe-desc { font-size: 0.85rem; color: var(--muted); line-height: 1.4; margin-bottom: 0.55rem; }
    .recipe-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-bottom: 0.55rem; }
    .recipe-tag {
        font-size: 0.7rem; padding: 0.18rem 0.55rem;
        background: var(--card-2); color: var(--muted);
        border-radius: 999px; border: 1px solid var(--line);
    }
    .recipe-link { font-size: 0.82rem; color: var(--accent); font-weight: 600; }

    /* Radio sub-label inside foto-tab */
    .or-divider {
        text-align: center;
        font-size: 0.78rem;
        color: var(--muted);
        margin: 0.4rem 0;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }
    </style>
    """
)

# ── Header ─────────────────────────────────────────────────────────────
st.html(
    """
    <div class="hero">
      <div class="hero-logo">🥗</div>
      <div class="hero-text">
        <div class="hero-name">Voeding-app</div>
        <div class="hero-tag">Voedingswaardes uit tekst of foto, met AI.</div>
      </div>
    </div>
    """
)

# ── Nav ────────────────────────────────────────────────────────────────
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    if st.button(
        "🥗 Analyse",
        key="nav_analyse",
        use_container_width=True,
        type="primary" if st.session_state.pagina == "analyse" else "secondary",
    ):
        st.session_state.pagina = "analyse"
        st.rerun()
with nav_col2:
    if st.button(
        "📖 Recepten",
        key="nav_recepten",
        use_container_width=True,
        type="primary" if st.session_state.pagina == "recepten" else "secondary",
    ):
        st.session_state.pagina = "recepten"
        st.rerun()

st.html('<div style="height: 0.8rem"></div>')

# ── Recepten-pagina ────────────────────────────────────────────────────
if st.session_state.pagina == "recepten":
    toon_recepten()
    st.html('<div class="disclaimer">Recept-links openen een Google-zoekopdracht.</div>')
    st.stop()

# ── Input area (alleen tonen als er nog geen resultaat is) ──────────────
if st.session_state.resultaat is None:
    tab_tekst, tab_foto = st.tabs(["✍️  Tekst", "📷  Foto"])

    with tab_tekst:
        maaltijd = st.text_area(
            "Wat heb je gegeten?",
            placeholder="bv. 2 boterhammen met kaas en een appel",
            height=110,
            key="tekst_input",
            label_visibility="collapsed",
        )
        if st.button("Analyseer maaltijd", type="primary", use_container_width=True, key="btn_tekst"):
            if maaltijd.strip() == "":
                st.warning("Vul eerst iets in.")
            else:
                with st.spinner("Gemini analyseert je maaltijd..."):
                    try:
                        st.session_state.resultaat = vraag_gemini(maaltijd)
                        st.session_state.bron = "tekst"
                        st.session_state.laatste_foto = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Er ging iets mis: {e}")

    with tab_foto:
        foto = st.file_uploader(
            "Upload foto",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        extra_context = st.text_input(
            "Extra context (optioneel)",
            placeholder="bv. grote portie, ongeveer 300g",
        )
        if st.button("Analyseer foto", type="primary", use_container_width=True, key="btn_foto"):
            if foto is None:
                st.warning("Voeg eerst een foto toe.")
            else:
                with st.spinner("Gemini bekijkt je foto..."):
                    try:
                        foto_bytes = foto.getvalue()
                        st.session_state.resultaat = vraag_gemini_met_foto(foto_bytes, extra_context)
                        st.session_state.bron = "foto"
                        st.session_state.laatste_foto = foto_bytes
                        st.rerun()
                    except Exception as e:
                        st.error(f"Er ging iets mis: {e}")

# ── Resultaat ──────────────────────────────────────────────────────────
NUTRI_KLEUREN = {"A": "#038141", "B": "#85bb2f", "C": "#fecb02", "D": "#ee8100", "E": "#e63e11"}


def render_nutriscore(letter: str) -> str:
    actief = (letter or "").strip().upper()
    blokken = "".join(
        f'<span class="ns-letter {"active" if l == actief else ""}" style="background:{kleur}">{l}</span>'
        for l, kleur in NUTRI_KLEUREN.items()
    )
    return f'<div class="nutriscore">{blokken}</div>'


def render_gauge(score: float) -> str:
    if score >= 8:
        kleur_hex = "#66bb6a"
    elif score >= 5:
        kleur_hex = "#d4925a"
    else:
        kleur_hex = "#c75450"
    radius = 46
    circumference = 2 * 3.14159 * radius
    dash = circumference * (max(0, min(10, score)) / 10)
    return f"""
    <svg width="120" height="120" viewBox="0 0 120 120">
      <circle cx="60" cy="60" r="{radius}" stroke="#25402b" stroke-width="10" fill="none"/>
      <circle cx="60" cy="60" r="{radius}" stroke="{kleur_hex}" stroke-width="10" fill="none"
              stroke-linecap="round" stroke-dasharray="{dash} {circumference}"
              transform="rotate(-90 60 60)"/>
      <text x="60" y="58" text-anchor="middle" font-size="28" font-weight="800" fill="#ecf3ed">{int(round(score))}</text>
      <text x="60" y="80" text-anchor="middle" font-size="11" fill="#a8bdad">/ 10</text>
    </svg>
    """


def render_macro_mix(eiwit_g: float, koolh_g: float, vet_g: float) -> str:
    p_kcal = eiwit_g * 4
    c_kcal = koolh_g * 4
    f_kcal = vet_g * 9
    total = p_kcal + c_kcal + f_kcal
    if total == 0:
        return ""
    p, c, f = (p_kcal / total) * 100, (c_kcal / total) * 100, (f_kcal / total) * 100
    return f"""
    <div class="macro-legend">
      <span><span class="dot" style="background:var(--accent)"></span>Eiwit {p:.0f}%</span>
      <span><span class="dot" style="background:var(--good)"></span>Koolhydraten {c:.0f}%</span>
      <span><span class="dot" style="background:var(--warn)"></span>Vet {f:.0f}%</span>
    </div>
    <div class="macro-mix">
      <div class="macro-seg seg-protein" style="width:{p}%"></div>
      <div class="macro-seg seg-carb" style="width:{c}%"></div>
      <div class="macro-seg seg-fat" style="width:{f}%"></div>
    </div>
    """


if st.session_state.resultaat:
    data = st.session_state.resultaat

    thumb_html = ""
    if st.session_state.bron == "foto" and st.session_state.laatste_foto:
        b64 = base64.b64encode(st.session_state.laatste_foto).decode()
        thumb_html = f'<img src="data:image/jpeg;base64,{b64}" class="thumb" alt="foto"/>'

    bron_label = "📷 Foto" if st.session_state.bron == "foto" else "✍️ Tekst"

    st.html(
        f"""
        <div class="card">
          <div class="summary-head">
            <div class="summary-title">{data['samenvatting']}</div>
            {thumb_html}
          </div>
          <div class="pill-row">
            <span class="pill pill-accent">⚖️ {data['portie_schatting']}</span>
            <span class="pill pill-muted">{bron_label}</span>
          </div>
        </div>
        """
    )

    st.html('<div class="section-title">Nutri-Score</div>')
    st.html(
        f"""
        <div class="card">
          {render_nutriscore(data.get('nutri_score', ''))}
        </div>
        """
    )

    st.html('<div class="section-title">Gezondheidsscore</div>')
    st.html(
        f"""
        <div class="card">
          <div class="gauge-wrap">
            {render_gauge(float(data['nutrient_score']))}
            <div class="gauge-text">{data['score_uitleg']}</div>
          </div>
        </div>
        """
    )

    st.html('<div class="section-title">Macronutriënten</div>')
    mix_html = render_macro_mix(
        float(data['eiwitten_g']), float(data['koolhydraten_g']), float(data['vetten_g'])
    )
    st.html(
        f"""
        <div class="card">
          <div class="macro-row"><span class="macro-label">🔥 Calorieën</span><span class="macro-value">{data['calorieen_kcal']}<span class="unit">kcal</span></span></div>
          <div class="macro-row"><span class="macro-label">🥩 Eiwitten</span><span class="macro-value">{data['eiwitten_g']}<span class="unit">g</span></span></div>
          <div class="macro-row"><span class="macro-label">🍞 Koolhydraten</span><span class="macro-value">{data['koolhydraten_g']}<span class="unit">g</span></span></div>
          <div class="macro-row"><span class="macro-label">🥑 Vetten</span><span class="macro-value">{data['vetten_g']}<span class="unit">g</span></span></div>
          <div class="macro-row"><span class="macro-label">🌾 Vezels</span><span class="macro-value">{data['vezels_g']}<span class="unit">g</span></span></div>
          <div class="macro-row"><span class="macro-label">🍬 Suikers</span><span class="macro-value">{data['suikers_g']}<span class="unit">g</span></span></div>
          {mix_html}
        </div>
        """
    )

    st.html('<div class="section-title">Vitamines & mineralen</div>')
    vm = data["vitamines_mineralen"]
    items = "".join(
        f'<div class="vm-item"><span class="vm-name">{naam.replace("_mg","").replace("_ug","").replace("_"," ").title()}</span><span class="vm-val">{waarde} mg</span></div>'
        for naam, waarde in vm.items()
    )
    st.html(f'<div class="card"><div class="vm-grid">{items}</div></div>')

    st.html('<div class="section-title">🌱 Gezondere alternatieven</div>')
    alts = "".join(f'<div class="alt-card">{alt}</div>' for alt in data["gezondere_alternatieven"])
    st.html(alts)

    st.button("↻ Nieuwe analyse", type="secondary", use_container_width=True, on_click=reset_resultaat)

st.html(
    '<div class="disclaimer">Schattingen door AI — niet voor medisch gebruik.</div>'
)
