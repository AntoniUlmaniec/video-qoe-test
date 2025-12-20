import streamlit as st
import random
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="Badanie Jakosci Wideo", layout="centered")

#GOOGLE SHEETS
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
        
        sheet.append_row([user_id, timestamp, video_filename, rating])
        return True
    except Exception as e:
        st.error(f"Błąd zapisu oceny: {e}")
        return False

BASE_URL = "https://pub-06f5e0d0b2794648af3dc511ad0b8b72.r2.dev/"

VIDEO_MAP = {
    "TRAIN_01": "training-01.mp4",
    "TRAIN_02": "training-02.mp4",

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

#APP STATE MANAGEMENT
if 'intro_accepted' not in st.session_state:
    st.session_state.intro_accepted = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0
if 'training_done' not in st.session_state:
    st.session_state.training_done = False 
if 'training_step' not in st.session_state:
    st.session_state.training_step = 0    

#PROGRESS TRACKING VARIABLES
if 'watched_videos' not in st.session_state:
    st.session_state.watched_videos = []
if 'finished' not in st.session_state:
    st.session_state.finished = False

#RANDOMIZATION LOGIC
def pick_new_video():
    if not st.session_state.training_done:
        if st.session_state.training_step == 0:
            st.session_state.current_code = "TRAIN_01"
        elif st.session_state.training_step == 1:
            st.session_state.current_code = "TRAIN_02"
        else:
            st.session_state.training_done = True
            pick_new_video()
            return

        st.session_state.rated = False
        st.session_state.video_ended = False
        return

    all_codes = list(VIDEO_MAP.keys())
    real_codes = [k for k in all_codes if "TRAIN" not in k]
    available_codes = [k for k in real_codes if k not in st.session_state.watched_videos]
    
    if not available_codes:
        st.session_state.finished = True
        st.session_state.current_code = None
    else:
        new_code = random.choice(available_codes)
        current_code = st.session_state.get("current_code")
        
        while len(available_codes) > 1 and new_code == current_code:
            new_code = random.choice(available_codes)
            
        st.session_state.current_code = new_code
        st.session_state.rated = False
        st.session_state.video_ended = False

if st.session_state.get('current_code') is None:
    if not st.session_state.finished:
        pick_new_video()


if st.session_state.finished:
    #END SCREEN
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
    #INTRO
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
    #DEMOGRAPHICS
    st.title("Metryczka uczestnika")
    st.markdown("""
    Zanim przejdziemy do wideo, prosimy o kilka podstawowych informacji.
    Są one w pełni **anonimowe** i służą wyłącznie do celów naukowych.
    """)
    st.markdown("---")
    
    with st.form("demographics_form"):
        user_age = st.selectbox("Jaki jest Twój wiek?", 
                            ["< 18", "18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70+"])

        st.markdown("---")
        
        user_gender = st.radio("Płeć:", 
                        ["Mężczyzna", "Kobieta", "Inna", "Nie chcę podawać"])
        
        st.markdown("---")
        
        user_experience = st.radio("Czy masz doświadczenie w testach percepcji (jakości)?",
                                 ["Nie", "Tak"])

        st.markdown("---")

        user_vision = st.selectbox("Jak oceniasz swój wzrok (ew. w korekcji)?", 
                         ["Doskonały", "Dobry", "Przeciętny", "Słaby", "Zły", "Trudno powiedzieć"])

        st.markdown("---")
        
        user_environment = st.radio("Która opcja najlepiej opisuje Twoje otoczenie?",
                              ["Sam(a) w cichym pomieszczeniu", 
                               "Trochę hałasu i rozpraszaczy", 
                               "Znaczny hałas i rozpraszacze"])

        st.markdown("---")
        
        user_device = st.radio("Z jakiego typu urządzenia korzystasz?",
                              ["Telefon", "Tablet", "Laptop", "Komputer stacjonarny"])
        
        submitted = st.form_submit_button("PRZEJDŹ DO TESTU WIDEO", type="primary")
        
        if submitted:
            with st.spinner("Generowanie profilu..."):
                uid = save_new_user(user_age, user_gender, user_experience, user_vision, user_environment, user_device)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.watched_videos = []
                    pick_new_video()
                    st.rerun()

else:
    #VIDEO TEST
    
    if st.session_state.current_code is None and not st.session_state.finished:
        pick_new_video()
        st.rerun()
    
    code = st.session_state.current_code
    
    if not st.session_state.training_done:
        st.title("Faza Treningowa")
        st.info("To jest wideo szkoleniowe. Zapoznaj się z procesem oceniania.")

        train_current = st.session_state.training_step + 1
        train_total = 2
        
        st.caption(f"ID: {st.session_state.user_id} | Wideo {train_current} z {train_total}")
        st.progress(train_current / train_total)
        
    else:
        progress_count = len(st.session_state.watched_videos) + 1
        total_videos = len(VIDEO_MAP) - 2 
        
        if total_videos < 1: total_videos = 1
        
        current_progress = len(st.session_state.watched_videos) / total_videos
        if current_progress > 1.0: current_progress = 1.0

        st.title("Badanie Jakości Wideo (QoE)")
        st.caption(f"ID: {st.session_state.user_id} | Wideo {progress_count} z {total_videos}")
        st.progress(current_progress)
        
        st.info("Twoim zadaniem jest obejrzeć wyświetlony klip i ocenić jego jakość.")

    filename = VIDEO_MAP.get(code, "out_bigBuckBunny_1920x1080_3000k.mp4")
    video_url = BASE_URL + filename

    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    video_html = f"""
    <!-- RESET_ID: {st.session_state.reset_counter} -->
    <style>
        #video-container {{ position: relative; width: 100%; text-align: center; }}
        #start-btn {{
            background-color: #cccccc; color: #666666; padding: 15px 32px;
            text-align: center; display: inline-block; font-size: 16px;
            margin: 4px 2px; border: none; border-radius: 4px;
            width: 100%; font-weight: bold; cursor: not-allowed;
            pointer-events: none; transition: background-color 0.3s;
        }}
        #start-btn.ready {{
            background-color: #FF4B4B; color: white; cursor: pointer; pointer-events: auto;
        }}
        #start-btn.ready:hover {{ background-color: #FF2B2B; }}
        video::-webkit-media-controls-timeline {{ display: none !important; }}
        #my-video {{ display: none; width: 100%; }}
        
        #loading-status {{ margin-top: 10px; font-family: sans-serif; font-size: 14px; color: #555; }}
        #progress-container {{ width: 100%; background-color: #e0e0e0; border-radius: 8px; margin-top: 5px; height: 10px; overflow: hidden; }}
        #progress-bar {{ width: 0%; height: 100%; background-color: #4CAF50; transition: width 0.1s; }}
    </style>

    <div id="video-container">
        <div id="loading-ui">
            <button id="start-btn" onclick="startVideo()">ŁADOWANIE WIDEO...</button>
            <div id="loading-status"><span id="percent-text">0%</span></div>
            <div id="progress-container">
                <div id="progress-bar"></div>
            </div>
        </div>

        <video id="my-video" controlsList="nodownload noplaybackrate">
        </video>
    </div>

    <script>
        var video = document.getElementById("my-video");
        var btn = document.getElementById("start-btn");
        var pBar = document.getElementById("progress-bar");
        var pText = document.getElementById("percent-text");
        var videoUrl = "{video_url}";

        var xhr = new XMLHttpRequest();
        xhr.open("GET", videoUrl, true);
        xhr.responseType = "blob";

        xhr.onprogress = function(event) {{
            if (event.lengthComputable) {{
                var percent = (event.loaded / event.total) * 100;
                pBar.style.width = percent + "%";
                pText.innerText = Math.round(percent) + "%";
            }}
        }};

        xhr.onload = function(event) {{
            if (xhr.status === 200) {{
                var blob = xhr.response;
                var blobUrl = URL.createObjectURL(blob);
                
                video.src = blobUrl;
                
                pBar.style.width = "100%";
                pText.innerText = "100%";
                enablePlayButton();
            }} else {{
                pText.innerText = "Błąd pobierania (" + xhr.status + ")";
            }}
        }};

        xhr.onerror = function() {{ pText.innerText = "Błąd sieci."; }};
        xhr.send();

        function enablePlayButton() {{
            btn.classList.add("ready");
            btn.innerHTML = "ODTWÓRZ WIDEO";
            pBar.style.backgroundColor = "#FF4B4B";
        }}

        function startVideo() {{
            document.getElementById("loading-status").style.display = "none";
            document.getElementById("progress-container").style.display = "none";
            
            video.style.display = "block";
            btn.style.display = "none";
            video.play();
            
            if (video.requestFullscreen) {{ video.requestFullscreen(); }}
            else if (video.webkitRequestFullscreen) {{ video.webkitRequestFullscreen(); }}
        }}

        function checkFullscreen() {{
            if (!document.fullscreenElement && !document.webkitFullscreenElement && 
                !document.mozFullScreenElement && !document.msFullscreenElement) {{
                if (!video.ended && video.currentTime > 0) {{ // Dodatkowe zabezpieczenie
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
                var sidebars = window.parent.document.querySelectorAll('[data-testid="stSidebar"]');
                if (sidebars.length > 0) {{
                    var buttons = sidebars[0].getElementsByTagName("button");
                    for (var i = 0; i < buttons.length; i++) {{
                        if (buttons[i].innerText.includes("NEXT_STEP_TRIGGER")) {{
                            buttons[i].click();
                            break;
                        }}
                    }}
                }}
            }}, 500);
        }});
    </script>
    """

    if not st.session_state.video_ended:
        components.html(video_html, height=100)
        
        with st.sidebar:
            if st.button("NEXT_STEP_TRIGGER"):
                st.session_state.video_ended = True
                st.rerun()
    else:
        st.success("Wideo zakończone. Proszę wypełnić ankietę poniżej.")

    st.markdown("---")

    #RATING
    if st.session_state.video_ended:
        st.header("Twoja ocena")
        if not st.session_state.rated:
            with st.form("rating_form"):
                st.write("**Jaka jest Twoja opinia o jakości wideo?**")
                
                rating_options = ["5 - Doskonała", "4 - Dobra", "3 - Przeciętna", "2 - Słaba", "1 - Fatalna"]
                selected_rating = st.radio("Wybierz ocenę:", rating_options, index=2, label_visibility="collapsed")
                
                submitted = st.form_submit_button("ZATWIERDŹ OCENĘ", type="primary")
                
                if submitted:
                    if code in st.session_state.watched_videos:
                        st.warning("Ta ocena została już zapisana.")
                        time.sleep(1)
                        pick_new_video()
                        st.rerun()

                    else:
                        with st.spinner("Zapisuję..."):
                            rating_int = int(selected_rating.split(" - ")[0])
                            
                            if not st.session_state.training_done:
                                st.success("Ocena Treningowa przyjęta!")
                                st.session_state.training_step += 1 
                                st.session_state.rated = True
                                time.sleep(1)
                                pick_new_video() 
                                st.rerun()
                            else:
                                target_filename = VIDEO_MAP[code]
                                save_success = save_rating(st.session_state.user_id, target_filename, rating_int)
                                
                                if save_success:
                                    st.success("Zapisano!")
                                    st.session_state.watched_videos.append(code)
                                    st.session_state.rated = True
                                    time.sleep(1)
                                    pick_new_video()
                                    st.rerun()
        else:
            st.info("Wideo ocenione. Ładowanie kolejnego...")
    else:
        st.write("Ankieta pojawi się automatycznie po zakończeniu wideo.")

    #RESCUE SECTION
    st.write("")
    st.write("")
    with st.expander("Wideo się zacięło lub ankieta nie działa?"):
        st.warning("Kliknij poniżej, aby przeładować wideo i spróbować ponownie.")
        if st.button("ZRESETUJ WIDEO"):
            st.session_state.rated = False
            st.session_state.video_ended = False
            st.session_state.reset_counter += 1
            st.rerun()
