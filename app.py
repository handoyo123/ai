import streamlit as st
from google import genai
from google.genai import types
from docx import Document
import random
import os
import io
import json
import warnings

# Pengaturan Global
warnings.filterwarnings("ignore")
st.set_page_config(page_title="Universal AI Agent Pro", page_icon="🔮", layout="centered")

# ==============================================================================
# 1. AUTHENTICATION & DATABASE CORE
# ==============================================================================
EMAIL_ADMIN = "handoyoyy1@gmail.com"

# Fungsi Login dengan mekanisme Rerunning yang kuat
def handle_login():
    st.login()
    st.rerun()

# Cek Login Status (Ini adalah kunci utama agar masuk ke aplikasi)
if not st.user.is_logged_in:
    st.write("")
    with st.container(border=True):
        st.markdown("## 🔮 Universal AI Agent Pro")
        st.warning("🔒 Aplikasi ini diproteksi oleh Google OAuth.")
        # Tombol login memicu fungsi khusus untuk memastikan rerunning
        #st.button("Log in with Google 🌐", on_click=handle_login, type="primary", use_container_width=True)
        st.button("Log in with Google 🌐", on_click=lambda: st.login("google"), type="primary", use_container_width=True
    st.stop()

# --- JIKA LOLOS LOGIN ---
email_aktif = st.user.email.strip().lower()
nama_aktif = st.user.name or "User Pelanggan"

# Inisialisasi Database User
if "db_users" not in st.session_state:
    st.session_state.db_users = {EMAIL_ADMIN: {"status": "Aktif", "nama": "Admin"}}

# Bar Navigasi Profil
col_p, col_n = st.columns([4, 1])
with col_p:
    st.write(f"👤 **{nama_aktif}** | `{email_aktif}`")
with col_n:
    if st.button("Keluar 🚪"):
        st.logout()
        st.rerun()

st.markdown("---")

# ==============================================================================
# 2. LOGIKA API KEY ROTATION
# ==============================================================================
def dapatkan_client():
    if "gemini" in st.secrets and "gcp_api_keys" in st.secrets["gemini"]:
        keys = st.secrets["gemini"]["gcp_api_keys"].strip().split("\n")
        key_aktif = random.choice([k.strip() for k in keys if k.strip()])
        return genai.Client(api_key=key_aktif)
    return None

# ==============================================================================
# 3. WORKSPACE UTAMA (LOGIKA UTAMA)
# ==============================================================================
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