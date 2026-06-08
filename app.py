import streamlit as st
from google import genai
from google.genai import types
from docx import Document
import random
import os
import io
import json
import warnings

# Menyembunyikan peringatan dari library pendukung
warnings.filterwarnings("ignore")

# Pengaturan Konfigurasi Halaman Utama Streamlit
st.set_page_config(page_title="Universal AI Agent Pro", page_icon="🔮", layout="centered")

# ==============================================================================
# 1. DATABASE CONFIG & AUTOMATIC AUTH CHECK
# ==============================================================================
EMAIL_ADMIN = "handoyoyy1@gmail.com"
NAMA_FILE_KEY = "api_keys.txt"
NAMA_FILE_DB = "database_users.json"  

def muat_database_kv():
    if hasattr(st, "kv"):
        if "db_users_master" not in st.kv:
            data_awal = {
                EMAIL_ADMIN: {
                    "nama": "Miftada Handoyo (Admin)",
                    "status": "Aktif", 
                    "nominal_transfer": 0, 
                    "kode_aktivasi": "ADMIN_ACCESS"
                }
            }
            st.kv["db_users_master"] = json.dumps(data_awal)
            return data_awal
        try:
            return json.loads(st.kv["db_users_master"])
        except:
            return {EMAIL_ADMIN: {"nama": "Miftada Handoyo (Admin)", "status": "Aktif", "nominal_transfer": 0, "kode_aktivasi": "ADMIN_ACCESS"}}
    else:
        if not os.path.exists(NAMA_FILE_DB):
            data_awal = {
                EMAIL_ADMIN: {
                    "nama": "Miftada Handoyo (Admin)",
                    "status": "Aktif", 
                    "nominal_transfer": 0, 
                    "kode_aktivasi": "ADMIN_ACCESS"
                }
            }
            with open(NAMA_FILE_DB, "w") as f:
                json.dump(data_awal, f, indent=4)
            return data_awal
        try:
            with open(NAMA_FILE_DB, "r") as f:
                return json.load(f)
        except:
            return {EMAIL_ADMIN: {"nama": "Miftada Handoyo (Admin)", "status": "Aktif", "nominal_transfer": 0, "kode_aktivasi": "ADMIN_ACCESS"}}

def simpan_database_kv(data_db):
    if hasattr(st, "kv"):
        st.kv["db_users_master"] = json.dumps(data_db)
    else:
        with open(NAMA_FILE_DB, "w") as f:
            json.dump(data_db, f, indent=4)

# --- PROTEKSI UTAMA GOOGLE OAUTH BROWSER ---
# Jika user belum login, tampilkan layar kunci halaman (Lock Screen)
if not st.user.is_logged_in:
    st.write("")
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>🔮 Universal AI Agent Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Aplikasi Terlindungi Sistem Google OAuth Resmi</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.warning("🔒 Anda wajib masuk menggunakan akun Google untuk memverifikasi hak akses aplikasi.")
        st.write("Silakan klik tombol login resmi di bawah untuk mendeteksi profil email browser Anda.")
        
        # Menggunakan event handler on_click agar pemanggilan login stabil dan aman
        st.button("Log in with Google 🌐", on_click=st.login, type="primary", use_container_width=True)
    st.stop()

# JIKA USER BERHASIL LOGIN, BACA IDENTITAS GOOGLE
email_aktif = st.user.email.strip().lower()
nama_aktif = st.user.name if st.user.name else "User Pelanggan"

# Sinkronisasi otomatis ke database internal aplikasi
st.session_state.db_users = muat_database_kv()
if email_aktif not in st.session_state.db_users:
    db_sekarang = muat_database_kv()
    nominal_acak = 49000 + random.randint(1, 999)
    db_sekarang[email_aktif] = {
        "nama": nama_aktif, 
        "status": "Pending Pembayaran",
        "nominal_transfer": nominal_acak, 
        "kode_aktivasi": f"PREM-{random.randint(100000, 999999)}"
    }
    simpan_database_kv(db_sekarang)
    st.session_state.db_users = db_sekarang

status_user = st.session_state.db_users[email_aktif]["status"]

# Bar Informasi Profil User Terdeteksi di Atas Workspace
col_profil, col_nav_out = st.columns([4, 1])
with col_profil:
    st.write(f"🌐 Terotentikasi Google: **{nama_aktif}** (`{email_aktif}`) | Status: **{status_user}**")
with col_nav_out:
    if st.button("Keluar 🚪", use_container_width=True):
        st.logout()
        st.rerun()

st.markdown("---")

# ==============================================================================
# 2. LOGIKA ROTASI POOL API KEY & PARSER DOKUMEN
# ==============================================================================
def muat_api_keys():
    keys = []
    
    # Membaca dari struktur flat TOML [gemini][gcp_api_keys]
    if "gemini" in st.secrets and "gcp_api_keys" in st.secrets["gemini"]:
        keys_env = st.secrets["gemini"]["gcp_api_keys"]
        for baris in keys_env.strip().split("\n"):
            baris_bersih = baris.strip().replace('"', '').replace(',', '').replace('[', '').replace(']', '')
            if baris_bersih and not baris_bersih.startswith("#"):
                keys.append(baris_bersih)
        if keys:
            return keys

    # Fallback jika ada cadangan data di file txt lokal
    if os.path.exists(NAMA_FILE_KEY):
        with open(NAMA_FILE_KEY, "r") as f:
            for baris in f:
                baris = baris.strip()
                if baris and not baris.startswith("#"):
                    keys.append(baris)
    return keys

def dapatkan_client_acak():
    daftar_keys = muat_api_keys()
    keys_valid = [k for k in daftar_keys if "Your" not in k and "Disini" not in k]
    if not keys_valid: return None
    return genai.Client(api_key=random.choice(keys_valid))

def ekstraks_dokumen_murni(teks_lengkap):
    tag_mulai = "===Mulai Dokumen==="
    tag_akhir = "===Akhir Dokumen==="
    
    if tag_mulai in teks_lengkap and tag_akhir in teks_lengkap:
        return teks_lengkap.split(tag_mulai)[1].split(tag_akhir)[0].strip()
    elif tag_mulai in teks_lengkap:
        return teks_lengkap.split(tag_mulai)[1].strip()
        
    baris_teks = teks_lengkap.split('\n')
    baris_bersih = []
    mulai_rekam = False
    
    for b in baris_teks:
        if b.strip().startswith("#") or b.strip().startswith("**Bab") or b.strip().startswith("**Kuis") or b.strip().startswith("**Materi"):
            mulai_rekam = True
        if "Rekomendasi dan Tindak Lanjut" in b or "Sebagai seorang pakar" in b:
            continue
        if mulai_rekam:
            baris_bersih.append(b)
            
    if baris_bersih:
        return "\n".join(baris_bersih).strip()
    return teks_lengkap.strip()

def buat_file_docx(teks_markdown):
    doc = Document()
    for baris in teks_markdown.split('\n'):
        baris = baris.replace("===Mulai Dokumen===", "").replace("===Akhir Dokumen===", "")
        if baris.startswith('### '): doc.add_heading(baris.replace('### ', ''), level=3)
        elif baris.startswith('## '): doc.add_heading(baris.replace('## ', ''), level=2)
        elif baris.startswith('# '): doc.add_heading(baris.replace('# ', ''), level=1)
        elif baris.strip().startswith('- ') or baris.strip().startswith('* '):
            doc.add_paragraph(baris.strip()[2:], style='List Bullet')
        else:
            if baris.strip(): doc.add_paragraph(baris)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==============================================================================
# 3. LOCK SCREEN LAYER PEMBAYARAN (OTOMATIS DILEWATI OLEH AKUN ADMIN)
# ==============================================================================
if status_user == "Pending Pembayaran" and email_aktif != EMAIL_ADMIN:
    st.title("🔒 Akses Layanan Premium Terkunci")
    nominal_bayar = st.session_state.db_users[email_aktif]["nominal_transfer"]
    with st.container(border=True):
        st.markdown("### 💳 Prosedur Aktivasi Premium")
        st.subheader(f"Rp {nominal_bayar:,}")
        col_rek, col_gambar_qris = st.columns([1, 1])
        with col_rek:
            st.markdown("**Tujuan Pembayaran:**\n* **E-Wallet (Gopay):** `081333260292`\n* **Atas Nama:** Miftada Handoyo Y.")
            if st.button("🔄 Cek Status Aktivasi Saya", use_container_width=True):
                st.session_state.db_users = muat_database_kv()
                st.rerun()
        with col_gambar_qris:
            if os.path.exists("qris.jpeg"): st.image("qris.jpeg", use_container_width=True)
    st.stop()

# ==============================================================================
# 4. DASHBOARD UTAMA WORKSPACE & KONTROL HAK AKSES ROLE
# ==============================================================================
if email_aktif == EMAIL_ADMIN:
    tab_workspace, tab_settings, tab_admin = st.tabs(["🚀 Ruang Kerja Agent", "⚙️ Konfigurasi API", "👑 Dashboard Admin"])
    
    with tab_workspace:
        st.write("")
        with st.container(border=True):
            st.markdown("### ✨ Spesifikasi Kebutuhan Kerja (Mode Admin)")
            profesi_user = st.text_input("Tentukan Peran Ahli / Profesi Spesialis Terfokus:", placeholder="Contoh: Senior Database Administrator", key="profesi_adm")
            tugas_user = st.text_area("Deskripsikan Masalah Teknis atau Tugas yang Harus Diselesaikan:", placeholder="Salin perintah pengerjaan berkas di sini...", height=150, key="tugas_adm")
            
        st.write("")
        tombol_proses = st.button("Jalankan Mesin Otomasi Agen ⚡", type="primary", use_container_width=True, key="btn_adm")

        if "hasil_ai" not in st.session_state: st.session_state.hasil_ai = ""

        if tombol_proses:
            if profesi_user.strip() != "" and tugas_user.strip() != "":
                client = dapatkan_client_acak()
                if client is not None:
                    with st.spinner(f"Mesin Otomasi sedang memproses solusi sebagai {profesi_user}..."):
                        try:
                            instruksi_kepribadian = (
                                f"Anda adalah seorang pakar top dunia dan profesional senior di bidang: '{profesi_user}'. "
                                f"Jawablah tugas dari user dengan kualitas industri tertinggi. "
                                f"Bungkus dokumen inti buatan Anda dengan menggunakan penanda teks eksak berikut:\n"
                                f"===Mulai Dokumen===\n[Isi dokumen/materi utama Anda di sini]\n===Akhir Dokumen===\n"
                            )
                            respons_final = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=tugas_user,
                                config=types.GenerateContentConfig(system_instruction=instruksi_kepribadian, temperature=0.0),
                            )
                            st.session_state.hasil_ai = respons_final.text
                            st.balloons()
                        except Exception as e:
                            st.error(f"Terjadi interupsi jaringan API: {e}")
            else:
                st.warning("Kolom Isian Peran Ahli dan Detail Masalah wajib diisi.")

        if st.session_state.hasil_ai != "":
            st.write("")
            st.markdown(f"### 📋 Dokumentasi Pratinjau Sistem: *{profesi_user}*")
            with st.container(border=True): st.markdown(st.session_state.hasil_ai)
            dokumen_murni_unduhan = ekstraks_dokumen_murni(st.session_state.hasil_ai)
            st.write("")
            with st.expander("💾 Opsi Penyimpanan Berkas Bersih", expanded=True):
                col_word, col_txt = st.columns(2)
                with col_word:
                    st.download_button(label="📝 Unduh Dokumen Word (.docx) Bersih", data=buat_file_docx(dokumen_murni_unduhan), file_name=f"Clean_{profesi_user.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, key="dl_word_adm")
                with col_txt:
                    st.download_button(label="📄 Unduh Teks Mentah (.txt) Bersih", data=dokumen_murni_unduhan, file_name=f"Clean_{profesi_user.replace(' ', '_')}.txt", mime="text/plain", use_container_width=True, key="dl_txt_adm")

    with tab_settings:
        st.write("")
        st.markdown("### ⚙️ Keseimbangan Token Pool")
        keys_aktif = [k for k in muat_api_keys() if "Your" not in k and "Disini" not in k]
        st.metric(label="Jumlah Kunci Cadangan API Aktif", value=len(keys_aktif))

    with tab_admin:
        st.write("")
        st.markdown("### 👑 Panel Manajemen Aktivasi Manual")
        if st.button("🔄 Refresh Data Pengajuan Masuk", use_container_width=True, key="ref_adm_btn"):
            st.session_state.db_users = muat_database_kv()
            st.rerun()
            
        db_sekarang = muat_database_kv()
        ada_user = False
        for user_mail, data in list(db_sekarang.items()):
            if user_mail == EMAIL_ADMIN: continue
            ada_user = True
            with st.container(border=True):
                col_data_user, col_tombol_konfirmasi = st.columns([3, 1])
                with col_data_user:
                    st.markdown(f"👤 **Nama:** {data.get('nama', 'User Baru')} | `{user_mail}`")
                    st.write(f"💰 Tagihan: **Rp {data['nominal_transfer']:,}** | Status: `{data['status']}`")
                with col_tombol_konfirmasi:
                    if data['status'] == "Pending Pembayaran":
                        if st.button("Confirm 🟩", key=f"adm_act_{user_mail}", use_container_width=True):
                            db_sekarang = muat_database_kv()
                            db_sekarang[user_mail]["status"] = "Aktif"
                            simpan_database_kv(db_sekarang)
                            st.session_state.db_users = db_sekarang
                            st.rerun()
                    else:
                        st.button("Aktif ✅", key=f"adm_done_{user_mail}", disabled=True, use_container_width=True)
                        
        if not ada_user:
            st.info("Belum ada data pelanggan terdaftar.")
            
        st.write("")
        st.markdown("---")
        st.markdown("### 🔍 Inspektur Data Mentah (Mode Dev/Admin)")
        if st.button("Lihat Seluruh Isi DB Murni 📂", use_container_width=True, key="insp_db_btn"):
            st.json(muat_database_kv())

else:
    st.write("")
    with st.container(border=True):
        st.markdown("### ✨ Spesifikasi Kebutuhan Kerja")
        profesi_user = st.text_input("Tentukan Peran Ahli / Profesi Spesialis Terfokus:", placeholder="Contoh: Kepala Sekolah, Guru Matematika SD, Konten Kreator TikTok", key="profesi_usr")
        tugas_user = st.text_area("Deskripsikan Masalah Teknis atau Tugas yang Harus Diselesaikan:", placeholder="Salin perintah pengerjaan berkas di sini...", height=150, key="tugas_usr")
        
    st.write("")
    tombol_proses = st.button("Jalankan Mesin Otomasi Agen ⚡", type="primary", use_container_width=True, key="btn_usr")

    if "hasil_ai_user" not in st.session_state: st.session_state.hasil_ai_user = ""

    if tombol_proses:
        if profesi_user.strip() != "" and tugas_user.strip() != "":
            client = dapatkan_client_acak()
            if client is not None:
                with st.spinner(f"Mesin Otomasi sedang memproses solusi..."):
                    try:
                        instruksi_kepribadian = (
                            f"Anda adalah seorang pakar top dunia dan profesional senior di bidang: '{profesi_user}'. "
                            f"Jawablah tugas dari user dengan kualitas industri tertinggi. "
                            f"Bungkus dokumen inti buatan Anda dengan menggunakan penanda teks eksak berikut:\n"
                            f"===Mulai Dokumen===\n[Isi dokumen/materi utama Anda di sini]\n===Akhir Dokumen===\n"
                        )
                        respons_final = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=tugas_user,
                            config=types.GenerateContentConfig(system_instruction=instruksi_kepribadian, temperature=0.0),
                        )
                        st.session_state.hasil_ai_user = respons_final.text
                        st.balloons()
                    except Exception as e:
                        st.error(f"Terjadi interupsi jaringan API: {e}")
        else:
            st.warning("Kolom Isian Peran Ahli dan Detail Masalah wajib diisi.")

    if st.session_state.hasil_ai_user != "":
        st.write("")
        st.markdown(f"### 📋 Dokumentasi Pratinjau Sistem: *{profesi_user}*")
        with st.container(border=True): st.markdown(st.session_state.hasil_ai_user)
        dokumen_murni_unduhan = ekstraks_dokumen_murni(st.session_state.hasil_ai_user)
        st.write("")
        with st.expander("💾 Opsi Penyimpanan Berkas Bersih", expanded=True):
            col_word, col_txt = st.columns(2)
            with col_word:
                st.download_button(label="📝 Unduh Dokumen Word (.docx) Bersih", data=buat_file_docx(dokumen_murni_unduhan), file_name=f"Clean_{profesi_user.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, key="dl_word_usr")
            with col_txt:
                st.download_button(label="📄 Unduh Teks Mentah (.txt) Bersih", data=dokumen_murni_unduhan, file_name=f"Clean_{profesi_user.replace(' ', '_')}.txt", mime="text/plain", use_container_width=True, key="dl_txt_usr")

st.write("")
st.markdown("---")
st.caption("© 2026 Universal AI Agent - Commercial Framework Pro Edition")