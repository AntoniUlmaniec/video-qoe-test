import streamlit as st
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit.components.v1 as components
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Badanie Jakosci Wideo", layout="centered")

# --- KONFIGURACJA GOOGLE SHEETS ---
# Wklej tutaj PEŁNY LINK do swojego Arkusza Google
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hDmQqQdy7jitS5B8Ah_k6mV31HA9QGRYpm63ISODrbg/edit?hl=pl&gid=0#gid=0" 

def save_to_google_sheets(video_code, rating):
    """Funkcja łącząca się z Google Sheets i zapisująca wynik."""
    try:
        # Pobieranie danych logowania z sekretów
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        client = gspread.authorize(creds)
        
        # Otwieranie arkusza po URL (najbezpieczniejsza metoda)
        sheet = client.open_by_url(SHEET_URL).sheet1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapis: [Data, Kod Wideo, Ocena]
        sheet.append_row([timestamp, video_code, rating])
        return True
    except Exception as e:
        st.error(f"Wystąpił błąd podczas zapisu: {e}")
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

# --- LOGIKA STANU (SESSION STATE) ---
if 'current_code' not in st.session_state:
    st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))

if 'rated' not in st.session_state:
    st.session_state.rated = False

def losuj_nowe():
    lista_kodow = list(VIDEO_MAP.keys())
    nowy_kod = random.choice(lista_kodow)
    while len(lista_kodow) > 1 and nowy_kod == st.session_state.current_code:
        nowy_kod = random.choice(lista_kodow)
    st.session_state.current_code = nowy_kod
    st.session_state.rated = False # Resetujemy flagę, aby pokazać formularz dla nowego filmu

# --- UI STRONY ---
st.title("Badanie Jakosci Wideo (QoE)")
st.info("Twoim zadaniem jest obejrzec wyswietlony klip i ocenic jego jakosc.")

code = st.session_state.current_code
filename = VIDEO_MAP[code]
video_url = BASE_URL + filename

st.subheader(f"Sekwencja testowa: {code}")

# --- SEKCJA HTML/JS DLA WIDEO (TWOJA ORYGINALNA WERSJA) ---
video_html = f"""
<style>
    /* Stylizacja przycisku startowego */
    #start-btn {{
        background-color: #FF4B4B;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border: none;
        border-radius: 4px;
        width: 100%;
        font-weight: bold;
    }}
    #start-btn:hover {{
        background-color: #FF2B2B;
    }}
    /* Ukrycie paska przewijania w wideo */
    video::-webkit-media-controls-timeline {{
        display: none !important;
    }}
    /* Ukrycie wideo na początku */
    #my-video {{
        display: none;
        width: 100%;
    }}
</style>

<div id="video-container">
    <button id="start-btn" onclick="startVideo()">▶ ODTWÓRZ WIDEO (FULLSCREEN)</button>
    
    <video id="my-video" controlsList="nodownload noplaybackrate">
        <source src="{video_url}" type="video/mp4">
        Twoja przeglądarka nie obsługuje wideo.
    </video>
</div>

<script>
    function startVideo() {{
        var video = document.getElementById("my-video");
        var btn = document.getElementById("start-btn");
        
        // 1. Pokaż wideo, ukryj przycisk
        video.style.display = "block";
        btn.style.display = "none";
        
        // 2. Zacznij odtwarzać
        video.play();
        
        // 3. Wymuś pełny ekran (musi być wywołane przez kliknięcie!)
        if (video.requestFullscreen) {{
            video.requestFullscreen();
        }} else if (video.webkitRequestFullscreen) {{ /* Safari */
            video.webkitRequestFullscreen();
        }} else if (video.msRequestFullscreen) {{ /* IE11 */
            video.msRequestFullscreen();
        }}
    }}
    
    // Opcjonalnie: Wyłącz pełny ekran gdy film się skończy
    document.getElementById("my-video").addEventListener('ended', function(e) {{
        if (document.exitFullscreen) {{
            document.exitFullscreen();
        }} else if (document.webkitExitFullscreen) {{
            document.webkitExitFullscreen();
        }}
    }});
</script>
"""

# Renderowanie HTML
st.components.v1.html(video_html, height=400)
st.markdown("---")

# --- SEKCJA OCENY (ZINTEGROWANA Z GOOGLE SHEETS) ---
st.header("Twoja ocena")

if not st.session_state.rated:
    with st.form("rating_form"):
        st.write("Po obejrzeniu filmu, zaznacz ocenę na suwaku poniżej:")
        
        # Suwak od 1 do 5
        ocena = st.slider("Jakość wideo (1 - Fatalna, 5 - Doskonała)", 1, 5, 3)
        
        submitted = st.form_submit_button("ZATWIERDŹ OCENĘ", type="primary")
        
        if submitted:
            with st.spinner("Zapisuję wynik w bazie..."):
                sukces = save_to_google_sheets(code, ocena)
                if sukces:
                    st.success("Zapisano pomyślnie!")
                    st.session_state.rated = True
                    time.sleep(1) # Krótka pauza dla efektu
                    losuj_nowe()
                    st.rerun()
else:
    st.info("Wideo ocenione. Ładowanie kolejnego...")

st.markdown("---")
# Opcjonalny przycisk awaryjny do pominięcia
if st.button("Pomiń to wideo (losuj inne)"):
    losuj_nowe()
    st.rerun()
