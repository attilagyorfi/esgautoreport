# reports/suggestion_utils.py

# A szabályokat egy szótárban definiáljuk.
# Kulcs: A kérdés szövegének egy kulcsfontosságú, egyedi része.
# Érték: A javaslat, amit akkor adunk, ha a válasz 'Nem'.
SUGGESTION_RULES = {
    "szelektív hulladékgyűjtési politikával": "Fontolja meg egy szelektív hulladékgyűjtési politika bevezetését az ökológiai lábnyom csökkentése és az újrahasznosítási arány növelése érdekében.",
    "megújuló energiaforrásokat": "Vizsgálja meg a megújuló energiaforrásokra (pl. napenergia) való átállás lehetőségét az energiaköltségek és a szén-dioxid-kibocsátás csökkentése céljából.",
    "esélyegyenlőségi tervvel": "Dolgozzon ki és kommunikáljon egy esélyegyenlőségi tervet, hogy egy befogadóbb és sokszínűbb munkahelyi környezetet teremtsen.",
    "munkavállalói képzési program": "Indítson rendszeres munkavállalói képzési programokat a készségek fejlesztése és a munkavállalói elégedettség növelése érdekében.",
    "etikai kódexszel": "Hozzon létre és tegyen közzé egy etikai kódexet, amely világosan lefekteti a vállalati értékeket és az elvárt magatartási normákat.",
    "beszállítói lánc átvilágítását": "Végezzen rendszeres átvilágítást a beszállítói láncban az etikai és fenntarthatósági kockázatok azonosítása és kezelése érdekében."
}

def generate_suggestions(data_entries):
    """
    Végigmegy a vállalati adatbejegyzéseken és szabályok alapján javaslatokat generál.
    """
    suggestions = []
    
    # A 'Nem' válaszhoz tartozó ChoiceOption objektum azonosítója (ezt esetleg dinamikussá kell tenni)
    # Tegyük fel, hogy a 'Nem' válaszlehetőség a ChoiceOption modellben a 2-es ID-val rendelkezik.
    # Ezt az admin felületen lehet ellenőrizni, és szükség esetén módosítani!
    NO_OPTION_ID = 2 

    for entry in data_entries:
        # Ellenőrizzük, hogy a válasz egy 'Nem' típusú választás-e
        if entry.choice_option and entry.choice_option.id == NO_OPTION_ID:
            question_text = entry.data_point.text.lower()
            
            for keyword, suggestion in SUGGESTION_RULES.items():
                if keyword in question_text and suggestion not in suggestions:
                    suggestions.append(suggestion)

    return suggestions