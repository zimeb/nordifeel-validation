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

# For example:
# RAW_TOP_NOTES = """Absint
# Agave
# ... (rest of notes)
# """
# VALID_TOP_NOTES_OPTIONS = parse_notes(RAW_TOP_NOTES)

VALID_CURRENCIES = ["SEK", "NOK", "EUR", "DKK", "DK", "sek", "nok", "eur", "dkk", "dk"]
VALID_UNITS = ["ml", "g", "pcs", "st", "set", "kit", "pack"]

# Regular expression patterns for validation
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$')
NUMERIC_PATTERN = re.compile(r'^\d+$')
HEX_COLOR_PATTERN = re.compile(r'^#[0-9a-fA-F]{6}$')
UN_NUMBER_PATTERN = re.compile(r'^(UN)?[0-9,.\s]{1,6}$', re.IGNORECASE)

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
        st.markdown("""
        ### Critical Columns (must be filled in)
        
        - **Main Category** - Helps customers find your product and increases visibility in filters and recommendations.
        - **Secondary Category** - Same as above. Be as specific as possible, but only select what is truly relevant.
        - **EAN** - 8 or 13 digits. Required to list and track the product in our systems.
        - **Brand Name** - Displayed across site. Must be correct and final from the start.
        - **Product Name** - This is the name customers will see on-site and in search results. It must be final and correctly formatted, as we publish exactly what you enter here — no internal corrections or adjustments are made. A clear, accurate name is essential for product presentation, customer trust, and overall sales performance.
        - **Gross Price** - Base for pricing calculations and margin setup.
        - **Currency** - Must match the pricing data you provide.
        - **Discount (%)** - Used to calculate your net purchasing price.
        - **Net Purchasing Price** - Calculated field (Gross Price - Discount).
        - **Sales Margin %** - Calculated from price data.
        - **Sales Margin KR** - Calculated from price data.
        - **Country of origin** - Required for customs and legal compliance.
        - **RRP SEK** - Customer-facing sales price. Displayed on site.
        
        ### Critical Columns (if applicable)
        
        - **If Relaunch, Enter Old EAN** - If this product is a renovation or replacement of an existing item, it's essential that you provide the previous EAN. This allows us to link the new product to the same article number and retain valuable data like historical sales, reviews, customer behavior, and order forecasts. Without this, the product is treated as completely new — which means our systems (and customers) have to "relearn" it from scratch, resulting in slower ramp-up and lost sales opportunities.
        - **Launch Date** - Use if you want to control the product's go-live date. If left blank, the product will be launched immediately once in stock.
        - **Purchasing Date** - If you want to control when we can start purchase the product. If left blank, we will purchase it immediately once registered.
        - **UN Number** - Mandatory for hazardous goods. Supplier must provide this if relevant.
        - **Flash-point** - Mandatory for hazardous goods. Supplier must provide this if relevant.
        
        ### Important Columns (but not critical)
        
        - **Third Category** - Improves product visibility and navigation on-site. Fill in to the extent possible as relevant.
        - **Size** - Displayed in filters and on product pages (e.g. 30, 50, 100).
        - **Unit/Volume** - Clarifies product size. Used with the number in "Size".
        - **Length/Width/Height of product package** - Used for shipping and storage setup.
        - **Weight** - Used for shipping and storage setup.
        - **Customs Code / STAT.no** - Used for customs classification. We can add if missing.
        - **Manufacturer Information** - Important (will become critical under EU law). Must be the GPSR-responsible company. Required for upcoming EU regulations.
        - **Giftset Value SEK** - Important if applicable. Required for gift sets or value packs to reflect bundle value.
        - **Product Text (all languages)** - Important but not critical at this stage. A good, descriptive product text increases customer trust and drives sales. Can be left empty at this stage if you will send it later or we can retrieve it from a supplier portal.
        - **How To Use (all languages)** - Important but not critical at this stage. Helps customers use the product correctly, reduces returns, and builds brand trust. Can be left empty at this stage if you will send it later or we can retrieve it from a supplier portal.
        - **Safety Information Use (all languages)** - Important (will become critical). Required for GPSR compliance.
        - **INCI** - Critical for transparency and compliance. Can be left empty at this stage if you will send it later or we can retrieve it from a supplier portal.
        
        ### Optional Columns
        
        - **Fourth Category** - Adds filtering depth if relevant. Only fill in if it makes sense for the product.
        - **Vendor Item Number** - Helps match SKUs across systems.
        - **Product Name 2** - Useful for distinguishing between similar products, especially variants like shades, scents, or formats. Helps customers easily identify the right version and improves clarity on product pages. Do not include brand name or volume. Avoid abbreviations, and capitalize each word for consistency and readability.
        - **Units (minimum/D-pack/per pallet/per pallet layer)** - Supports logistics and order planning.
        - **RRP NOK/EUR/DKK** - We'll convert from SEK if left blank.
        - **SEO Keywords** - Improves product discoverability in search and SEO.
        - **Hex Color Code** - Helps visually match color cosmetics or packaging. Improves product filtering and visibility.
        
        ### Attribute Columns (recommended if relevant)
        
        These columns improve product discoverability, filtering, and recommendation precision:
        
        - **Gender** - Used in filters and helps us recommend the product more effectively to the right audience.
        - **SPF** - Important for skincare and sun protection categories. Improves filtering and recommendation precision.
        - **Color** - Displayed on product pages and filters. Helps customers compare and find matching shades.
        - **Finish** - Relevant for makeup. Improves discoverability through filters and recommendations.
        - **Coverage** - Used for foundations, concealers, and BB creams. Helps the right customers find the right level of coverage.
        - **Product Type** - Supports site navigation, filters, and search. Improves product matching and cross-selling.
        - **Sustainable Beauty** - Used in filters and badges to promote eco-conscious choices. Boosts visibility for customers who shop by values.
        - **Active Ingredients** - Key for product discovery and trust. Helps us highlight benefits and connect to search terms like "Vitamin C" or "Retinol."
        - **Skin Type** - Used in filters and recommendations. Helps customers find suitable products based on their skin needs.
        - **Skin Condition** - Improves targeting for specific concerns (e.g., acne, dryness). Helps customers find the right solutions.
        - **Trait** - Describes additional benefits (e.g., hydrating, volumizing). Supports filters and recommendation accuracy.
        - **Hair Type** - Used in recommendations and filters to guide the right product to the right user.
        - **Fragrance Family** - Improves discoverability in scent categories. Helps group similar products and refine recommendations.
        - **Top/Heart/Base Notes** - Enhances discovery and storytelling for perfumes. Useful in detailed product pages and guided shopping."""
