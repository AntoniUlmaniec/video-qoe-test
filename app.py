import streamlit as st
import random
import streamlit.components.v1 as components

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Badanie Jakosci Wideo", layout="centered")

# --- DANE KONFIGURACYJNE ---
BASE_URL = "https://github.com/AntoniUlmaniec/video-qoe-test/releases/download/v1.0/"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeBmQlBJMBmLk4kSiJ7EYgWlhpUyCz1wPuNjTYHXDPF1T7-Mw/viewform"
ENTRY_ID = "entry.2143728072"

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

# --- LOGIKA STANU (Session State) ---
if 'current_code' not in st.session_state:
    st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))

def losuj_nowe():
    lista_kodow = list(VIDEO_MAP.keys())
    nowy_kod = random.choice(lista_kodow)
    # Zabezpieczenie przed wylosowaniem tego samego dwa razy pod rząd
    while len(lista_kodow) > 1 and nowy_kod == st.session_state.current_code:
        nowy_kod = random.choice(lista_kodow)
    st.session_state.current_code = nowy_kod

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("Badanie Jakosci Wideo (QoE)")
st.info("Twoim zadaniem jest obejrzec wyswietlony klip i ocenic jego jakosc.")

code = st.session_state.current_code
filename = VIDEO_MAP[code]
video_url = BASE_URL + filename

st.subheader(f"Sekwencja testowa: {code}")

# --- SEKCJA HTML/JS DLA WIDEO (MODYFIKACJA BLOKADY ESC) ---
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

    /* Overlay - czyli nasza "nakładka" pełnoekranowa */
    #video-overlay {{
        display: none;          /* Domyślnie ukryty */
        position: fixed;        /* Przyklejony do okna */
        top: 0;
        left: 0;
        width: 100vw;           /* 100% szerokości widoku */
        height: 100vh;          /* 100% wysokości widoku */
        background-color: black;
        z-index: 999999;        /* Zawsze na wierzchu */
        text-align: center;
    }}

    /* Styl samego wideo wewnątrz nakładki */
    #my-video {{
        width: 100%;
        height: 100%;
        object-fit: contain;    /* Skalowanie bez obcinania (czarne pasy) */
        outline: none;
    }}
    
    /* Ukrycie paska przewijania w wideo */
    video::-webkit-media-controls-timeline {{
        display: none !important;
    }}
</style>

<div id="controls-container">
    <button id="start-btn" onclick="startVideo()">▶ ODTWÓRZ WIDEO (Pełny ekran)</button>
</div>

<div id="video-overlay">
    <video id="my-video" controlsList="nodownload noplaybackrate">
        <source src="{video_url}" type="video/mp4">
        Twoja przeglądarka nie obsługuje wideo.
    </video>
</div>

<script>
    var video = document.getElementById("my-video");
    var overlay = document.getElementById("video-overlay");

    function startVideo() {{
        // 1. Pokaż nakładkę (zasłania wszystko czarnym tłem)
        overlay.style.display = "block";
        
        // 2. Uruchom wideo
        video.play();
        
        // UWAGA: Nie używamy video.requestFullscreen(), 
        // dzięki temu ESC nie działa systemowo.
    }}
    
    // 3. Gdy wideo się skończy -> Ukryj nakładkę
    video.addEventListener('ended', function(e) {{
        overlay.style.display = "none";
    }});

    // 4. Dodatkowa blokada przycisku ESC (dla pewności)
    // Jeśli użytkownik naciśnie ESC, skrypt spróbuje zablokować akcję.
    document.addEventListener('keydown', function(e) {{
        if (e.key === "Escape" || e.keyCode === 27) {{
            e.preventDefault();
            console.log("Przycisk ESC zablokowany - czekaj na koniec wideo.");
            return false;
        }}
    }});
</script>
"""

# Renderowanie HTML - zwiększamy height komponentu, żeby przycisk był wygodny, 
# ale samo wideo i tak "wyskoczy" poza ten obszar dzięki position: fixed.
components.html(video_html, height=100)

st.markdown("---")

final_link = f"{FORM_URL}?usp=pp_url&{ENTRY_ID}={code}"

st.header("Twoja ocena")
st.write("1. Obejrzyj film powyzej.")
st.write("2. Kliknij przycisk OCEN, aby otworzyc ankiete.")
st.write(f"3. W ankiecie kod {code} wypelni sie automatycznie.")

st.link_button("KLIKNIJ TUTAJ, ABY OCENIC", final_link, type="primary")

st.markdown("---")
st.caption("Po wyslaniu ankiety wroc na te karte i wylosuj kolejny film.")

if st.button("Wylosuj kolejne wideo"):
    losuj_nowe()
    st.rerun()
