import streamlit as st
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit.components.v1 as components

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Badanie Jakosci Wideo", layout="centered")

# --- KONFIGURACJA GOOGLE SHEETS ---
# Upewnij się, że masz plik secrets.toml lub sekrety w chmurze skonfigurowane!
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hDmQqQdy7jitS5B8Ah_k6mV31HA9QGRYpm63ISODrbg/edit?hl=pl&gid=0#gid=0" 

def save_to_google_sheets(video_code, rating):
    try:
        # Pobieramy dane logowania z sekretów Streamlit
        # Zakładamy, że w secrets.toml sekcja nazywa się [gcp_service_account]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        client = gspread.authorize(creds)
        
        # Otwieramy arkusz
        sheet = client.open(SHEET_URL).sheet1  # sheet1 to pierwsza zakładka
        
        # Pobieramy aktualną datę
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapisujemy wiersz: [Data, Kod Wideo, Ocena]
        sheet.append_row([timestamp, video_code, rating])
        return True
    except Exception as e:
        st.error(f"Błąd zapisu do bazy: {e}")
        return False

# --- DANE WIDEO ---
BASE_URL = "https://github.com/AntoniUlmaniec/video-qoe-test/releases/download/v1.0/"

VIDEO_MAP = {
    "SEQ_01": "out_bigBuckBunny_1920x1080_3000k.mp4",
    "SEQ_02": "out_bigBuckBunny_1920x1080_3000k_withAD.mp4",
    "SEQ_03": "out_bigBuckBunny_256x144_100k.mp4",
    "SEQ_04": "out_bigBuckBunny_256x144_100k_withAD.mp4",
    "SEQ_05": "out_bigBuckBunny_480x270_250k.mp4",
    "SEQ_06": "out_bigBuckBunny_480x270_250k_withAD.mp4",
    "SEQ_07": "out_caminandes_1920x1080_3000k.mp4",
    "SEQ_08": "out_caminandes_1920x1080_3000k_withAD.mp4",
    "SEQ_09": "out_caminandes_256x144_75k.mp4",
    "SEQ_10": "out_caminandes_256x144_75k_withAD.mp4",
    "SEQ_11": "out_caminandes_480x270_250k.mp4",
    "SEQ_12": "out_caminandes_480x270_250k_withAD.mp4",
    "SEQ_13": "out_elephantsDream_1920x1080_3000k.mp4",
    "SEQ_14": "out_elephantsDream_1920x1080_3000k_withAD.mp4",
    "SEQ_15": "out_elephantsDream_256x144_100k.mp4",
    "SEQ_16": "out_elephantsDream_256x144_100k_withAD.mp4",
    "SEQ_17": "out_elephantsDream_480x270_400k.mp4",
    "SEQ_18": "out_elephantsDream_480x270_400k_withAD.mp4",
    "SEQ_19": "out_sintelDragons_1920x1080_3000k.mp4",
    "SEQ_20": "out_sintelDragons_1920x1080_3000k_withAD.mp4",
    "SEQ_21": "out_sintelDragons_256x144_75k.mp4",
    "SEQ_22": "out_sintelDragons_256x144_75k_withAD.mp4",
    "SEQ_23": "out_sintelDragons_480x270_250k.mp4",
    "SEQ_24": "out_sintelDragons_480x270_250k_withAD.mp4"
}

# --- LOGIKA STANU ---
if 'current_code' not in st.session_state:
    st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))

# Dodatkowa flaga, czy oceniono już bieżący film
if 'rated' not in st.session_state:
    st.session_state.rated = False

def losuj_nowe():
    lista_kodow = list(VIDEO_MAP.keys())
    nowy_kod = random.choice(lista_kodow)
    while len(lista_kodow) > 1 and nowy_kod == st.session_state.current_code:
        nowy_kod = random.choice(lista_kodow)
    st.session_state.current_code = nowy_kod
    st.session_state.rated = False # Resetujemy flagę oceny

# --- INTERFEJS ---
st.title("Badanie Jakosci Wideo (QoE)")
st.info("Twoim zadaniem jest obejrzec klip i ocenic go BEZ wychodzenia ze strony.")

code = st.session_state.current_code
filename = VIDEO_MAP[code]
video_url = BASE_URL + filename

st.subheader(f"Sekwencja testowa: {code}")

# --- PLAYER WIDEO (Ten sam co wcześniej) ---
video_html = f"""
<style>
    #start-btn {{
        background-color: #FF4B4B; color: white; padding: 15px 32px;
        text-align: center; display: inline-block; font-size: 16px;
        margin: 4px 2px; cursor: pointer; border: none; border-radius: 4px;
        width: 100%; font-weight: bold;
    }}
    #start-btn:hover {{ background-color: #FF2B2B; }}
    #video-overlay {{
        display: none; position: fixed; top: 0; left: 0;
        width: 100vw; height: 100vh; background-color: black;
        z-index: 999999; text-align: center;
    }}
    #my-video {{ width: 100%; height: 100%; object-fit: contain; outline: none; }}
    video::-webkit-media-controls-timeline {{ display: none !important; }}
</style>

<div id="controls-container">
    <button id="start-btn" onclick="startVideo()">▶ ODTWÓRZ WIDEO</button>
</div>

<div id="video-overlay">
    <video id="my-video" controlsList="nodownload noplaybackrate">
        <source src="{video_url}" type="video/mp4">
    </video>
</div>

<script>
    var video = document.getElementById("my-video");
    var overlay = document.getElementById("video-overlay");
    function startVideo() {{ overlay.style.display = "block"; video.play(); }}
    video.addEventListener('ended', function(e) {{ overlay.style.display = "none"; }});
    document.addEventListener('keydown', function(e) {{
        if (e.key === "Escape" || e.keyCode === 27) {{ e.preventDefault(); return false; }}
    }});
</script>
"""
components.html(video_html, height=100)

st.markdown("---")

# --- NOWY FORMULARZ OCENY ---
st.header("Twoja ocena")

if not st.session_state.rated:
    # Formularz
    with st.form("qoe_form"):
        st.write("Jak oceniasz jakość obejrzanego wideo?")
        
        # Suwak 1-5 (możesz zmienić na st.feedback("stars") w nowszym Streamlit)
        ocena = st.slider("Jakość (1 - Bardzo zła, 5 - Doskonała)", 1, 5, 3)
        
        # Przycisk wysyłania (wewnątrz formularza)
        submitted = st.form_submit_button("ZAPISZ OCENĘ", type="primary")
        
        if submitted:
            with st.spinner("Zapisuję wynik..."):
                sukces = save_to_google_sheets(code, ocena)
                if sukces:
                    st.session_state.rated = True
                    st.success("Ocena zapisana! Ładuję kolejne wideo...")
                    import time
                    time.sleep(1.5) # Krótka pauza żeby użytkownik zobaczył sukces
                    losuj_nowe()
                    st.rerun()
else:
    st.success("Wideo ocenione. Ładowanie nowego...")

st.markdown("---")
