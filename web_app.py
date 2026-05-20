import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="AI Employee Trainer", page_icon="🤖", layout="centered")

# ==========================================
# 2. SETUP API KEY & INISIALISASI GEMINI
# ==========================================
# Mengambil kunci dengan aman dari Streamlit Secrets
try:
    API_KEY = st.secrets["AIzaSyB95IVToE2ZYv6IR8S-ZX17FkCtcJd_GgU"]
    client = genai.Client(api_key=API_KEY)
except KeyError:
    st.error("API Key belum disetting di Streamlit Secrets! Silakan atur di menu Manage App -> Secrets.")
    st.stop()

# ==========================================
# 3. SETUP MEMORI (SESSION STATE)
# ==========================================
# Mengingat nama karyawan dan riwayat chat agar tidak hilang saat refresh
if "nama_tersimpan" not in st.session_state:
    st.session_state.nama_tersimpan = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 4. MEMBACA FILE SOP
# ==========================================
# Pastikan file sop_kafe.txt ada di dalam folder yang sama di GitHub
sop_content = "SOP belum dimuat."
try:
    with open("sop_kafe.txt", "r", encoding="utf-8") as file:
        sop_content = file.read()
except FileNotFoundError:
    st.warning("⚠️ File sop_kafe.txt tidak ditemukan di folder proyek!")

# Instruksi inti untuk membatasi AI agar menjawab HANYA dari SOP
instruksi_sistem = f"""
Kamu adalah AI Employee Trainer yang tegas dan profesional. 
Tugasmu adalah melatih karyawan baru berdasarkan dokumen SOP perusahaan berikut:

{sop_content}

Aturan menjawab:
1. Jawab dengan ramah namun profesional.
2. Selalu rujuk jawabanmu HANYA pada SOP di atas.
3. Jika karyawan bertanya hal di luar SOP, tolak dengan sopan dan katakan itu di luar materi training.
"""

# ==========================================
# 5. HALAMAN LOGIN (JIKA NAMA BELUM DIISI)
# ==========================================
if st.session_state.nama_tersimpan == "":
    st.title("🤖 AI Employee Trainer")
    st.markdown("### 📝 Pendaftaran Training Mandiri")
    
    nama_input = st.text_input("Masukkan Nama Lengkapmu sebelum memulai:", placeholder="Contoh: Andika")
    
    if st.button("Masuk ke Ruang Training 🚀"):
        if nama_input.strip() != "":
            st.session_state.nama_tersimpan = nama_input.strip()
            st.rerun() # Refresh layar untuk masuk ke ruang chat
        else:
            st.warning("Nama tidak boleh kosong, Bro!")

# ==========================================
# 6. RUANG TRAINING (JIKA NAMA SUDAH ADA)
# ==========================================
else:
    nama_karyawan = st.session_state.nama_tersimpan
    
    # --- Header & Tombol Ganti Nama ---
    col_nama, col_logout = st.columns([4, 1])
    with col_nama:
        st.success(f"Selamat belajar,**{nama_karyawan}**! Silahkan tanyakan hal apapun terkait SOP di bawah.")