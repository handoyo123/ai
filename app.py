import streamlit as st
from google import genai
from google.genai import types
import random
import warnings

# Pengaturan Global
warnings.filterwarnings("ignore")
st.set_page_config(page_title="Universal AI Agent Pro", page_icon="🔮", layout="centered")

# --- 1. SISTEM LOGIN EMAIL WHITELIST ---
EMAIL_WHITELIST = ["handoyoyy1@gmail.com"]

def check_login():
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
        st.session_state.user_email = ""

    if not st.session_state.is_logged_in:
        st.markdown("## 🔮 Universal AI Agent Pro")
        email_input = st.text_input("Masukkan Email Anda:")
        if st.button("Masuk"):
            if email_input.lower() in EMAIL_WHITELIST:
                st.session_state.is_logged_in = True
                st.session_state.user_email = email_input
                st.rerun()
            else:
                st.error("Email tidak terdaftar!")
        st.stop()

check_login()

# --- 2. LOGIKA ROTASI API KEY (Mengatasi Error 429) ---
def dapatkan_client():
    if "gemini" in st.secrets and "gcp_api_keys" in st.secrets["gemini"]:
        # Mengambil semua key dan memisahkannya per baris
        raw_keys = st.secrets["gemini"]["gcp_api_keys"].strip()
        keys = [k.strip() for k in raw_keys.split("\n") if k.strip()]
        
        # Memilih salah satu key secara acak
        key_aktif = random.choice(keys)
        return genai.Client(api_key=key_aktif)
    return None

# --- 3. UI DAN LOGIKA AI ---
st.write(f"👤 **User:** {st.session_state.user_email}")
if st.button("Keluar 🚪"):
    st.session_state.is_logged_in = False
    st.rerun()

st.markdown("---")
st.subheader("🚀 Ruang Kerja Agen")
profesi = st.text_input("Profesi Ahli:", placeholder="Contoh: Database Administrator")
tugas = st.text_area("Tugas Anda:", placeholder="Tuliskan tugas di sini...")

if st.button("Jalankan Mesin ⚡", type="primary"):
    if profesi and tugas:
        client = dapatkan_client()
        if client:
            with st.spinner("Memproses dengan rotasi API Key..."):
                try:
                    res = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=tugas,
                        config=types.GenerateContentConfig(
                            system_instruction=f"Anda adalah pakar {profesi}", 
                            temperature=0.2
                        ),
                    )
                    st.session_state.hasil = res.text
                    st.success("Tugas Selesai!")
                except Exception as e:
                    st.error(f"Error API (Coba klik tombol lagi untuk ganti key): {e}")
        else:
            st.error("API Key belum diset di Secrets!")
    else:
        st.warning("Mohon isi semua kolom.")

if "hasil" in st.session_state:
    st.markdown(st.session_state.hasil)