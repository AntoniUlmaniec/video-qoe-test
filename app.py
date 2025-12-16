import streamlit as st
import random

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

if 'current_code' not in st.session_state:
    st.session_state.current_code = random.choice(list(VIDEO_MAP.keys()))

if 'video_playing' not in st.session_state:
    st.session_state.video_playing = False

def losuj_nowe():
    lista_kodow = list(VIDEO_MAP.keys())
    nowy_kod = random.choice(lista_kodow)
    while len(lista_kodow) > 1 and nowy_kod == st.session_state.current_code:
        nowy_kod = random.choice(lista_kodow)
    st.session_state.current_code = nowy_kod
    st.session_state.video_playing = False

st.set_page_config(page_title="Badanie Jakosci Wideo", layout="centered")

st.title("Badanie Jakosci Wideo (QoE)")
st.info("Twoim zadaniem jest obejrzec wyswietlony klip i ocenic jego jakosc.")

code = st.session_state.current_code
filename = VIDEO_MAP[code]
video_url = BASE_URL + filename

st.subheader(f"Sekwencja testowa: {code}")

if not st.session_state.video_playing:
    if st.button("Odtwórz wideo"):
        st.session_state.video_playing = True
        st.rerun()
else:
    video_html = f"""
    <style>
        video::-webkit-media-controls-timeline {{
            display: none !important;
        }}
    </style>
    <video width="100%" controls autoplay name="media">
        <source src="{video_url}" type="video/mp4">
    </video>
    <script>
        const video = document.querySelector('video');
        if (video) {{
            video.requestFullscreen().catch(err => {{
                console.log("Fullscreen blocked by browser");
            }});
        }}
    </script>
    """
    st.markdown(video_html, unsafe_allow_html=True)

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
