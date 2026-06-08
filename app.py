import streamlit as st
from google import genai
from google.genai import types
import random
import time
import warnings

# --- SETUP & CONFIG ---
warnings.filterwarnings("ignore")
st.set_page_config(page_title="Universal AI Agent Pro", page_icon="🔮", layout="centered")

# --- INITIALIZATION ---
if "blacklist" not in st.session_state:
    st.session_state.blacklist = {}

# --- FUNGSI LOGIN (GOOGLE OAUTH) ---
def perform_login():
    st.login("google")

# Proteksi Login (Wajib)
if not st.user.is_logged_in:
    st.markdown("## 🔮 Universal AI Agent Pro")
    st.warning("🔒 Aplikasi diproteksi oleh Google OAuth.")
    st.button("Log in with Google 🌐", on_click=perform_login, type="primary", use_container_width=True)
    st.stop()

# --- HEADER & PROFIL ---
email_aktif = st.user.email.strip().lower()
col_p, col_n = st.columns([4, 1])
with col_p:
    st.write(f"👤 **{st.user.name or 'User'}** | `{email_aktif}`")
with col_n:
    if st.button("Keluar 🚪"):
        st.logout()
        st.rerun()

st.markdown("---")

# --- LOGIKA AI PINTAR ---
def adalah_tersedia(key, model):
    key_id = f"{key[:5]}_{model}"
    if key_id in st.session_state.blacklist:
        if time.time() < st.session_state.blacklist[key_id]:
            return False
        else:
            del st.session_state.blacklist[key_id]
    return True

def jalankan_ai_pintar(tugas, profesi):
    # Mengambil key dari secrets
    if "gemini" not in st.secrets or "gcp_api_keys" not in st.secrets["gemini"]:
        return None, "API Key tidak ditemukan di Secrets!"
        
    keys = [k.strip() for k in st.secrets["gemini"]["gcp_api_keys"].split("\n") if k.strip()]
    models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    random.shuffle(keys)
    
    for key in keys:
        for model in models:
            if not adalah_tersedia(key, model):
                continue
            try:
                client = genai.Client(api_key=key)
                res = client.models.generate_content(
                    model=model,
                    contents=tugas,
                    config=types.GenerateContentConfig(
                        system_instruction=f"Anda adalah pakar {profesi}"
                    )
                )
                return res.text, model
            except Exception as e:
                if "429" in str(e):
                    st.session_state.blacklist[f"{key[:5]}_{model}"] = time.time() + 60
                    continue
                else:
                    return None, f"Error: {e}"
    return None, "Semua model/key terkena limit. Tunggu sebentar."

# --- UI WORKSPACE ---
st.subheader("🚀 Ruang Kerja Agen")
profesi = st.text_input("Profesi Ahli:", placeholder="Contoh: Database Administrator")
tugas = st.text_area("Tugas Anda:", placeholder="Tuliskan tugas di sini...")

if st.button("Jalankan Mesin ⚡", type="primary"):
    if profesi and tugas:
        with st.spinner("Memproses dengan cerdas..."):
            hasil, info = jalankan_ai_pintar(tugas, profesi)
            if hasil:
                st.success(f"Berhasil menggunakan model: {info}")
                st.markdown(hasil)
            else:
                st.error(info)
    else:
        st.warning("Mohon isi semua kolom.")