import streamlit as st
import pandas as pd
import re
import numpy as np
from io import BytesIO
from datetime import datetime

# Set page configuration first
st.set_page_config(page_title="Product Validation", layout="wide", initial_sidebar_state="expanded")

st.title("✅ Product Validation – NordicFeel Template")

# Define validation constants
# Main categories
VALID_MAIN_CATEGORIES = ["Makeup", "Hårvård", "Parfym", "Hudvård"]

# Secondary categories by main category
VALID_SECONDARY_CATEGORIES = {
    "Makeup": ["Ansikte_makeup", "Läppar", "Naglar", "Set_och_paletter", "Sminkverktyg", "Ögon"],
    "Hårvård": ["Schampo_och_balsam", "Hårstyling", "Treatment", "Hårfärg_och_toning", 
                "Hårborste_och_tillbehör", "Värmeverktyg", "Hårparfym", "Hårvårdskit", 
                "Skäggvård_och_styling"],
    "Parfym": ["Damparfym", "Herrparfym", "Unisexparfym", "Parfym_gift_set", "Body_mist"],
    "Hudvård": ["Ansikte_hudvård", "Kropp", "Sol", "Beauty_tech", "Hudvårdsverktyg", 
                "Hårborttagning", "Presenter_Hudvårdskit"]
}

# Third categories by main category
VALID_THIRD_CATEGORIES = {
    "Makeup": [
        "Bronzer", "Concealer", "Contouring", "Foundation", "Highlighter", "Primer", 
        "Puder", "Rouge_och_blush", "Setting_spray", "Läppglans", "Läppenna", "Läppstift", 
        "Läppvård", "Lip_stain_och_tint", "Lip_plumber", "Lösnaglar", "Nagellack", 
        "Nagellackborttagning", "Nagelvård", "Gellack", "Bas/Topplack", "Makeup_set", 
        "Sminkpaletter", "Ögonskuggspaletter", "Blotting_papers", "Pennvässare", "Pincett", 
        "Sminkborstar_och_penslar", "Sminkspeglar", "Ögonbrynskniv_och_trimmers", 
        "Ögonfransböjare", "Eyeliner_och_kajal", "Färgade_linser", "Lösögonfransar", 
        "Mascara", "Ögonbryn", "Ögonfransserum_och_brynsserum", "Ögonprimer", "Ögonskugga"
    ],
    "Hårvård": [
        "Schampo", "Balsam", "Silverschampo", "Silverbalsam", "Torrschampo", "Balsamspray", 
        "Detoxschampo", "Glansspray", "Hårgel", "Hårvax", "Hårspray", "Mousse", "Saltvattenspray", 
        "Stylingcreme", "Värmeskydd", "Volym", "Hårinpackning", "Hårolja", "Leave_in_conditioner", 
        "Vårdande_produkter", "Solskydd_för_hår", "Hårserum", "Scalp_Treatment", "Hårfärg", "Avfärgning", 
        "Blondering_och_blekning", "Färginpackning_och_färgbomb", "Färgtillbehör", "Tillfällig_färg", 
        "Toning", "Hårborstar", "Löshår", "Pumpar", "Kammar", "Hårfön_och_hårtork", "Locktång", 
        "Plattång", "Vågtång_och_krustång", "Värmeborste", "Värmespolar", "Skäggolja"
    ],
    "Parfym": [
        "Gist_set_dam", "Gift_set_herr", "Eau_de_toilette_dam", "Eau_de_parfum_dam", 
        "Parfum_dam", "Eau_de_toilette_herr", "Eau_de_parfum_herr", "Parfum_herr", 
        "Eau_de_toilette_unisex", "Eau_de_parfum_unisex", "Parfum_unisex"
    ],
    "Hudvård": [
        "Ansiktskräm", "Ansiktsmask", "Ansiktsolja", "Ansiktsrengöring", "Ansiktsskrubb_och_peeling", 
        "Ansiktsvatten", "Dermaroller", "Ögonmask", "Hals_och_dekolletage", "Spot_treatment", 
        "Serum", "Sminkborttagning", "Ögonkräm", "Ögonserum", "Badbomber_badskum_och_badolja", 
        "Body_lotion", "Deodorant", "Duschtvål", "Handvård_och_fotvård", "Hudserum_och_kroppsolja", 
        "Body_scrub", "After_sun", "Brun_utan_sol", "Solskydd_och_solkräm", "Epilator_och_trimmer", 
        "Hårborttagningskräm_och_vax", "IPL", "Rakning", "Ansikte_hudvårdskit", "Kropp_hudvårdskit"
    ]
}

# Fourth categories by main category
VALID_FOURTH_CATEGORIES = {
    "Makeup": [
        "Bronzer_stick", "BB_cream", "CC_cream", "Blush_Stick", "Läppskrubb", "Läppbalsam", 
        "Nagelsax", "Ansikte_sminkborstar", "Läppar_sminkborstar", "Makeupsvamp", 
        "Rengöring_sminkborstar", "Set_sminkborstar", "Ögon_sminkborstar", "Ögonbryn_sminkborstar", 
        "Vattenfast_mascara", "Ögonbrynsgel_och_mascaror", "Ögonbrynsfärg", "Ögonbrynspenna_och_puder"
    ],
    "Hårvård": ["Volympuder", "Volymspray"],
    "Parfym": [],
    "Hudvård": [
        "Dagkräm", "Nattkräm", "Dagkräm_med_SPF", "Sheet_mask", "Lermask", "Ansiktsmask_mot_pormaskar", 
        "Ansiktsborstar_och_rengöringsborstar", "Cleansing_oil", "Rengöringsmjölk", "Rengöringsgel", 
        "Rengöringsskum", "Rengöringsservetter", "Cleansing_balm", "Micellärvatten", "Toner", "Essence", 
        "Face_mist", "Hyaluronsyraserum", "Retionalserum", "Vitamin_C_serum", "Niacinamideserum", 
        "Body_butter", "Damdeodorant", "Herrdeodorant", "Duscholja", "Handtvål", "Handkräm", "Fotvård", 
        "Handsprit", "Tanning_drops", "Brun-utan-sol_för_ansiktet", "Brun-utan-sol_för_kroppen", 
        "Solkräm_för_ansiktet", "Solkräm_för_kroppen", "Rakapparat", "Rakhyvel", "After_shave", "Rakgel"
    ]
}

# Other validation lists
VALID_GENDER_OPTIONS = ["Dam", "Herr", "Unisex"]

VALID_COLOR_OPTIONS = [
    "Aprikos", "Beige", "Blå", "Blond", "Brun", "Flerfärgad", "Grå", "Grön", 
    "Gul", "Guld", "Koppar", "Lila", "Ljus", "Medium", "Mörk", "Mörkbrun", 
    "Mörkröd", "Orange", "Röd", "Rosa", "Silver", "Svart", "Transparent", "Turkos", "Vit"
]

VALID_SUSTAINABLE_BEAUTY_OPTIONS = [
    "Alkoholfri", "Doftfri", "Ekologisk", "Parabenfri", "Parfymfri", 
    "Refill", "Refillable", "Silikonfri", "Sulfatfri", "Vegansk"
]

VALID_PRODUCT_TYPE_OPTIONS = [
    "Antiperspirant", "Ask", "Balm", "Böjd borste", "Deospray", "Deostick", 
    "EdC", "EdP", "EdT", "Elektrisk", "Flaska", "Flerpack", "Flytande", "För barn", 
    "Gel", "Giftset", "Kräm", "Lotion", "Med SPF", "Mousse", "Olja", "Paddelborste", 
    "Pads", "Paletter", "Parfum", "Penna", "Pensel", "Puder", "Pump", "Rak borste", 
    "Roll-on", "Rundborste", "Spray", "Stick", "Tillbehör", "Tub", "Wipes"
]

VALID_SKIN_TYPE_OPTIONS = [
    "Acne", "Blandhy", "Fet", "Känslig", "Mogen", "Torr", "Ung hy"
]

VALID_TRAIT_OPTIONS = [
    "Anti-age", "Anti-friss", "Avlägsnar vattenfast", "Bättre lockar", "Djuprengörande", 
    "Exfolierande", "Fransseparerande", "Färgbevarande", "Förlängande", "Glansförstärkande", 
    "Jämnar ut hudton", "Kylande", "Lugnande", "Lyster", "Mattifierande", "Minskar porer", 
    "Mjukgörande", "Plumping", "Snabbtorkande", "Stärkande", "Texturgivande", "Utjämnande", 
    "Vattenfast", "Vattenresistent", "Volymgivande", "Värmeskyddande", "Återfuktande"
]

VALID_SKIN_CONDITION_OPTIONS = [
    "Acne", "Blank hy", "Fina linjer", "Finnar", "Fuktfattig", "Förstorade porer", 
    "Lysterlös", "Mörka ringar", "Ojämn hudstruktur", "Pigmenteringar", "Påsar", 
    "Rodnad", "Rosacea", "Rynkor", "Slapp hy", "Svullnad"
]

VALID_HAIR_TYPE_OPTIONS = [
    "Blont", "Färgat", "Fett", "Frissigt", "Håravfall", "Känslig hårbotten", 
    "Lockigt", "Mjäll", "Skadat", "Tjockt", "Torrt", "Tunt"
]

VALID_COVERAGE_OPTIONS = ["Full", "Lätt", "Medium"]

VALID_FRAGRANCE_FAMILY_OPTIONS = [
    "Akvatisk", "Amber", "Aromatisk", "Blommig", "Chypré", "Citrus", 
    "Fougère", "Fruktig", "Gourmand", "Läder", "Orientalisk", "Träig", "Vanilj"
]

VALID_SPF_OPTIONS = ["SPF <15", "SPF 15-25", "SPF 30-40", "SPF 50+"]

VALID_FINISH_OPTIONS = ["Glitter", "Lyster", "Matt", "Metallic", "Neutral"]

VALID_ACTIVE_INGREDIENTS_OPTIONS = [
    "AHA-syra", "Aloe_vera", "Bakuchiol", "BHA-syra", "C-vitamin", "CBD", 
    "Ceramider", "Cica", "E-vitamin", "Hyaluronsyra", "LHA-syra", "Niacinamide", 
    "Peptider", "PHA-syra", "Retionol", "Salicylsyra"
]

# Parse notes lists from raw text
def parse_notes(raw_text):
    return [note.strip() for note in raw_text.split("\n") if note.strip()]

# Top notes
TOP_NOTES_RAW = """Absint
Agave
Aldehyd
Ambrette
Ananas
Angelika
Apelsin
Apelsinblomma
Aromatiska ackord
Artemisia
Bambu
Basilika
Bergamot
Bitter apelsin
Bittermandel
Björkblad
Björnbär
Blodapelsin
Blomackord
Blåbär
Blåklocka
Boysenbär
Bär
Cactus
Calone
Cascalone
Cassis
Ceder
Cederlöv
Cistus
Citron
Citrus
Clementin
cottonCandy
Cypress
Daggbris
Damaskusros
Davana
Dragon
Drakfrukt
Elemi
Elemi absolute
Enbär
Eukalyptus
Fikon
Fikonkaktus
Fikonlöv
Finger lime
Frangipani
Fresia
Fruktig
Fänkol
Galbanum
Gardenia
Gentiana
Geranium
Gin
Gourmandbär
Granatäpple
Grapefrukt
Gräs
Gröna ackord
Gurkmeja
Hallon
Hav
Heliotrop
Honung
Honungsmelon
Ingefära
Ingefärablommor
Iris
Jasmine
Jordgubbar
Kamomill
Kanderat äpple
Kanel
Kaprifol
Karamelliserat socker
Kardemumma
Kashmirträ
Kassia
Kiwi
Kokosnöt
Koriander
Krut
Kryddnejlika
Kvitten
Körsbär
Körsbärsblomma
Labdanum
Labdanum ciste
Lavandin
Lavendel
Lilja
Liljekonvalj
Lime
Litchi
Lotus
Luktärt
Magnolia
Malört
Mandarin
Mandel
Mandora
Mango
Maninka
Marshmallow
Mate
Melon
Mimosa
Muskotnöt
Mynta
Nashipäron
Nektarin
Neroli
Olibanum
Oregano
Orris
Osmanthus
Ozonackord
Papaya
Papayablomma
Passionsblomma
Passionsfrukt
Peppar
Pepparmynta
Persika
Persimon
Petitgrain
Pimento
Pion
Pistasch
Plommon
Pomerans
Päron
Päronblomna
Rabarber
Regnackord
Ringblomma
Rom
Ros
Rosa blommor
Rosa pepparkorn
Rosépeppar
Roslikör
Rosmarin
Röda bär
Röda frukter
Röda vinbär
Rökelse
Saffran
Saftig kiwi
Salt
Salvia
Solackord
Spiskummin
Stjärnanis
Svarta körsbär
Svartpeppar
Svartvinbär
Syrén
Tangerin
Tonic
Tuberose
Vanilj
Vattenmelon
Vin
Vinackord
Viol
Violblad
Vita blommor
Vitt te
Ylang-ylang
Yuzu
Äpple
Örtackord"""

# Heart notes
HEART_NOTES_RAW = """Amaryllis
Amber
Ambrette
Ambroxan
Ananas
Apelsinblomma
Aprikos
Bambu
Basilika
Benzoin
Bergamot
Björk
Björklöv
Blomblad
Buchuruta
Casablancalilja
Cederträ
Citron
Citrus
Cypress
Cypriol
Damaskusros
Datura
Davana
Dragon
Drivved
Ekmossa
Elemi
Enbär
Eukalyptus
Fikon
Frangipani
Fresia
Galbanum
Gardenia
Gentania
Gentian absolute
Geranium
Granbalsam
Grönt te
Guaiacträd
Guava
Gul näckros
Hallon
Hasselnöt
Hav
Hedion
Heliotrop
Hiacynt
Hibiskus
Honung
Ingefära
Ingefärslilja
Iris
Jasmin sambac
Jasmine
Jonquille
Jordgubbe
Kaffe
Kakao
Kanel
Kaprifol
Karamell
Kardemumma
Kashirträ
Kaviar
Kokosnöt
Kola
Koriander
Kryddnejlika
Kummin
Kvanne
Kvitten
Körsbär
Körsbärsblomma
Labdanum
Lagerblad
Lavandin
Lavendel
Lavendelhonung
Lilja
Liljekonvalj
Lin
Litchi
Lotus
Luktärt
Läder
Magnolia
Mahogany
Makroner
Mandarin
Mandel
Mandelmjölk
Maninka
Marshmallow
Mate absolute
Mimosa
Mirabell
Mocka
Mossa
Murgröna
Muskot
Mynta
Myrra
Mysk
Narciss
Nejlika
Nektarin
Neroli
Näckros
Olibanum
Olivblommor
opoponax
Orkidé
Orris
Osmanthus
Paprika
Papyrus
Patchouli
Peppar
Pepparkaka
Pepparmynta
Persika
Persikoblommor
Petalia
Petitgrain
Pion
Plommon
Pomarose
Popcorn
Portvin
Päron
Päronblomma
Rabarber
Ringblomma
Ros
Rosa cyklamen
Rosa pepparkorn
Rosenknoppar
Rosenträ
Rosépeppar
Rosmarin
Röd chili
Rökelse
Saffran
Salta mineraler
Salvia
Sandelträ
Sapucaya
Sockrad mandel
Stjärnfrukt
Strandlilja
Svart te
Svarta vinbär
Svartpeppar
Syrén
Szechuanpeppar
Sötgräs
Tagetes
Tall
Tiareblomma
Timjan
Tobak
Tonkaböna
Trä
Tuberos
Vanilj
Vattenackord
Vattenmelon
Verbena
Vetiver
Viol
Violblad
Vispgrädde
Vit kaktus
Vita blommor
Vita pepparkorn
Vitt te
Ylang-ylang
Äpple"""

# Base notes
BASE_NOTES_RAW = """Agarträ
Akigalaträ
Amber
Ambertonic
Ambra
Ambrette
Ambroxan
Apelsinblomma
Aprikos
Balsamträ
Benzoin
Bivax
Björk
Blomstertobak
Blåbär
Brunt socker
Cade
Cashmeran
Castoreum
Cederträ
Clearwood
Cognac
Cypress
Cypriol
Ebenholts
Ekmossa
Ekträ
Enbär
Galbanum
Grapefrukt
Grädde
Gräsrot
Guaiacträd
Hasselnöt
Heliotrop
Hinokiträ
Honung
Hyacint
Iris
Iso E Super
Jasmine
Järnträ
Kaffe
Kakao
Kanel
Karamell
Kardemumma
Kashmirträ
Kastanj
Kokosnöt
Konfektyr
Kryddnejlika
Kumarin
Kummin
Kåda
Labdanum
Labdanum resinoid
Lakrits
Ljust trä
Läder
Läderträ
Madrasträ
Makroner
Mandel
Mandelmjölk
Marshmallow
Mate absolute
Mjölk
Mocka
Mossa
Muskotnöt
Mynta
Myrra
Mysk
Mörk choklad
Neroli
Olibanum
Olivträd
Opoponax
Orris
Osmanthus
Oud
Papyrus
Patchouli
Peppar
Perubalsam
Plommon
Pralin
Rangoon creeper
Ros
rosePepper
Röda bär
Rökelse
Rött äpple
Salvia
Sandelträ
Santal
Skog
Socker
Styraxharts
Svartpeppar
Svartvinbär
Sylkoldie
Tall
Tobak
Tonkaböna
Tryffel
Trä
Tuberos
Vanilj
Vetiver
Viol
Vit mocka
Ylang-ylang"""

# Parse the notes
VALID_TOP_NOTES_OPTIONS = parse_notes(TOP_NOTES_RAW)
VALID_HEART_NOTES_OPTIONS = parse_notes(HEART_NOTES_RAW)
VALID_BASE_NOTES_OPTIONS = parse_notes(BASE_NOTES_RAW)

# Additional validation constants
VALID_CURRENCIES = ["SEK", "NOK", "EUR", "DKK", "DK", "sek", "nok", "eur", "dkk", "dk"]
VALID_UNITS = ["ml", "g", "pcs", "st", "set", "kit", "pack"]

# Regular expression patterns for validation
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$')
HEX_COLOR_PATTERN = re.compile(r'^#[0-9a-fA-F]{6}$')
# Updated UN Number pattern to accept "UN" prefix and Excel comma-formatting
UN_NUMBER_PATTERN = re.compile(r'^(UN)?(\d{1,2},\d{2}|\d{4})$', re.IGNORECASE)

# Function to check if a value is numeric
def is_numeric(val):
    """Check if value can be converted to a number."""
    try:
        val = str(val).strip().replace('\xa0', '').replace(',', '.')
        if val.lower() in ["", "nan", "none"]:
            return False
        float(val)
        return True
    except (ValueError, TypeError):
        return False

# Function to validate date format
def is_valid_date(date_str):
    """Check if a string is a valid date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."""
    if not DATE_PATTERN.match(date_str):
        return False

    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S'):
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False

# Function to normalize text for comparison
def normalize(val):
    """Normalize a value for comparison (lowercase and strip)."""
    return str(val).strip().lower() if pd.notna(val) else ""

# Function to validate multi-select values (for fields with multiple choices separated by ;)
def validate_multi_select(value, valid_options):
    """Validate a multi-select field (values separated by semicolons)."""
    if not value or pd.isna(value):
        return True, []
    
    values = [v.strip() for v in str(value).split(';')]
    invalid_values = [v for v in values if v and v not in valid_options]
    return not bool(invalid_values), invalid_values

# Sidebar configuration
with st.sidebar:
    st.header("Settings")
    show_all_columns = st.checkbox("Show all columns", value=False)
    enable_advanced_validation = st.checkbox("Activate advanced validation", value=True)
    
    st.subheader("Filter results")
    filter_by = st.radio(
        "Filter by:",
        ["All", "All with errors", "All without errors"]
    )
    
    st.divider()
    
    with st.expander("⚙️ Show instructions", expanded=False):
        
        st.info("Upload an Excel file with product data for validation. The system checks that the information complies with NordicFeel's specifications for product uploads.")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Data loading and processing in tabs
        tabs = st.tabs(["Validation", "Raw Data", "Statistics"])
        
        # Create a copy of the file to allow multiple reads
        file_copy = BytesIO(uploaded_file.getvalue())
        
        # Try to find the right sheet name
        sheet_names = pd.ExcelFile(file_copy).sheet_names
        product_sheet_name = None
        
        # Look for possible product template sheets
        possible_names = ["Products", "Product Template", "NordicFeel Product Template", "Template", "Youty Product Template"]
        for name in sheet_names:
            if any(possible in name for possible in possible_names):
                product_sheet_name = name
                break
                
        # If no matching name found, use the first sheet
        if not product_sheet_name and sheet_names:
            product_sheet_name = sheet_names[0]
            
        if not product_sheet_name:
            st.error("Kunde inte hitta produktblad i Excel-filen")
            st.stop()
            
        # Read the data from Excel
        df = pd.read_excel(file_copy, sheet_name=product_sheet_name, header=None)
        st.sidebar.info(f"Filen innehåller {len(sheet_names)} flikar: {', '.join(sheet_names)}")
        st.sidebar.success(f"Använder flik: {product_sheet_name}")

        # Extract headers from row 2 (index 1)
        headers = df.iloc[1].tolist()
        headers = [str(h).strip() if pd.notna(h) else f"Unnamed_{i}" for i, h in enumerate(headers)]
        
        # Deduplicate column headers
        def deduplicate_columns(columns):
            seen = {}
            result = []
            for col in columns:
                if col not in seen:
                    seen[col] = 0
                    result.append(col)
                else:
                    seen[col] += 1
                    result.append(f"{col}.{seen[col]}")
            return result

        # Keep the original order of columns
        deduped_headers = deduplicate_columns(headers)
        original_column_order = deduped_headers.copy()

        # Determine where the actual data starts
        # Usually row 4 (index 3) contains examples
        # Look at row 5 (index 4) to decide if it's real data or not
        first_data_row = df.iloc[4]
        ean_candidate = str(first_data_row[headers.index("EAN")] if "EAN" in headers else "").strip()
        
        # If row 5 looks like example data, start from row 6 (index 5), otherwise from row 5 (index 4)
        start_row = 5 if ean_candidate in ["0737052972268", "Example", "Exempel", ""] else 4

        # Extract the data, set the headers
        data = df.iloc[start_row:].copy()
        data.columns = deduped_headers
        
        # Filter out rows with all empty or formula placeholder values
        # Check for actual content (not just formulas)
        def has_actual_content(row):
            # Look at important columns to determine if this is a real data row
            # EAN is mandatory, so if it's missing/empty it's not a real row
            ean_col = "EAN"
            if ean_col in row:
                ean_value = str(row[ean_col]).strip()
                if ean_value and not ean_value.startswith("=") and ean_value.lower() not in ["nan", "none", ""]:
                    return True
            return False
        
        # Filter rows with actual content
        data = data[data.apply(has_actual_content, axis=1)]
        data.reset_index(drop=True, inplace=True)

        # Show raw data tab
        with tabs[1]:  # Raw data tab
            st.subheader("Rådata från Excel")
            st.dataframe(data, use_container_width=True)

        st.success(f"Filen laddades in – {len(data)} rader att kontrollera.")

        # Prepare for validation
        cell_issues = {}
        summary_rows = []
        styled_summary_data = []

        # Validate each row
        for idx, row in data.iterrows():
            row_num = idx + start_row + 1
            summary_row = {"Radnummer": row_num}
            styled_row = {}
            issue_count = 0

            # Process all columns in the original order
            for col in original_column_order:
                val = str(row.get(col, "")).strip() if pd.notna(row.get(col, "")) else ""
                
                # Main Category validation
                if col == "Main Category":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Fält saknas – välj huvudkategori"
                        issue_count += 1
                    elif val not in VALID_MAIN_CATEGORIES:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Ogiltig huvudkategori"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Secondary Category validation
                elif col == "Secondary Category":
                    main_val = str(row.get("Main Category", "")).strip() if "Main Category" in row else ""
                    
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Välj en subkategori"
                        issue_count += 1
                    elif main_val in VALID_SECONDARY_CATEGORIES and val not in VALID_SECONDARY_CATEGORIES[main_val]:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Välj en existerande subkategori"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Third Category validation
                elif col == "Third Category":
                    main_val = str(row.get("Main Category", "")).strip() if "Main Category" in row else ""
                    
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif main_val in VALID_THIRD_CATEGORIES and val not in VALID_THIRD_CATEGORIES[main_val]:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Välj en existerande subkategori"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                            
                # Fourth Category validation
                elif col == "Fourth Category":
                    main_val = str(row.get("Main Category", "")).strip() if "Main Category" in row else ""
                    
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif main_val in VALID_FOURTH_CATEGORIES and val not in VALID_FOURTH_CATEGORIES[main_val]:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Välj en existerande subkategori"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # EAN validation - simplified to only check if empty
                elif col == "EAN":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ EAN saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Vendor Item Number validation
                elif col == "Vendor Item Number":
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ {val}"
                
                # If Relaunch, Enter Old EAN validation
                elif "old ean" in col.lower():
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ {val}"
                
                # Limited Edition validation
                elif "limited" in col.lower() or "limited edition" in col.lower():
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ {val}"
                
                # Launch Date validation
                elif col == "Launch Date":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid_date(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Felaktigt datumformat, använd YYYY-MM-DD"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # Purchasing Date validation
                elif col == "Purchasing Date":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid_date(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Felaktigt datumformat, använd YYYY-MM-DD"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Brand Name validation
                elif col == "Brand Name":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Varumärke saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                        
                # Product Name validation - removed capitalization check
                elif col == "Product Name":
                    brand_val = str(row.get("Brand Name", "")).strip() if "Brand Name" in row else ""
                    
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Produktnamn saknas"
                        issue_count += 1
                    else:
                        issues = []
                        
                        # Check for brand name in product name
                        if brand_val and brand_val.lower() in val.lower():
                            issues.append("Produktnamn innehåller varumärke")
                        
                        # Check for abbreviations (simple check for short words with periods)
                        if re.search(r'\b[A-Za-z]{1,2}\.\b', val):
                            issues.append("Inga förkortningar")
                        
                        # Check for volume info
                        if re.search(r'\d+\s*(ml|g|pcs)', val.lower()):
                            issues.append("Volym ska inte anges här")
                        
                        if issues:
                            cell_issues[(idx, col)] = "yellow"
                            styled_row[col] = f"⚠️ {', '.join(issues)}"
                            issue_count += 1
                        else:
                            cell_issues[(idx, col)] = "green"
                            styled_row[col] = f"✅ {val}"

                # Product Name 2 validation - removed capitalization check
                elif col == "Product Name 2":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    else:
                        issues = []
                        
                        # Check for abbreviations
                        if re.search(r'\b[A-Za-z]{1,2}\.\b', val):
                            issues.append("Inga förkortningar")
                        
                        # Check for volume info
                        if re.search(r'\d+\s*(ml|g|pcs)', val.lower()):
                            issues.append("Volym ska inte anges här")
                        
                        if issues:
                            cell_issues[(idx, col)] = "yellow"
                            styled_row[col] = f"⚠️ {', '.join(issues)}"
                            issue_count += 1
                        else:
                            cell_issues[(idx, col)] = "green"
                            styled_row[col] = f"✅ {val}"

                # Size validation
                elif col == "Size":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_numeric(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Storlek bör vara numerisk"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Unit/Volume validation
                elif col == "Unit/Volume":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val.lower() not in VALID_UNITS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Okänd enhet: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Units validations (all can be empty)
                elif col in ["Units (minimum)", "Units D-pack", "Units per pallet", "Units per pallet layer"]:
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_numeric(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Bör vara numeriskt värde"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # Package dimensions
                elif col in ["Length of product package", "Width of product package", "Height of product package"]:
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_numeric(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Bör vara numeriskt värde (cm)"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # Weight validation
                elif col == "Weight":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_numeric(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Bör vara numeriskt värde (gram)"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Country of origin validation - simplified to only check if empty
                elif col == "Country of origin":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Ursprungsland saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                        
                # Customs Code validation
                elif "customs code" in col.lower() or "stat.no" in col.lower():
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ {val}"
                
                # Manufacturer Information validation
                elif "manufacturer information" in col.lower():
                    invalid_values = ["na", "n/a", "not assigned", "nr"]
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val.strip().lower() in invalid_values or val.strip().upper().startswith("UN"):
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Lägg till korrekt tillverkare eller lämna fältet tomt"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # UN Number validation - updated to accept UN prefix and handle Excel formatting
                elif col == "UN Number":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val.lower() in ["n/a", "na"]:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Ta bort 'N/A' eller 'NA', lämna fältet tomt istället"
                        issue_count += 1
                    elif UN_NUMBER_PATTERN.match(val) or UN_NUMBER_PATTERN.match(val.replace(',', '')):
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                    else:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ UN-nummer bör vara 4 siffror, eller 'UN' följt av 4 siffror"
                        issue_count += 1
                
                # Flash-point validation
                elif col == "Flash-point":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_numeric(val.replace("°C", "").replace("°", "").strip()):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Bör vara numeriskt värde i Celsius"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Gross Price validation - simplified to only check if empty
                elif col == "Gross Price":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Pris saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Currency validation
                elif col == "Currency":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Valuta saknas"
                        issue_count += 1
                    elif val.lower() not in VALID_CURRENCIES:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltig valuta: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # Discount validation - simplified to only check if empty
                elif "discount" in col.lower():
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Rabatt saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # Net Purchasing Price validation - simplified to only check if empty
                elif col == "Net Purchasing Price":
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Nettopris saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # Sales Margin % validation - kept negative check, removed format validation
                elif "sales margin %" in col.lower():
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Vinstmarginal saknas"
                        issue_count += 1
                    else:
                        # Check if margin is negative
                        try:
                            margin_value = float(val.replace(",", ".").replace("%", "").strip())
                            if margin_value < 0:
                                cell_issues[(idx, col)] = "red"
                                styled_row[col] = f"❌ Negativ vinstmarginal: {val}"
                                issue_count += 1
                            else:
                                cell_issues[(idx, col)] = "green"
                                styled_row[col] = f"✅ {val}"
                        except ValueError:
                            cell_issues[(idx, col)] = "green"
                            styled_row[col] = f"✅ {val}"
                
                # Sales Margin KR validation - kept negative check, removed format validation
                elif "sales margin kr" in col.lower():
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ Vinstmarginal i kronor saknas"
                        issue_count += 1
                    else:
                        # Check if margin is negative
                        try:
                            margin_value = float(val.replace(",", ".").replace(" ", "").strip())
                            if margin_value < 0:
                                cell_issues[(idx, col)] = "red"
                                styled_row[col] = f"❌ Negativ vinstmarginal: {val}"
                                issue_count += 1
                            else:
                                cell_issues[(idx, col)] = "green"
                                styled_row[col] = f"✅ {val}"
                        except ValueError:
                            cell_issues[(idx, col)] = "green"
                            styled_row[col] = f"✅ {val}"

                # RRP SEK validation - simplified to only check if empty
                elif col.upper() in ["RRP SEK", "REC SEK"]:
                    if not val:
                        cell_issues[(idx, col)] = "red"
                        styled_row[col] = "❌ RRP SEK saknas"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # RRP NOK validation - simplified to only check if empty
                elif col.upper() in ["RRP NOK", "REC NOK"]:
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # RRP EUR validation - simplified to only check if empty
                elif col.upper() in ["RRP EUR", "REK EUR"]:
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
                # RRP DKK validation - simplified to only check if empty
                elif col.upper() in ["RRP DKK", "REK DK", "REK DKK"]:
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Giftset Value validation - simplified to only check if empty
                elif "giftset value" in col.lower():
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Product Descriptions and How To Use validations (can be empty)
                elif any(text in col.lower() for text in ["product text", "how to use", "safety information"]):
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ Text finns"

                # INCI validation
                elif col == "INCI":
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ INCI finns"

                # SEO Keywords validation
                elif "seo keywords" in col.lower():
                    cell_issues[(idx, col)] = "green"
                    styled_row[col] = "—" if not val else f"✅ Nyckelord finns"

                # Hex Color Code validation
                elif "hex color" in col.lower() or "hex code" in col.lower():
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not HEX_COLOR_PATTERN.match(val):
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = "⚠️ Ogiltigt hexformat (ska vara #RRGGBB)"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Gender validation
                elif col == "Gender":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val not in VALID_GENDER_OPTIONS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltigt kön: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # SPF validation
                elif col == "SPF":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val not in VALID_SPF_OPTIONS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltigt SPF-värde: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Color validation
                elif col == "Color":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val not in VALID_COLOR_OPTIONS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltig färg: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Finish validation
                elif col == "Finish":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val not in VALID_FINISH_OPTIONS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltig finish: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Coverage validation
                elif col == "Coverage":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val not in VALID_COVERAGE_OPTIONS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltig täckning: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Product Type validation
                elif col == "Product Type":
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif val not in VALID_PRODUCT_TYPE_OPTIONS:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltig produkttyp: {val}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Multi-select fields validation
                elif col == "Sustainable Beauty":
                    is_valid, invalid_values = validate_multi_select(val, VALID_SUSTAINABLE_BEAUTY_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Active Ingredients":
                    is_valid, invalid_values = validate_multi_select(val, VALID_ACTIVE_INGREDIENTS_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Skin Type":
                    is_valid, invalid_values = validate_multi_select(val, VALID_SKIN_TYPE_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Skin Condition":
                    is_valid, invalid_values = validate_multi_select(val, VALID_SKIN_CONDITION_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Trait":
                    is_valid, invalid_values = validate_multi_select(val, VALID_TRAIT_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Hair Type":
                    is_valid, invalid_values = validate_multi_select(val, VALID_HAIR_TYPE_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Fragrance Family":
                    is_valid, invalid_values = validate_multi_select(val, VALID_FRAGRANCE_FAMILY_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Top Notes":
                    is_valid, invalid_values = validate_multi_select(val, VALID_TOP_NOTES_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Heart Notes":
                    is_valid, invalid_values = validate_multi_select(val, VALID_HEART_NOTES_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                elif col == "Base Notes":
                    is_valid, invalid_values = validate_multi_select(val, VALID_BASE_NOTES_OPTIONS)
                    if not val:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    elif not is_valid:
                        cell_issues[(idx, col)] = "yellow"
                        styled_row[col] = f"⚠️ Ogiltiga värden: {', '.join(invalid_values)}"
                        issue_count += 1
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"

                # Default validation for all other fields (OK to leave empty)
                else:
                    if not val or val.lower() in ["nan", "none"] or pd.isna(val):
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = "—"
                    else:
                        cell_issues[(idx, col)] = "green"
                        styled_row[col] = f"✅ {val}"
                
            # Add summary information to the rows
            summary_row["Antal problem"] = issue_count
            summary_rows.append(summary_row)
            styled_summary_data.append(styled_row)
            
        # Function to style the dataframe with color-coded cells
        def style_dataframe(df):
            def highlight_cell(val, row_idx, col_name):
                color = cell_issues.get((row_idx, col_name))
                if color == "red":
                    return "background-color: #ffcccc"
                elif color == "yellow":
                    return "background-color: #fff3b0"
                elif color == "green":
                    return "background-color: #d4edda"
                return ""
    
            # Create a copy of the dataframe for display formatting
            display_df = df.copy()
        
            # Replace NaN values with a dash in the display dataframe
            display_df = display_df.fillna("—")
    
            # Define numeric columns that should have 2 decimal places
            numeric_columns = [
                "Length of product package", "Width of product package", 
                "Height of product package", "Weight", "Flash-point", 
                "Gross Price", "Discount (%)", "Net Purchasing Price", 
                "Sales Margin % SEK", "Sales Margin KR SEK", "RRP SEK", 
                "RRP NOK", "RRP EUR", "RRP DKK", "Giftset Value SEK"
            ]
            
            # Add more number-like columns to be formatted
            number_terms = ["price", "margin", "discount", "rrp", "value", "cost", 
                            "rate", "fee", "weight", "height", "width", "length"]
        
            # Format function that handles both numeric and non-numeric values
            def format_value(val, col):
                if val == "—" or val == "" or pd.isna(val):
                    return "—"
                    
                # Check if this column should be formatted as numeric
                is_numeric_col = (col in numeric_columns or 
                                 any(term in str(col).lower() for term in number_terms))
                                 
                if is_numeric_col:
                    try:
                        # Clean the value string and try to convert to float
                        cleaned_val = str(val).replace(',', '.').replace(' ', '')
                        if cleaned_val.lower() in ["nan", "none", ""]:
                            return "—"
                            
                        num_val = float(cleaned_val)
                        # Format with 2 decimal places
                        return "{:.2f}".format(num_val)
                    except (ValueError, TypeError):
                        # If it can't be converted to float, return as is
                        return val
                # For non-numeric columns, return value as is
                return val
        
            # Apply formatting to each cell in the dataframe
            for col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: format_value(x, col))
    
            # Apply highlighting to the display dataframe
            styled = display_df.style.apply(
                lambda row: [highlight_cell(row[col], row.name, col) for col in df.columns],
                axis=1
            )
    
            return styled
            
        # Display validation results tab
        with tabs[0]:  # Validation tab
            st.write("📋 Validated product file with highlighted fields")
            
            # Always show all columns, regardless of show_all_columns setting
            filtered_data = data
            
            # Create a styled dataframe with all issue highlights
            styled_df = style_dataframe(filtered_data)
            st.dataframe(styled_df, use_container_width=True, height=400)

            st.divider()
            st.write("🧾 Summary per row with status per column")

            # Create summary dataframe
            summary_df = pd.DataFrame(summary_rows)
            summary_df.rename(columns={"Radnummer": "Row Number", "Antal problem": "Error Count"}, inplace=True)
            
            # Create the detailed dataframe with columns in the original order
            detail_columns = original_column_order
            
            # Create new dict with ordered columns
            ordered_summary_data = []
            for row_data in styled_summary_data:
                ordered_row = {}
                for col in detail_columns:
                    ordered_row[col] = row_data.get(col, "")
                ordered_summary_data.append(ordered_row)
            
            detail_df = pd.DataFrame(ordered_summary_data)
            
            # Merge summary with detailed validation
            merged = pd.concat([summary_df, detail_df], axis=1)
            merged = merged.loc[:, ~merged.columns.duplicated()]
            # Round numeric columns to 2 decimal places
            for col in merged.columns:
                if merged[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                    try:
                        merged[col] = merged[col].round(2)
                    except:
                        pass
            
            # Apply filter based on sidebar selection
            if filter_by == "Only with errors":
                merged = merged[merged["Error Count"] > 0]
            elif filter_by == "Only without errors":
                merged = merged[merged["Error Count"] == 0] == "Endast med fel";
                merged = merged[merged["Antal problem"] > 0]
            elif filter_by == "Endast utan fel":
                merged = merged[merged["Antal problem"] == 0]

            # Style the summary table with appropriate colors
            def style_summary(df):
                def get_style(val):
                    if isinstance(val, str):
                        if val.startswith("✅"):
                            return "background-color: #d4edda"
                        elif val.startswith("⚠️"):
                            return "background-color: #fff3b0"
                        elif val.startswith("❌"):
                            return "background-color: #f8d7da"
                    return ""
    
                # Format numeric columns with 2 decimal places
                display_df = df.copy()
                # Replace NaN values with dash
                display_df = display_df.fillna("—")
    
                # Format numeric columns
                number_terms = ["price", "margin", "discount", "rrp", "value", "cost", 
                               "rate", "fee", "weight", "height", "width", "length"]
    
                # Format function for numeric values
                def format_numeric(val):
                    if pd.isna(val) or val == "" or val == "—":
                        return "—"
        
                    # Check if the value appears to be numeric
                    try:
                        if isinstance(val, str) and (val.startswith("✅") or val.startswith("⚠️") or val.startswith("❌")):
                            return val
                
                        # Try to convert to float and format with 2 decimal places
                        cleaned_val = str(val).replace(',', '.').replace(' ', '')
                        if cleaned_val.lower() in ["nan", "none", ""]:
                            return "—"
                
                        num_val = float(cleaned_val)
                        # Format with 2 decimal places
                        return "{:.2f}".format(num_val)
                    except (ValueError, TypeError):
                        # If it can't be converted to float, return as is
                        return val
    
                # Apply numeric formatting to columns that likely contain numbers
                for col in display_df.columns:
                    if any(term in str(col).lower() for term in number_terms):
                        display_df[col] = display_df[col].apply(format_numeric)
    
                # Apply cell styling
                return display_df.style.applymap(get_style)

            # Round numeric values to 2 decimal places
            merged = merged.round(2)
            st.dataframe(style_summary(merged), use_container_width=True, height=400)

            # Add EAN list for easy copying
            if "EAN" in data.columns:
                st.divider()
                st.subheader("📋 EAN List for Copying")
                
                # Get all EANs and display them
                eans = data["EAN"].dropna().astype(str).tolist()
                if eans:
                    # Format as one EAN per line for easy copying
                    ean_text = "\n".join(eans)
                    st.code(ean_text, language=None)

                else:
                    st.info("No valid EAN codes found in the data.")

            # Export options with more visible buttons
            st.divider()
            st.subheader("📊 Export Options")
            col1, col2 = st.columns(2)
            with col1:
                csv = merged.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Validation Report (CSV)",
                    data=csv,
                    file_name="validation_summary.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Create Excel report with formatting
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    merged.to_excel(writer, index=False, sheet_name="Validation Report")
                    # Could add Excel styling here with openpyxl if needed
                
                excel_buffer.seek(0)
                st.download_button(
                    "📥 Download as Excel Report",
                    data=excel_buffer,
                    file_name="validation_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        # Statistics tab - reorganized as requested
        with tabs[2]:  # Statistics tab
            st.subheader("Statistics and Data Analysis")
            
            # Calculate statistics
            total_rows = len(data)
            rows_with_issues = sum(1 for row in summary_rows if row["Antal problem"] > 0)
            error_percentage = (rows_with_issues / total_rows * 100) if total_rows > 0 else 0
            
            # Display stats in metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", total_rows)
            col2.metric("Rows with Issues", rows_with_issues)
            col3.metric("Error Percentage", f"{error_percentage:.1f}%")
            
            # 1. Validation Status per Column
            st.subheader("Validation Status per Column")
            
            field_validation = {}
            for (idx, col), status in cell_issues.items():
                field_validation.setdefault(col, {"green": 0, "yellow": 0, "red": 0})
                field_validation[col][status] += 1
                
            # Convert to percentage
            field_validation_pct = {}
            for col, counts in field_validation.items():
                total = sum(counts.values())
                if total > 0:
                    field_validation_pct[col] = {
                        "Correct (%)": (counts["green"] / total * 100),
                        "Warnings (%)": (counts["yellow"] / total * 100),
                        "Errors (%)": (counts["red"] / total * 100)
                    }
                    
            # Create a dataframe for visualization
            validation_data = []
            for col, stats in field_validation_pct.items():
                validation_data.append({
                    "Column": col,
                    "Status": "Correct",
                    "Percent": stats["Correct (%)"]
                })
                validation_data.append({
                    "Column": col,
                    "Status": "Warnings",
                    "Percent": stats["Warnings (%)"]
                })
                validation_data.append({
                    "Column": col,
                    "Status": "Errors",
                    "Percent": stats["Errors (%)"]
                })
                
            validation_df = pd.DataFrame(validation_data)
            
            # Convert to a pivot table for visualization
            pivot_df = validation_df.pivot(index="Column", columns="Status", values="Percent")
            
            # Ensure all columns exist
            for col in ["Correct", "Warnings", "Errors"]:
                if col not in pivot_df.columns:
                    pivot_df[col] = 0
                    
            # Sort by error percentage
            pivot_df = pivot_df.sort_values("Errors", ascending=False)
            
            # Display stacked bar chart
            if not pivot_df.empty:
                st.bar_chart(pivot_df)
                
            # 2. Field Completion Rate
            st.subheader("Field Completion Rate")
            
            field_stats = {}
            for col in data.columns:
                non_empty = sum(1 for val in data[col] if pd.notna(val) and str(val).strip() not in ["", "nan", "none"])
                completion_pct = (non_empty / total_rows * 100) if total_rows > 0 else 0
                field_stats[col] = completion_pct
                
            field_stats_df = pd.DataFrame({
                "Column": list(field_stats.keys()),
                "Completion Rate (%)": list(field_stats.values())
            }).sort_values("Completion Rate (%)", ascending=False)
            
            st.bar_chart(field_stats_df.set_index("Column"))
            
            # 3. Detailed Issue List
            st.subheader("Detailed Issue List")
            issue_types = {}
            for row in styled_summary_data:
                for col, val in row.items():
                    if val.startswith("❌") or val.startswith("⚠️"):
                        issue_key = val.split("❌ ")[-1] if "❌ " in val else val.split("⚠️ ")[-1]
                        issue_key = issue_key[:40] + "..." if len(issue_key) > 40 else issue_key
                        issue_types.setdefault(issue_key, 0)
                        issue_types[issue_key] += 1
            
            issue_df = pd.DataFrame({
                "Issue": list(issue_types.keys()),
                "Count": list(issue_types.values())
            }).sort_values("Count", ascending=False)
            
            if not issue_df.empty:
                st.dataframe(issue_df, use_container_width=True)
            else:
                st.success("No issues found in the file!")
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
        if st.checkbox("Show detailed error information"):
            st.exception(e)
else:
    st.info("Upload an Excel file to start validation.")
    
    # Show welcome message and instructions
    st.markdown("""
    ## Welcome to NordicFeel Product Validation
    
    This tool helps you validate product files for upload to NordicFeel. 
    It checks that your Excel file has the correct format and that all necessary information is included.
    
    ### How to use the tool:
    
    1. Upload your Excel file with product data by clicking "Browse files" above
    2. The system automatically analyzes your file and shows any errors or warnings
    3. Fix the errors in your Excel file based on the feedback
    4. You can download an error report to share with others
    5. A list of all EAN codes is shown at the end for easy copying
    
    ### Color coding:
    
    - 🟢 **Green** - The information is correct
    - 🟡 **Yellow** - Warning that must be corrected
    - 🔴 **Red** - Error that must be fixed
    """)
    
    # Display file structure requirements
    with st.expander("📋 View Column Explanations", expanded=False):
        st.markdown("""

         ### First, let’s start with the basics
        Providing proper product data is one of the easiest and most effective ways to improve the performance of your products. When your data is accurate and complete, products are processed faster, become easier to find on the site, and are prioritized in search, filters, and recommendation algorithms.

        ✅ Always use the latest version of our product template – NordicFeel Product Template v.2025-04-30

        We strongly encourage you to submit complete and correct product data from the start, as this significantly reduces the risk of errors and ensures your product gets the best possible placement on site. 
        Incomplete submissions often delay launch and increase the risk of incorrect product listings. 
        
        **We cannot guarantee that the product data will be corrected at a later stage if required fields are missing in the initial submission.**
        
        ### Critical Columns (must be filled in with correct information from the start)

        **Required to register and order the product. We cannot process any files with missing information in critical fields.**
        
        - Categories
        - EAN
        - Brand Name
        - Product Name
        - Country of origin
        - Gross Price
        - Currency
        - Discount (%)
        - Net Purchasing Price
        - Sales Margin %
        - Sales Margin KR
        - RRP SEK
        
        ### Critical Columns, if applicable

        **If these columns are relevant for your products, it's critical that they are filled in correctly from the start..**
        
        - If Relaunch, Enter Old EAN
        - Launch Date
        - Purchasing Date
        - UN Number
        - Flash-point
        
        ### Required Columns 
        
        **These are required for full product setup and before the product launch on site.**
        
        - Limited Edition
        - Size & Unit/Volume
        - Logistics & Packaging
        - Customs Code / STAT.no – 10 digits
        - Manufacturer Information – Name, Postal Address, Email
        - Product Attributes – If relevant for the category
        - Fragrance Profile – If relevant (e.g., perfumes, scented products)
        """)

        st.info("For more details, see the documentation from NordicFeel about product uploads.")
