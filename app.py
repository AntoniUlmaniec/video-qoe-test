import streamlit as st
import random

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeBmQlBJMBmLk4kSiJ7EYgWlhpUyCz1wPuNjTYHXDPF1T7-Mw/viewform"
ENTRY_ID = "entry.2143728072"

VIDEO_DB = {
    "video_01.mp4": "https://drive.google.com/file/d/1-cISeIup5fTpuJsXXNIIO3OAnjXzKHkF/view?usp=sharing",
    "video_02.mp4": "https://drive.google.com/file/d/11Ybp3fFQdGNT_R9EGHatDebWp7DwHVWo/view?usp=sharing",
    "video_03.mp4": "https://drive.google.com/file/d/11exk-3xMt0nkxn2IriHDvtLiKhaCORQ3/view?usp=sharing",
    "video_04.mp4": "https://drive.google.com/file/d/11l_jLMG_0kGTaJMWBAJf7agXSqQsH30U/view?usp=sharing",
    "video_05.mp4": "https://drive.google.com/file/d/16umKtzgKaf7Ub-xCwzHwlLIWF3My1xdx/view?usp=sharing",
    "video_06.mp4": "https://drive.google.com/file/d/1AbqIA9LEy0KCbXnM8Lup313l2mnIdT_r/view?usp=sharing",
    "video_07.mp4": "https://drive.google.com/file/d/1D6pISFRy4oZsHfOYfRMP4YauGuUAWN84/view?usp=sharing",
    "video_08.mp4": "https://drive.google.com/file/d/1DU49G8D5bMVh8xJNVnwNueAl8kc_0Mdu/view?usp=sharing",
    "video_09.mp4": "https://drive.google.com/file/d/1Dj8Koc1_TMXkexOYDAeDIAaaqnzwm2u9/view?usp=sharing",
    "video_10.mp4": "https://drive.google.com/file/d/1K_K80VR5OM4x2oHgMcNOxuDUDFLbCHdt/view?usp=sharing",
    "video_11.mp4": "https://drive.google.com/file/d/1MN-WMCjNikZ2dQTCizi0O8tFKsnOajRk/view?usp=sharing",
    "video_12.mp4": "https://drive.google.com/file/d/1TBLQYu-B4Db5rmPuHV0uJDLNN7p4kYTI/view?usp=sharing",
    "video_13.mp4": "https://drive.google.com/file/d/1UsTUDMC8-89O3tS9viWu_buI5PLU_t_f/view?usp=sharing",
    "video_14.mp4": "https://drive.google.com/file/d/1XXrHMaLVJMLXyO-6b1w2vzT2v2upPgx8/view?usp=sharing",
    "video_15.mp4": "https://drive.google.com/file/d/1_UEUESNoq6mjDp6g3Hx-QfFhQDIz9TCs/view?usp=sharing",
    "video_16.mp4": "https://drive.google.com/file/d/1bj0vgHxBk2gdbmpoT1DBGCjYrxp-l_i_/view?usp=sharing",
    "video_17.mp4": "https://drive.google.com/file/d/1hK9eFYex99_lY6Ng1b8fZEWlT_kJy-jV/view?usp=sharing",
    "video_18.mp4": "https://drive.google.com/file/d/1iU_P4CV_lMP0zaEE5AeGB3gsWf_Q4yIP/view?usp=sharing",
    "video_19.mp4": "https://drive.google.com/file/d/1inKHRy1fm4j_DMwqlK9T00Cit7nv83jK/view?usp=sharing",
    "video_20.mp4": "https://drive.google.com/file/d/1kRB5cts-AJGxB58z94hsSvf7IAmofmsK/view?usp=sharing",
    "video_21.mp4": "https://drive.google.com/file/d/1m4NVhN78g_K_4cS67ZAk6vHVfCq3dIJc/view?usp=sharing",
    "video_22.mp4": "https://drive.google.com/file/d/1rzSnjfUJ3KVT081oZluYJi-HqUuzXokj/view?usp=sharing",
    "video_23.mp4": "https://drive.google.com/file/d/1s2_rodIt7OihGFM9oCzKYGZ9YY2eFiTW/view?usp=sharing",
    "video_24.mp4": "https://drive.google.com/file/d/1u5Siwd7RIP0fMTDaammR_fgnlaSfB5Pv/view?usp=sharing"
}

def get_direct_link(google_link):
    """Zamienia link podglądu na link bezpośredniego pobierania (oryginalna jakość)"""
    try:
        file_id = google_link.split('/d/')[1].split('/')[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except IndexError:
        return google_link

if 'current_video_key' not in st.session_state:
    st.session_state.current_video_key = random.choice(list(VIDEO_DB.keys()))

def losuj_nowe():
    """Losuje nowe wideo z listy"""
    lista_kluczy = list(VIDEO_DB.keys())
    nowy_klucz = random.choice(lista_kluczy)
    if len(lista_kluczy) > 1:
        while nowy_klucz == st.session_state.current_video_key:
            nowy_klucz = random.choice(lista_kluczy)
    st.session_state.current_video_key = nowy_klucz

st.set_page_config(page_title="Badanie Jakości Wideo", layout="centered")

st.title("🎬 Badanie Jakości Wideo (QoE)")
st.info("Twoim zadaniem jest obejrzeć wyświetlony klip i ocenić jego jakość.")

# Pobieramy aktualny film (z pamięci sesji)
video_filename = st.session_state.current_video_key
raw_link = VIDEO_DB[video_filename]
direct_link = get_direct_link(raw_link)

# Wyświetlamy
st.subheader("🎥 Oglądasz losową sekwencję")
st.video(direct_link)

st.markdown("---")

# Tworzymy inteligentny link do formularza
final_link = f"{FORM_URL}?usp=pp_url&{ENTRY_ID}={video_filename}"

st.header("Twoja ocena")
st.write("1. Obejrzyj film powyżej.")
st.write("2. Kliknij przycisk **OCEŃ**, aby otworzyć ankietę.")
st.write("3. W ankiecie pole z nazwą pliku wypełni się automatycznie!")

# Wielki przycisk odsyłający do ankiety
st.link_button("KLIKNIJ TUTAJ, ABY OCENIĆ", final_link, type="primary")

st.markdown("---")
st.caption("Po wysłaniu ankiety wróć na tę kartę i wyświetl kolejny film.")

if st.button("Kolejne wideo"):
    losuj_nowe()
    st.rerun()
