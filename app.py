import streamlit as st
from google import genai
from google.genai import types
import random
import warnings

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Universal AI Agent Pro", page_icon="🔮", layout="centered")

# --- 1. SISTEM LOGIN EMAIL WHITELIST ---
# Daftarkan email yang diizinkan di sini
EMAIL_WHITELIST = ["handoyoyy1@gmail.com", "partner@email.com"]

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

# --- 2. FITUR UTAMA (Sama seperti sebelumnya) ---
col_p, col_n = st.columns([4, 1])
with col_p:
    st.write(f"👤 **{st.session_state.user_email}**")
with col_n:
    if st.button("Keluar 🚪"):
        st.session_state.is_logged_in = False
        st.rerun()

st.markdown("---")

# --- 3. LOGIKA AI ---
def dapatkan_client():
    if "gemini" in st.secrets and "gcp_api_keys" in st.secrets["gemini"]:
        keys = st.secrets["gemini"]["gcp_api_keys"].strip().split("\n")
        key_aktif = random.choice([k.strip() for k in keys if k.strip()])
        return genai.Client(api_key=key_aktif)
    return None

st.subheader("🚀 Ruang Kerja Agen")
profesi = st.text_input("Profesi Ahli:", placeholder="Contoh: Database Administrator")
tugas = st.text_area("Tugas Anda:", placeholder="Tuliskan tugas di sini...")

if st.button("Jalankan Mesin ⚡", type="primary"):
    if profesi and tugas:
        client = dapatkan_client()
        if client:
            with st.spinner("Memproses..."):
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
                    st.error(f"Error API: {e}")
        else:
            st.error("API Key belum diset di Secrets!")
    else:
        st.warning("Mohon isi semua kolom.")

if "hasil" in st.session_state:
    st.markdown(st.session_state.hasil)