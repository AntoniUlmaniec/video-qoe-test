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
# Wklej swój link do arkusza
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
        # Otwieramy zakładkę o nazwie "Uczestnicy"
        sheet = client.open_by_url(SHEET_URL).worksheet("Uczestnicy")
        
        # Generujemy unikalne ID (krótkie, 8 znaków dla czytelności)
        new_user_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapisujemy: ID, Data, Wiek, Płeć, Wzrok, Środowisko
        sheet.append_row([new_user_id, timestamp, age, gender, vision, environment])
        return new_user_id
    except Exception as e:
        st.error(f"Błąd zapisu użytkownika: {e}")
        return None

def save_rating(user_id, video_code, rating):
    """Zapisuje ocenę wideo w zakładce 'Wyniki'."""
    try:
        client = get_google_sheet_client()
        # Otwieramy zakładkę o nazwie "Wyniki"
        sheet = client.open_by_url(SHEET_URL).worksheet("Wyniki")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapis: User_ID, Data, Kod Wideo, Ocena
        sheet.append_row([user_id, timestamp, video_code, rating])
        return True
    except Exception as e:
        st.error(f"Błąd zapisu oceny: {e}")
        return False

# --- DANE WIDEO ---
BASE_URL = "https://github.com/AntoniUlmaniec/video-qoe-test/releases/download/v1.0/"
VIDEO_MAP = {
    "SEQ_01": "out_bigBuckBunny_1920x1080_3000k.mp4",
    "SEQ_02": "out_bigBuckBunny_1920x1080_3000k_withAD.mp4",
    "SEQ_03": "out_bigBuckBunny_256x144_100k.mp4",
    "SEQ_04": "out_bigBuckBunny_256x144_100k_withAD.mp4",
    # ... (możesz tu wkleić resztę swoich filmów, skróciłem dla czytelności) ...
    "SEQ_24": "out_sintelDragons_480x270_250k_withAD.mp4"
}

# --- LOGIKA APLIKACJI ---

# 1. Sprawdzamy, czy użytkownik jest już "zalogowany" (ma ID)
if 'user_id' not in st.session_state:
    # --- EKRAN POWITALNY / ANKIETA DEMOGRAFICZNA ---
    st.title("Witaj w badaniu QoE")
    st.markdown("""
    Cześć! Dziękuję za udział w eksperymencie.
    Zanim przejdziemy do oglądania wideo, proszę o kilka podstawowych informacji statystycznych.
    Są one w pełni **anonimowe**.
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
        
        submitted = st.form_submit_button("ROZPOCZNIJ TEST", type="primary")
        
        if submitted:
            with st.spinner("Generowanie profilu..."):
                # Zapisujemy usera i dostajemy jego ID
                uid = save_new_user(wiek, plec, wzrok, srodowisko)
                
                if uid:
                    st.session_state.user_id = uid
                    # Inicjujemy też losowanie pierwszego filmu
                    st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))
                    st.session_state.rated = False
                    st.rerun()

else:
    # --- EKRAN WŁAŚCIWY (TEST WIDEO) ---
    # Ten kod wykonuje się TYLKO, gdy mamy już user_id
    
    def losuj_nowe():
        lista_kodow = list(VIDEO_MAP.keys())
        nowy_kod = random.choice(lista_kodow)
        while len(lista_kodow) > 1 and nowy_kod == st.session_state.current_code:
            nowy_kod = random.choice(lista_kodow)
        st.session_state.current_code = nowy_kod
        st.session_state.rated = False

    st.title("Badanie Jakosci Wideo (QoE)")
    # Wyświetlamy ID dyskretnie na dole lub w sidebarze
    st.sidebar.text(f"Twój ID uczestnika: {st.session_state.user_id}")
    
    st.info("Twoim zadaniem jest obejrzec wyswietlony klip i ocenic jego jakosc.")

    code = st.session_state.current_code
    filename = VIDEO_MAP.get(code, "out_bigBuckBunny_1920x1080_3000k.mp4") # Fallback
    video_url = BASE_URL + filename

    st.subheader(f"Sekwencja testowa: {code}")

    # --- PLAYER WIDEO ---
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
            st.write("Po obejrzeniu filmu, zaznacz ocenę:")
            ocena = st.slider("Jakość (1 - Fatalna, 5 - Doskonała)", 1, 5, 3)
            
            submitted = st.form_submit_button("ZATWIERDŹ OCENĘ", type="primary")
            
            if submitted:
                # TU JEST ZMIANA: Przekazujemy user_id do funkcji zapisu
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
    if st.button("Pomiń to wideo"):
        losuj_nowe()
        st.rerun()
