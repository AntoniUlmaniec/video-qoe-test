import streamlit as st
import random
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit.components.v1 as components
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Badanie Jakości Wideo", 
    page_icon="🎬", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (STYLISTYKA) ---
def local_css():
    st.markdown("""
    <style>
        /* Ogólny styl nagłówków */
        h1 {
            color: #2E2E2E;
            text-align: center;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
        }
        h2, h3 {
            color: #4F4F4F;
            text-align: center;
        }
        
        /* Stylizacja kontenera wideo */
        .video-box {
            background-color: #000000;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Przyciski */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            font-weight: bold;
        }
        
        /* Ukrywanie przycisku 'Bridge' (zachowanie logiki oryginalnej) */
        .hidden-bridge {
            opacity: 0;
            pointer-events: none;
            height: 0;
        }
        
        /* Styl suwaka */
        .stSlider {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- KONFIGURACJA GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hDmQqQdy7jitS5B8Ah_k6mV31HA9QGRYpm63ISODrbg/edit?hl=pl&gid=310694828#gid=310694828"

def get_google_sheet_client():
    """Pomocnicza funkcja do autoryzacji."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    return client

def save_new_user(age, gender, experience, vision, environment, device):
    """Tworzy nowego użytkownika, generuje ID i zapisuje w zakładce 'Uczestnicy'."""
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

def save_rating(user_id, video_code, rating):
    """Zapisuje ocenę wideo w zakładce 'Wyniki'."""
    try:
        client = get_google_sheet_client()
        sheet = client.open_by_url(SHEET_URL).worksheet("Wyniki")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zapis: User_ID, Data, Kod Wideo, Ocena
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
if 'intro_accepted' not in st.session_state:
    st.session_state.intro_accepted = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- Pasek boczny (informacje techniczne) ---
if st.session_state.user_id:
    with st.sidebar:
        st.write("### 👤 Profil Uczestnika")
        st.code(st.session_state.user_id, language="text")
        st.caption("To jest Twój anonimowy identyfikator sesji.")
        st.markdown("---")
        st.write("Status systemu: 🟢 Online")

# --- LOGIKA WYŚWIETLANIA ---

if not st.session_state.intro_accepted:
    # === ETAP 1: EKRAN POWITALNY / INSTRUKCJA ===
    st.markdown("# 🎬 Badanie Jakości Wideo")
    st.markdown("### Witamy w eksperymencie QoE")
    
    st.divider()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/fluency/240/video-playlist.png", caption="Video Quality Assessment")
    
    with col2:
        st.markdown("""
        ### Cel badania
        Twoim zadaniem będzie obejrzenie serii krótkich sekwencji wideo i ocena ich jakości.
        
        **Ważne informacje:**
        * 👁️ Skup się wyłącznie na **jakości obrazu** (ostrość, płynność, artefakty).
        * 🔊 Test najlepiej wykonywać w cichym otoczeniu.
        * 🧠 Nie ma złych odpowiedzi – liczy się Twoja subiektywna opinia.
        """)
    
    st.info("""
    **Przebieg:**
    1. Obejrzyj klip od początku do końca.
    2. Po zakończeniu wideo pojawi się suwak z oceną.
    3. Zaznacz swoją opinię i zatwierdź.
    """)
    
    st.write("") 
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if st.button("🚀 ROZPOCZNIJ BADANIE", type="primary"):
            st.session_state.intro_accepted = True
            st.rerun()

elif st.session_state.user_id is None:
    # === ETAP 2: ANKIETA DEMOGRAFICZNA ===
    st.markdown("# 📝 Metryczka uczestnika")
    st.markdown("""
    <div style='text-align: center; color: gray; margin-bottom: 30px;'>
    Prosimy o podanie podstawowych informacji. Dane są w pełni anonimowe.
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("demographics_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                wiek = st.selectbox("Jaki jest Twój wiek?", 
                                ["< 18", "18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70+"])
                
                wzrok = st.selectbox("Jak oceniasz swój wzrok (ew. w korekcji)?", 
                             ["Doskonały", "Dobry", "Przeciętny", "Słaby", "Zły", "Trudno powiedzieć"])
                
                urzadzenie = st.radio("Z jakiego typu urządzenia korzystasz?",
                                  ["Telefon", "Tablet", "Laptop", "Komputer stacjonarny"])

            with col_b:
                plec = st.radio("Płeć:", 
                            ["Mężczyzna", "Kobieta", "Inna", "Nie chcę podawać"])
                
                st.write("") # Spacer
                doswiadczenie = st.radio("Czy masz doświadczenie w testach percepcji (jakości)?",
                                     ["Nie", "Tak"])
                
                st.write("") # Spacer
                srodowisko = st.radio("Otoczenie:",
                                  ["Sam(a) w cichym pomieszczeniu", 
                                   "Trochę hałasu i rozpraszaczy", 
                                   "Znaczny hałas i rozpraszacze"])
            
            st.markdown("---")
            submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
            with submit_col2:
                submitted = st.form_submit_button("PRZEJDŹ DO TESTU WIDEO", type="primary")
            
            if submitted:
                with st.spinner("Generowanie profilu..."):
                    uid = save_new_user(wiek, plec, doswiadczenie, wzrok, srodowisko, urzadzenie)
                    if uid:
                        st.session_state.user_id = uid
                        st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))
                        st.session_state.rated = False
                        st.session_state.video_ended = False
                        st.rerun()

else:
    # === ETAP 3: WŁAŚCIWY TEST WIDEO ===
    
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
        st.session_state.video_ended = False

    # Nagłówek sekcji testowej
    st.markdown("### 👁️ Ocena Jakości")
    
    # Progress bar (fake - visual only, or could be implemented properly if we tracked count)
    st.progress(0, text="Sekwencja testowa w toku...") 

    code = st.session_state.current_code
    filename = VIDEO_MAP.get(code, "out_bigBuckBunny_1920x1080_3000k.mp4")
    video_url = BASE_URL + filename

    # --- UKRYTY PRZYCISK "BRIDGE" ---
    if not st.session_state.video_ended:
        placeholder = st.empty()
        # Dodajemy klasę CSS .hidden-bridge wewnątrz markdowne, aby ukryć kontener przycisku
        st.markdown('<style>iframe + div .stButton { opacity: 0; pointer-events: none; height: 0; margin: 0; }</style>', unsafe_allow_html=True)
        
        if placeholder.button("Kliknij tutaj jeśli ankieta nie pojawi się automatycznie po filmie", key="bridge_btn"):
            st.session_state.video_ended = True
            st.rerun()
    
    # --- PLAYER WIDEO ---
    if not st.session_state.video_ended:
        st.markdown(f'<div class="video-box">Odtwarzanie: <b>{code}</b></div>', unsafe_allow_html=True)
        
        video_html = f"""
        <style>
            #start-btn {{
                background: linear-gradient(90deg, #FF4B4B 0%, #FF2B2B 100%);
                color: white; padding: 15px 32px;
                text-align: center; display: inline-block; font-size: 18px;
                margin: 4px 2px; cursor: pointer; border: none; border-radius: 8px;
                width: 100%; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                transition: transform 0.1s;
            }}
            #start-btn:hover {{ transform: scale(1.02); }}
            video::-webkit-media-controls-timeline {{ display: none !important; }}
            #my-video {{ display: none; width: 100%; border-radius: 8px; }}
            body {{ background-color: transparent; }}
        </style>

        <div id="video-container" style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
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
        components.html(video_html, height=450)
    else:
        st.success("✅ Wideo zakończone pomyślnie.")

    st.divider()

    # --- OCENA ---
    if st.session_state.video_ended:
        with st.container(border=True):
            st.header("📊 Twoja ocena")
            if not st.session_state.rated:
                with st.form("rating_form"):
                    st.markdown("<h4 style='text-align: center;'>Jak oceniasz jakość tego wideo?</h4>", unsafe_allow_html=True)
                    
                    # Suwak z etykietami
                    cols = st.columns([1, 8, 1])
                    with cols[0]: st.write("👎 Fatalna")
                    with cols[1]: 
                        ocena = st.slider("", 1, 5, 3, label_visibility="collapsed")
                    with cols[2]: st.write("Doskonała 👍")
                    
                    st.write("")
                    
                    submit_btn = st.form_submit_button("ZATWIERDŹ OCENĘ", type="primary")
                    
                    if submit_btn:
                        with st.spinner("Zapisywanie odpowiedzi..."):
                            sukces = save_rating(st.session_state.user_id, code, ocena)
                            if sukces:
                                st.toast("Zapisano ocenę!", icon="✅")
                                st.session_state.rated = True
                                time.sleep(1)
                                losuj_nowe()
                                st.rerun()
            else:
                st.info("Wideo ocenione. Ładowanie kolejnego...")
    else:
        st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
        Ankieta oceny pojawi się tutaj automatycznie po zakończeniu odtwarzania.
        </div>
        """, unsafe_allow_html=True)

    # --- STOPKA / AWARYJNE POMINIĘCIE ---
    st.write("")
    st.write("")
    with st.expander("⚠️ Masz problem z odtwarzaniem?"):
        st.warning("Jeśli wideo się nie ładuje lub zacięło, możesz wylosować inne.")
        if st.button("Pomiń to wideo i wylosuj inne"):
            losuj_nowe()
            st.rerun()
