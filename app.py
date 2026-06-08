import streamlit as st
from google import genai
import random
import time

# --- INITIALIZATION ---
if "blacklist" not in st.session_state:
    st.session_state.blacklist = {} # Menyimpan key/model yang sedang limit

def adalah_tersedia(key, model):
    """Mengecek apakah kombinasi ini masih dalam masa cooldown"""
    key_id = f"{key[:5]}_{model}" # Unik ID untuk key+model
    if key_id in st.session_state.blacklist:
        waktu_cooldown = st.session_state.blacklist[key_id]
        if time.time() < waktu_cooldown:
            return False # Masih limit
        else:
            del st.session_state.blacklist[key_id] # Cooldown habis
    return True

def jalankan_ai_pintar(tugas, profesi):
    keys = [k.strip() for k in st.secrets["gemini"]["gcp_api_keys"].split("\n") if k.strip()]
    models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    random.shuffle(keys)
    
    for key in keys:
        for model in models:
            if not adalah_tersedia(key, model):
                continue # Lewati jika masih limit
            
            try:
                client = genai.Client(api_key=key)
                res = client.models.generate_content(
                    model=model,
                    contents=tugas,
                    config={"system_instruction": f"Anda adalah pakar {profesi}"}
                )
                return res.text, model
            except Exception as e:
                if "429" in str(e):
                    # Masukkan ke blacklist selama 60 detik
                    key_id = f"{key[:5]}_{model}"
                    st.session_state.blacklist[key_id] = time.time() + 60
                    continue # Coba kombinasi berikutnya
                else:
                    st.error(f"Error fatal: {e}")
                    return None, None
    return None, None

# --- UI ---
if st.button("Eksekusi Pintar ⚡"):
    hasil, model_dipakai = jalankan_ai_pintar(tugas, profesi)
    if hasil:
        st.success(f"Berhasil dengan {model_dipakai}")
        st.markdown(hasil)
    else:
        st.error("Semua model/key sedang limit. Tunggu 1 menit agar blacklist ter-reset.")