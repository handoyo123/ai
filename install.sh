#!/bin/bash

# ====================================================================
# PRE-FLIGHT CHECK: MEMASTIKAN PYTHON TERINSTAL DENGAN BENAR
# ====================================================================
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    VERSION=$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null)
    if [ "$VERSION" = "3" ]; then
        PYTHON_CMD="python"
    else
        echo "🚨 Error: Aplikasi ini membutuhkan Python 3. Versi Python Anda saat ini adalah Python 2."
        exit 1
    fi
else
    echo "🚨 Error: Python tidak ditemukan di sistem ini. Silakan instal Python 3 terlebih dahulu."
    exit 1
fi

clear
echo "===================================================="
echo "  1. MEMULAI INSTALASI & UPDATE LIBRARY PREMIUM...  "
echo "===================================================="
echo "[*] Menggunakan perintah: $PYTHON_CMD"

# Memastikan pip menggunakan versi terbaru
$PYTHON_CMD -m pip install --upgrade pip

# Menginstal semua dependensi utama (Streamlit versi terbaru otomatis mendukung st.kv)
$PYTHON_CMD -m pip install --upgrade streamlit google-genai python-docx streamlit-google-auth streamlit-oauth

# Pengecekan otomatis untuk file api_keys.txt agar sistem tidak error
if [ ! -f "api_keys.txt" ]; then
    echo ""
    echo "===================================================="
    echo "  [INFO] Membuat file pool api_keys.txt otomatis... "
    echo "===================================================="
    echo "# Masukkan API Key Gemini Anda di bawah ini (1 key per baris)" > api_keys.txt
    echo "# Hapus baris contoh di bawah jika sudah ada key asli" >> api_keys.txt
    echo "AIzaSyYourFirstKeyDisini" >> api_keys.txt
fi

# ====================================================================
# BAGIAN YANG DILENGKAPI: INISIALISASI DATABASE LOKAL (MODE HYBRID)
# ====================================================================
if [ ! -f "database_users.json" ]; then
    echo ""
    echo "===================================================="
    echo "  [INFO] Inisialisasi Database Cadangan Lokal...    "
    echo "===================================================="
    echo "{\"handoyoyy1@gmail.com\": {\"nama\": \"Miftada Handoyo (Admin)\", \"status\": \"Aktif\", \"nominal_transfer\": 0, \"kode_aktivasi\": \"ADMIN_ACCESS\"}}" > database_users.json
    echo "[*] Berkas 'database_users.json' berhasil dibuat dengan hak akses Admin."
fi

echo ""
echo "===================================================="
echo "  2. INSTALASI SELESAI! MENJALANKAN APLIKASI...      "
echo "===================================================="
echo "Sistem mendeteksi mode: Hybrid Engine Aktif (Local JSON & Cloud KV Ready)."
echo "Aplikasi akan terbuka otomatis di browser Anda."
echo "Jangan tutup jendela terminal ini selama aplikasi berjalan."
echo "----------------------------------------------------"

# Menjalankan aplikasi dengan database internal st.kv / Local Fallback
$PYTHON_CMD -m streamlit run app.py