import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. KONFIGURASI UTAMA WEBSITE
# ==========================================
st.set_page_config(page_title="AI Employee Trainer", page_icon="🤖", layout="centered")

# ==========================================
# 2. KEAMANAN API KEY (STREAMLIT SECRETS)
# ==========================================
try:
    # Membaca brankas rahasia TOML Streamlit Cloud
    API_KEY = st.secrets["AIzaSyB95IVToE2ZYv6IR8S-ZX17FkCtcJd_GgU"]
    client = genai.Client(api_key=API_KEY)
except KeyError:
    st.error("⚠️ API Key belum disetting dengan benar di Streamlit Secrets! Pastikan di menu Secrets sudah tertulis format TOML: GEMINI_API_KEY = 'KUNCI_API_KAMU'")
    st.stop()

# ==========================================
# 3. PENGATURAN MEMORI (SESSION STATE)
# ==========================================
# Menjaga nama dan riwayat chat agar tidak hilang saat halaman refresh
if "nama_tersimpan" not in st.session_state:
    st.session_state.nama_tersimpan = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 4. MEMBACA FILE PANDUAN (SOP KAFE)
# ==========================================
sop_content = "SOP belum dimuat."
try:
    with open("sop_kafe.txt", "r", encoding="utf-8") as file:
        sop_content = file.read()
except FileNotFoundError:
    st.warning("⚠️ File 'sop_kafe.txt' tidak ditemukan di folder GitHub-mu! Pastikan filenya sudah di-upload.")

# Sistem instruksi ketat agar Gemini hanya menjawab berdasarkan buku SOP
instruksi_sistem = f"""
Kamu adalah AI Employee Trainer yang tegas, pintar, dan profesional. 
Tugasmu adalah melatih dan menjawab pertanyaan karyawan baru berdasarkan dokumen SOP perusahaan berikut:

{sop_content}

Aturan Menjawab (WAJIB DIPATUHI):
1. Jawab dengan bahasa Indonesia yang ramah, jelas, namun tetap profesional.
2. Selalu gunakan rujukan informasi HANYA dari dokumen SOP di atas.
3. Jika karyawan bertanya hal di luar materi SOP, tolak dengan sangat sopan dan katakan bahwa hal tersebut di luar materi training karyawan.
"""

# ==========================================
# 5. HALAMAN LOGIN (JIKA NAMA MASIH KOSONG)
# ==========================================
if st.session_state.nama_tersimpan == "":
    st.title("🤖 AI Employee Trainer")
    st.subheader("Ruang Training Mandiri Karyawan Baru")
    st.markdown("---")
    
    nama_input = st.text_input("Masukkan Nama Lengkapmu sebelum memulai:", placeholder="Contoh: Epul")
    
    if st.button("Masuk ke Ruang Training 🚀", use_container_width=True):
        if nama_input.strip() != "":
            st.session_state.nama_tersimpan = nama_input.strip()
            st.rerun() # Refresh instan untuk membuka ruang chat
        else:
            st.warning("Nama tidak boleh kosong, Bro! Ketik namamu dulu ya.")

# ==========================================
# 6. RUANG CHAT TRAINING (JIKA NAMA SUDAH ADA)
# ==========================================
else:
    nama_karyawan = st.session_state.nama_tersimpan
    
    # --- Header Tampilan & Tombol Ganti Nama ---
    col_nama, col_logout = st.columns([4, 1])
    with col_nama:
        st.success(f"Selamat belajar, **{nama_karyawan}**! Silakan tanyakan hal apa pun terkait SOP toko di kolom bawah.")
    with col_logout:
        if st.button("🚪 Ganti Nama", use_container_width=True):
            st.session_state.nama_tersimpan = ""
            st.session_state.messages = [] # Reset chat lama agar bersih kembali
            st.rerun()
            
    st.markdown("---")
            
    # --- Fitur Tombol Pertanyaan Cepat ---
    st.write("💡 **Contoh pertanyaan cepat (klik untuk menanyakan):**")
    col1, col2 = st.columns(2)
    
    pertanyaan_cepat = None 
    
    with col1:
        if st.button("💬 Bagaimana cara menyapa pelanggan?", use_container_width=True):
            pertanyaan_cepat = "Bagaimana cara menyapa pelanggan?"
    with col2:
        if st.button("💬 Bagaimana aturan pembayaran di kafe?", use_container_width=True):
            pertanyaan_cepat = "Bagaimana aturan pembayaran di kafe?"

    st.markdown(" ")

    # --- Menampilkan Riwayat Obrolan ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Kotak Input Ketik Chat Biasa ---
    prompt = st.chat_input("Tanyakan sesuatu tentang SOP perusahaan...")

    # --- Logika Pemroses Pesan (Dari Tombol / Ketikan) ---
    input_user = pertanyaan_cepat if pertanyaan_cepat else prompt

    if input_user:
        # 1. Amankan & tampilkan chat dari user ke layar
        st.session_state.messages.append({"role": "user", "content": input_user})
        with st.chat_message("user"):
            st.markdown(input_user)

        # 2. Panggil AI Gemini dengan efek loading spinner yang interaktif
        with st.chat_message("model"):
            with st.spinner("Membaca buku panduan SOP..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=input_user,
                        config=types.GenerateContentConfig(
                            system_instruction=instruksi_sistem,
                            temperature=0.2 # Kunci temperature rendah agar AI patuh pada teks SOP
                        )
                    )
                    jawaban = response.text
                    
                    # Tampilkan jawaban AI dan simpan ke memori chat
                    st.markdown(jawaban)
                    st.session_state.messages.append({"role": "model", "content": jawaban})
                    
                except Exception as e:
                    st.error(f"Terjadi masalah teknis pada server AI: {e}")