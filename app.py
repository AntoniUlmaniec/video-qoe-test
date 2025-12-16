import streamlit as st
import random
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit.components.v1 as components
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Badanie Jakosci Wideo", layout="centered")

# --- KONFIGURACJA GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hDmQqQdy7jitS5B8Ah_k6mV31HA9QGRYpm63ISODrbg/edit?hl=pl&gid=310694828#gid=310694828"

def get_google_sheet_client():
    """Pomocnicza funkcja do autoryzacji."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    return client

def save_new_user(age, gender, vision, environment):
    """Tworzy nowego użytkownika, generuje ID i zapisuje w zakładce 'Uczestnicy'."""
    try:
        client = get_google_sheet_client()
        sheet = client.open_by_url(SHEET_URL).worksheet("Uczestnicy")
        
        new_user_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sheet.append_row([new_user_id, timestamp, age, gender, vision, environment])
        return new_user_id
    except Exception as e:
        st.error(f"Błąd zapisu użytkownika: {e}")
        return None

def save_rating(user_id, video_code, rating):
    """Zapisuje ocenę wideo w zakładce 'Wyniki'."""
    try:
        client = get_google_sheet_client()
        sheet = client.open_by_url(SHEET_URL).worksheet("Wyniki")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sheet.append_row([user_id, timestamp, video_code, rating])
        return True
    except Exception as e:
        st.error(f"Błąd zapisu oceny: {e}")
        return False

# --- PEŁNA LISTA WIDEO ---
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

# --- ZARZĄDZANIE STANEM APLIKACJI ---
# 1. Czy użytkownik przeczytał wstęp?
if 'intro_accepted' not in st.session_state:
    st.session_state.intro_accepted = False

# 2. Czy użytkownik ma ID (czy wypełnił ankietę demograficzną)?
if 'user_id' not in st.session_state:
    st.session_state.user_id = None


# --- LOGIKA WYŚWIETLANIA ---

if not st.session_state.intro_accepted:
    # === ETAP 1: EKRAN POWITALNY / INSTRUKCJA ===
    st.title("Witamy w badaniu jakości wideo")
    st.subheader("Dziękujemy za udział w teście.")
    
    st.markdown("""
    Podczas eksperymentu na Twoim urządzeniu wyświetlane będą krótkie sekwencje wideo.
    Po obejrzeniu każdej sekwencji zostaniesz poproszony o ocenę jakości materiału.
    
    Prosimy, abyś skupił się na **jakości wideo**, a nie na treści czy ewentualnych reklamach.
    """)
    
    st.info("""
    **Wytyczne do testu:**
    * Oglądaj każdą sekwencję uważnie od początku do końca.
    * Postaraj się wykonać test w cichym otoczeniu.
    * Oceniaj każdą sekwencję wyłącznie na podstawie własnego odczucia.
    """)
    
    st.markdown("""
    Po każdej sekwencji zadamy Ci pytanie:  
    ***"Jaka jest Twoja opinia o jakości wideo?"***
    
    Prosimy o intuicyjne odpowiedzi – nie ma złych ani dobrych ocen. Interesuje nas Twoja subiektywna opinia. 
    Żadna wiedza techniczna ani wcześniejsze doświadczenie nie są wymagane.
    
    Dziękujemy za Twój czas i zaangażowanie.
    """)
    
    st.write("") # Odstęp
    if st.button("ROZPOCZNIJ", type="primary"):
        st.session_state.intro_accepted = True
        st.rerun()

elif st.session_state.user_id is None:
    # === ETAP 2: ANKIETA DEMOGRAFICZNA ===
    st.title("Metryczka uczestnika")
    st.markdown("""
    Zanim przejdziemy do wideo, prosimy o kilka podstawowych informacji statystycznych.
    Są one w pełni **anonimowe** i służą wyłącznie do celów naukowych.
    """)
    st.markdown("---")
    
    with st.form("demographics_form"):
        wiek = st.radio("Twój przedział wiekowy:", 
                        ["18-24", "25-34", "35-44", "45-54", "55+"])
        
        plec = st.radio("Płeć:", ["Kobieta", "Mężczyzna", "Nie chcę podawać"])
        
        wzrok = st.radio("Czy posiadasz wadę wzroku?", 
                         ["Nie, mam dobry wzrok", "Tak, ale noszę okulary/soczewki", "Tak, nie korygowana"])
        
        srodowisko = st.radio("W jakich warunkach przeprowadzasz test?",
                              ["W domu (spokój)", "W biurze/szkole", "W podróży/na zewnątrz"])
        
        submitted = st.form_submit_button("PRZEJDŹ DO TESTU WIDEO", type="primary")
        
        if submitted:
            with st.spinner("Generowanie profilu..."):
                uid = save_new_user(wiek, plec, wzrok, srodowisko)
                if uid:
                    st.session_state.user_id = uid
                    # Inicjujemy losowanie pierwszego filmu
                    st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))
                    st.session_state.rated = False
                    st.rerun()

else:
    # === ETAP 3: WŁAŚCIWY TEST WIDEO ===
    
    # Inicjalizacja zmiennych jeśli zniknęły
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
        st.session_state.rated = False

    st.title("Badanie Jakości Wideo (QoE)")
    # Dyskretne ID
    st.caption(f"ID Uczestnika: {st.session_state.user_id}")
    
    st.info("Twoim zadaniem jest obejrzeć wyświetlony klip i ocenić jego jakość.")

    code = st.session_state.current_code
    filename = VIDEO_MAP.get(code, "out_bigBuckBunny_1920x1080_3000k.mp4")
    video_url = BASE_URL + filename

    st.subheader(f"Sekwencja testowa: {code}")

    # --- PLAYER WIDEO (Fake Fullscreen) ---
    video_html = f"""
    <style>
        #start-btn {{
            background-color: #FF4B4B; color: white; padding: 15px 32px;
            text-align: center; display: inline-block; font-size: 16px;
            margin: 4px 2px; cursor: pointer; border: none; border-radius: 4px;
            width: 100%; font-weight: bold;
        }}
        #start-btn:hover {{ background-color: #FF2B2B; }}
        video::-webkit-media-controls-timeline {{ display: none !important; }}
        #my-video {{ display: none; width: 100%; }}
    </style>

    <div id="video-container">
        <button id="start-btn" onclick="startVideo()">▶ ODTWÓRZ WIDEO (FULLSCREEN)</button>
        <video id="my-video" controlsList="nodownload noplaybackrate">
            <source src="{video_url}" type="video/mp4">
        </video>
    </div>

    <script>
        function startVideo() {{
            var video = document.getElementById("my-video");
            var btn = document.getElementById("start-btn");
            video.style.display = "block";
            btn.style.display = "none";
            video.play();
            if (video.requestFullscreen) {{ video.requestFullscreen(); }}
            else if (video.webkitRequestFullscreen) {{ video.webkitRequestFullscreen(); }}
        }}
        document.getElementById("my-video").addEventListener('ended', function(e) {{
            if (document.exitFullscreen) {{ document.exitFullscreen(); }}
            else if (document.webkitExitFullscreen) {{ document.webkitExitFullscreen(); }}
        }});
    </script>
    """
    components.html(video_html, height=400)
    st.markdown("---")

    # --- OCENA ---
    st.header("Twoja ocena")

    if not st.session_state.rated:
        with st.form("rating_form"):
            st.write("**Jaka jest Twoja opinia o jakości wideo?**")
            ocena = st.slider("(1 - Fatalna, 5 - Doskonała)", 1, 5, 3)
            
            submitted = st.form_submit_button("ZATWIERDŹ OCENĘ", type="primary")
            
            if submitted:
                with st.spinner("Zapisuję..."):
                    sukces = save_rating(st.session_state.user_id, code, ocena)
                    if sukces:
                        st.success("Zapisano!")
                        st.session_state.rated = True
                        time.sleep(1)
                        losuj_nowe()
                        st.rerun()
    else:
        st.info("Wideo ocenione. Ładowanie kolejnego...")

    st.markdown("---")
    if st.button("Pomiń to wideo (losuj inne)"):
        losuj_nowe()
        st.rerun()
