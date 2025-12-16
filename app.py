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
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    return client

def save_new_user(age, gender, experience, vision, environment, device):
    try:
        client = get_google_sheet_client()
        sheet = client.open_by_url(SHEET_URL).worksheet("Uczestnicy")
        
        new_user_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapisujemy: ID, Data, Wiek, Płeć, Doświadczenie, Wzrok, Otoczenie, Urządzenie
        sheet.append_row([new_user_id, timestamp, age, gender, experience, vision, environment, device])
        return new_user_id
    except Exception as e:
        st.error(f"Błąd zapisu użytkownika: {e}")
        return None

def save_rating(user_id, video_filename, rating):
    try:
        client = get_google_sheet_client()
        sheet = client.open_by_url(SHEET_URL).worksheet("Wyniki")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapis: User_ID, Data, NAZWA PLIKU, Ocena
        sheet.append_row([user_id, timestamp, video_filename, rating])
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
if 'intro_accepted' not in st.session_state:
    st.session_state.intro_accepted = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# NOWE ZMIENNE DO ŚLEDZENIA POSTĘPU
if 'watched_videos' not in st.session_state:
    st.session_state.watched_videos = []
if 'finished' not in st.session_state:
    st.session_state.finished = False

# --- LOGIKA LOSOWANIA Z WYKLUCZENIEM OBEJRZANYCH ---
def losuj_nowe():
    wszystkie = list(VIDEO_MAP.keys())
    dostepne = [k for k in wszystkie if k not in st.session_state.watched_videos]
    
    if not dostepne:
        st.session_state.finished = True
        st.session_state.current_code = None
    else:
        nowy_kod = random.choice(dostepne)
        obecny_kod = st.session_state.get("current_code")
        
        while len(dostepne) > 1 and nowy_kod == obecny_kod:
            nowy_kod = random.choice(dostepne)
            
        st.session_state.current_code = nowy_kod
        st.session_state.rated = False
        st.session_state.video_ended = False

if st.session_state.get('current_code') is None:
    if not st.session_state.finished:
        losuj_nowe()


if st.session_state.finished:
    # === ETAP 4: EKRAN KOŃCOWY (DZIĘKUJEMY) ===
    st.balloons()
    st.title("Badanie zakończone!")
    st.success("Udało Ci się ocenić wszystkie sekwencje wideo.")
    
    st.markdown("""
    ### Dziękujemy za Twój czas i udział w eksperymencie.
    
    Twoje odpowiedzi zostały pomyślnie zapisane w naszej bazie danych. 
    Wszystkie zebrane informacje są anonimowe i posłużą do celów naukowych w analizie jakości wideo (QoE).
    
    Możesz teraz bezpiecznie zamknąć tę kartę przeglądarki.
    """)
    st.stop()

elif not st.session_state.intro_accepted:
    # === ETAP 1: EKRAN POWITALNY / INSTRUKCJA ===
    st.title("Witamy w badaniu jakości wideo")
    st.subheader("Dziękujemy za udział w teście.")
    
    st.markdown("""
    Badanie to powinno zająć około 20 minut.
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
    
    st.write("") 
    if st.button("ROZPOCZNIJ", type="primary"):
        st.session_state.intro_accepted = True
        st.rerun()

elif st.session_state.user_id is None:
    # === ETAP 2: ANKIETA DEMOGRAFICZNA ===
    st.title("Metryczka uczestnika")
    st.markdown("""
    Zanim przejdziemy do wideo, prosimy o kilka podstawowych informacji.
    Są one w pełni **anonimowe** i służą wyłącznie do celów naukowych.
    """)
    st.markdown("---")
    
    with st.form("demographics_form"):
        wiek = st.selectbox("Jaki jest Twój wiek?", 
                        ["< 18", "18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70+"])

        st.markdown("---")
        
        plec = st.radio("Płeć:", 
                        ["Mężczyzna", "Kobieta", "Inna", "Nie chcę podawać"])
        
        st.markdown("---")
        
        doswiadczenie = st.radio("Czy masz doświadczenie w testach percepcji (jakości)?",
                                 ["Nie", "Tak"])

        st.markdown("---")

        wzrok = st.selectbox("Jak oceniasz swój wzrok (ew. w korekcji)?", 
                         ["Doskonały", "Dobry", "Przeciętny", "Słaby", "Zły", "Trudno powiedzieć"])

        st.markdown("---")
        
        srodowisko = st.radio("Która opcja najlepiej opisuje Twoje otoczenie?",
                              ["Sam(a) w cichym pomieszczeniu", 
                               "Trochę hałasu i rozpraszaczy", 
                               "Znaczny hałas i rozpraszacze"])

        st.markdown("---")
        
        urzadzenie = st.radio("Z jakiego typu urządzenia korzystasz?",
                              ["Telefon", "Tablet", "Laptop", "Komputer stacjonarny"])
        
        submitted = st.form_submit_button("PRZEJDŹ DO TESTU WIDEO", type="primary")
        
        if submitted:
            with st.spinner("Generowanie profilu..."):
                uid = save_new_user(wiek, plec, doswiadczenie, wzrok, srodowisko, urzadzenie)
                if uid:
                    st.session_state.user_id = uid
                    # Resetujemy stan i losujemy pierwszy
                    st.session_state.watched_videos = []
                    losuj_nowe()
                    st.rerun()

else:
    # === ETAP 3: WŁAŚCIWY TEST WIDEO ===
    
    if st.session_state.current_code is None and not st.session_state.finished:
        losuj_nowe()
        st.rerun()

    code = st.session_state.current_code
    
    # Licznik postępu (opcjonalny, dla informacji użytkownika)
    progress_count = len(st.session_state.watched_videos) + 1
    total_videos = len(VIDEO_MAP)

    st.title("Badanie Jakości Wideo (QoE)")
    st.caption(f"ID: {st.session_state.user_id} | Wideo {progress_count} z {total_videos}")
    st.progress(len(st.session_state.watched_videos) / total_videos)
    
    st.info("Twoim zadaniem jest obejrzeć wyświetlony klip i ocenić jego jakość.")

    filename = VIDEO_MAP.get(code, "out_bigBuckBunny_1920x1080_3000k.mp4")
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
        <button id="start-btn" onclick="startVideo()">▶ ODTWÓRZ WIDEO</button>
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

        function checkFullscreen() {{
            var video = document.getElementById("my-video");
            var btn = document.getElementById("start-btn");
            
            if (!document.fullscreenElement && !document.webkitFullscreenElement && 
                !document.mozFullScreenElement && !document.msFullscreenElement) {{
                
                if (!video.ended) {{
                    video.pause();
                    video.style.display = "none";
                    btn.style.display = "inline-block";
                    btn.innerHTML = "KONTYNUUJ ODTWARZANIE";
                }}
            }}
        }}

        document.addEventListener('fullscreenchange', checkFullscreen);
        document.addEventListener('webkitfullscreenchange', checkFullscreen);
        document.addEventListener('mozfullscreenchange', checkFullscreen);
        document.addEventListener('msfullscreenchange', checkFullscreen);
        
        document.getElementById("my-video").addEventListener('ended', function(e) {{
            if (document.exitFullscreen) {{ document.exitFullscreen(); }}
            else if (document.webkitExitFullscreen) {{ document.webkitExitFullscreen(); }}
            
            setTimeout(function() {{
                var buttons = window.parent.document.getElementsByTagName("button");
                for (var i = 0; i < buttons.length; i++) {{
                    if (buttons[i].innerText.includes("Kliknij tutaj jeśli ankieta")) {{
                        buttons[i].click();
                        break;
                    }}
                }}
            }}, 500);
        }});
    </script>
    """
    
    if not st.session_state.video_ended:
        components.html(video_html, height=100)
    else:
        st.success("Wideo zakończone. Proszę wypełnić ankietę poniżej.")

    st.markdown("---")

    # --- OCENA ---
    
    if st.session_state.video_ended:
        st.header("Twoja ocena")
        if not st.session_state.rated:
            with st.form("rating_form"):
                st.write("**Jaka jest Twoja opinia o jakości wideo?**")
                ocena = st.slider("(1 - Fatalna, 5 - Doskonała)", 1, 5, 3)
                
                submitted = st.form_submit_button("ZATWIERDŹ OCENĘ", type="primary")
                
                if submitted:
                    with st.spinner("Zapisuję..."):
                        nazwa_pliku = VIDEO_MAP[code]
                        sukces = save_rating(st.session_state.user_id, nazwa_pliku, ocena)
                        if sukces:
                            st.success("Zapisano!")
                            # OZNACZAMY FILM JAKO OBEJRZANY
                            st.session_state.watched_videos.append(code)
                            st.session_state.rated = True
                            time.sleep(1)
                            losuj_nowe()
                            st.rerun()
        else:
            st.info("Wideo ocenione. Ładowanie kolejnego...")
    else:
        st.write("Ankieta pojawi się po zakończeniu wideo.")
        
        if st.button("Kliknij tutaj jeśli ankieta nie pojawi się automatycznie po filmie"):
            st.session_state.video_ended = True
            st.rerun()
            
        st.markdown('<style>iframe + div .stButton { opacity: 0; pointer-events: none; }</style>', unsafe_allow_html=True)


# --- SEKCJA RATUNKOWA (FIX NA ZACIĘCIA) ---
    st.write("")
    st.write("")
    # Używamy expandera, żeby nie rozpraszał użytkownika, jeśli wszystko działa dobrze
    with st.expander("⚠️ Masz problem techniczny? (Ekran się zaciął?)"):
        st.warning("Użyj tego przycisku TYLKO jeśli ekran zaciął się na komunikacie 'Ładowanie kolejnego...' lub wideo nie chce się załadować.")
        
        if st.button("🆘 WYMUŚ NASTĘPNE WIDEO"):
            # 1. Zabezpieczenie: uznajemy obecne wideo za "zaliczone", żeby nie wróciło
            if st.session_state.current_code and st.session_state.current_code not in st.session_state.watched_videos:
                st.session_state.watched_videos.append(st.session_state.current_code)
            
            # 2. Resetujemy kluczowe flagi stanu
            st.session_state.rated = False       # Reset flagi oceny
            st.session_state.video_ended = False # Reset flagi końca wideo
            
            # 3. Wymuszamy losowanie nowego wideo
            losuj_nowe()
            
            # 4. Twarde odświeżenie strony
            st.rerun()
