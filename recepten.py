import streamlit as st
from urllib.parse import quote_plus

# Tags: maaltijd (ontbijt/lunch/diner/snack), dieet (vegetarisch/vegan/glutenvrij/hoog-eiwit/vezelrijk), stijl (mediterraan/aziatisch/mexicaans)
RECEPTEN = [
    # Ontbijt
    {"naam": "Havermout met blauwe bessen en walnoten", "tags": ["ontbijt", "vegetarisch", "vezelrijk"], "kort": "Langzame koolhydraten + antioxidanten."},
    {"naam": "Griekse yoghurt met granola en honing", "tags": ["ontbijt", "vegetarisch", "hoog-eiwit"], "kort": "Snel en eiwitrijk."},
    {"naam": "Avocado-toast met ei en chili", "tags": ["ontbijt", "vegetarisch", "hoog-eiwit"], "kort": "Romig vet + eiwit, perfect ontbijt."},
    {"naam": "Smoothie bowl met banaan en chiazaad", "tags": ["ontbijt", "vegan", "vezelrijk"], "kort": "Fris en vol vezels."},
    {"naam": "Volkoren pannenkoeken met aardbeien", "tags": ["ontbijt", "vegetarisch"], "kort": "Zoete, vezelrijke klassieker."},
    {"naam": "Roerei met spinazie en feta", "tags": ["ontbijt", "vegetarisch", "hoog-eiwit"], "kort": "Eiwitbom met groente."},
    {"naam": "Chia-pudding met kokos en mango", "tags": ["ontbijt", "vegan", "glutenvrij"], "kort": "Maak vooraf, eet direct."},
    {"naam": "Overnight oats met appel en kaneel", "tags": ["ontbijt", "vegan", "vezelrijk"], "kort": "Geen tijd? Avond ervoor klaarmaken."},
    {"naam": "Volkorenwrap met hummus en komkommer", "tags": ["ontbijt", "vegan"], "kort": "Hartig en licht."},
    {"naam": "Tofu-scramble met paprika", "tags": ["ontbijt", "vegan", "hoog-eiwit"], "kort": "Plantaardig alternatief voor roerei."},

    # Lunch
    {"naam": "Quinoa-salade met geroosterde groenten", "tags": ["lunch", "vegan", "vezelrijk", "mediterraan"], "kort": "Volwaardig en vullend."},
    {"naam": "Buddha bowl met zoete aardappel", "tags": ["lunch", "vegan", "vezelrijk"], "kort": "Kleurrijk en compleet."},
    {"naam": "Mediterrane couscoussalade", "tags": ["lunch", "vegetarisch", "mediterraan"], "kort": "Fris met olijven en feta."},
    {"naam": "Pompoensoep met kokosmelk", "tags": ["lunch", "vegan", "glutenvrij"], "kort": "Romig, zoet, troostend."},
    {"naam": "Linzensoep met curry", "tags": ["lunch", "vegan", "hoog-eiwit", "vezelrijk"], "kort": "Eiwitrijke maaltijdsoep."},
    {"naam": "Niçoise-salade met tonijn", "tags": ["lunch", "hoog-eiwit", "mediterraan"], "kort": "Frans klassiek, vol omega-3."},
    {"naam": "Kip-caesarsalade (light)", "tags": ["lunch", "hoog-eiwit"], "kort": "Lichtere versie van een klassieker."},
    {"naam": "Sushi bowl met zalm", "tags": ["lunch", "hoog-eiwit", "aziatisch"], "kort": "Alle sushi-smaken, makkelijker."},
    {"naam": "Falafel-wrap met tzatziki", "tags": ["lunch", "vegetarisch", "mediterraan"], "kort": "Krokant, fris en vullend."},
    {"naam": "Volkoren pasta-pesto met cherrytomaten", "tags": ["lunch", "vegetarisch", "mediterraan"], "kort": "Snel klaar, vol smaak."},
    {"naam": "Mexicaanse zwarte-bonensalade", "tags": ["lunch", "vegan", "hoog-eiwit", "mexicaans"], "kort": "Pittig en eiwitrijk."},
    {"naam": "Garnaal-mango-salade", "tags": ["lunch", "hoog-eiwit", "aziatisch"], "kort": "Zoet-pittige zomersalade."},
    {"naam": "Tonijn-avocado-poké-bowl", "tags": ["lunch", "hoog-eiwit", "aziatisch"], "kort": "Verse, gezonde bowl."},
    {"naam": "Hummus-bowl met rauwkost", "tags": ["lunch", "vegan", "vezelrijk"], "kort": "Crunchy én romig."},

    # Diner
    {"naam": "Zalm uit de oven met asperges", "tags": ["diner", "hoog-eiwit", "glutenvrij"], "kort": "30 minuten, max smaak."},
    {"naam": "Kip-tikka-masala (light)", "tags": ["diner", "hoog-eiwit"], "kort": "Indiaas klassiek, minder vet."},
    {"naam": "Vegetarische lasagne met spinazie", "tags": ["diner", "vegetarisch"], "kort": "Comfort food zonder gehakt."},
    {"naam": "Thaise groene curry met tofu", "tags": ["diner", "vegan", "aziatisch"], "kort": "Pittig, romig, plantaardig."},
    {"naam": "Gevulde paprika's met quinoa", "tags": ["diner", "vegan", "vezelrijk"], "kort": "Voedzaam en presenteerbaar."},
    {"naam": "Mexicaanse chili sin carne", "tags": ["diner", "vegan", "hoog-eiwit", "mexicaans"], "kort": "Vol eiwit en vezels."},
    {"naam": "Risotto met paddenstoelen", "tags": ["diner", "vegetarisch", "mediterraan"], "kort": "Romige troost zonder vlees."},
    {"naam": "Kip-shoarma met bloemkoolrijst", "tags": ["diner", "hoog-eiwit", "glutenvrij"], "kort": "Low-carb shoarma."},
    {"naam": "Indiase dahl met kikkererwten", "tags": ["diner", "vegan", "hoog-eiwit", "vezelrijk"], "kort": "Goedkoop en supergezond."},
    {"naam": "Marokkaanse tagine met kip en olijven", "tags": ["diner", "hoog-eiwit"], "kort": "Aromatisch one-pot."},
    {"naam": "Aziatische gewokte kip met cashew", "tags": ["diner", "hoog-eiwit", "aziatisch"], "kort": "15 minuten, krokant en vol smaak."},
    {"naam": "Kabeljauw-traybake met citroen", "tags": ["diner", "hoog-eiwit", "glutenvrij"], "kort": "Vis + groente, één plaat."},
    {"naam": "Couscous-tagine met groente", "tags": ["diner", "vegan", "vezelrijk"], "kort": "Vegan en aromatisch."},
    {"naam": "Bonen-quesadilla met avocado", "tags": ["diner", "vegetarisch", "mexicaans"], "kort": "Knapperig en smeuïg."},
    {"naam": "Aubergine-parmigiana", "tags": ["diner", "vegetarisch", "mediterraan"], "kort": "Italiaanse klassieker."},
    {"naam": "Garnalen-curry met basmatirijst", "tags": ["diner", "hoog-eiwit", "aziatisch"], "kort": "Romig en pittig."},
    {"naam": "Linzen-walnoot-bolognese", "tags": ["diner", "vegan", "hoog-eiwit"], "kort": "Plantaardige bolognese die voldoet."},
    {"naam": "Bloemkool-pizza met groente", "tags": ["diner", "vegetarisch", "glutenvrij"], "kort": "Low-carb pizza-fix."},

    # Snacks & smoothies
    {"naam": "Energy balls met dadels en cacao", "tags": ["snack", "vegan", "vezelrijk"], "kort": "Natuurlijk zoet, instant energie."},
    {"naam": "Hummus met groente-sticks", "tags": ["snack", "vegan", "hoog-eiwit"], "kort": "Klassieke gezonde dip."},
    {"naam": "Kwark met fruit en honing", "tags": ["snack", "vegetarisch", "hoog-eiwit"], "kort": "Eiwitrijke tussendoor."},
    {"naam": "Geroosterde kikkererwten met paprika", "tags": ["snack", "vegan", "hoog-eiwit"], "kort": "Krokant alternatief voor chips."},
    {"naam": "Edamame met zeezout", "tags": ["snack", "vegan", "hoog-eiwit"], "kort": "Eiwitbom, twee minuten klaar."},
    {"naam": "Groene smoothie met spinazie", "tags": ["snack", "vegan", "vezelrijk"], "kort": "Groente die je niet proeft."},
    {"naam": "Cacao-banaan smoothie", "tags": ["snack", "vegan"], "kort": "Romig en chocoladig."},
    {"naam": "Hardgekookt ei met avocado", "tags": ["snack", "vegetarisch", "hoog-eiwit"], "kort": "Snel en verzadigend."},
    {"naam": "Notenmix (ongezouten)", "tags": ["snack", "vegan", "vezelrijk"], "kort": "Handvol = perfect tussendoortje."},
]


def _zoek_link(naam: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(naam + ' recept')}"


def toon_recepten():
    st.html('<div class="section-title">Gezonde gerechten</div>')

    col1, col2 = st.columns([3, 2])
    with col1:
        zoek = st.text_input(
            "Zoeken", placeholder="Zoek op naam...", label_visibility="collapsed", key="recept_zoek"
        )
    with col2:
        alle_tags = sorted({t for r in RECEPTEN for t in r["tags"]})
        actieve = st.multiselect(
            "Filter", alle_tags, placeholder="Filter op tag", label_visibility="collapsed", key="recept_filter"
        )

    z = zoek.strip().lower()
    gefilterd = [
        r for r in RECEPTEN
        if (not z or z in r["naam"].lower() or any(z in t for t in r["tags"]))
        and (not actieve or all(t in r["tags"] for t in actieve))
    ]

    st.html(f'<div class="recipe-count">{len(gefilterd)} van {len(RECEPTEN)} gerechten</div>')

    if not gefilterd:
        st.html('<div class="recipe-empty">Geen gerechten gevonden. Pas je filter aan.</div>')
        return

    cards = "".join(
        f"""
        <a href="{_zoek_link(r['naam'])}" target="_blank" rel="noopener noreferrer" class="recipe-card">
          <div class="recipe-name">{r['naam']}</div>
          <div class="recipe-desc">{r['kort']}</div>
          <div class="recipe-tags">{''.join(f'<span class="recipe-tag">{t}</span>' for t in r['tags'])}</div>
          <div class="recipe-link">Bekijk recept ↗</div>
        </a>
        """
        for r in gefilterd
    )
    st.html(f'<div class="recipe-grid">{cards}</div>')
