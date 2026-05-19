import streamlit as st
from google import genai
from google.genai import types
import pypdf
import docx
import pandas as pd
from datetime import datetime
import os

# 1. Masukkan API Key Google Gemini milikmu di sini
API_KEY = "AIzaSyAUNLfZotUB2EgPNFbdzgzGRGnK7qEY9uU"

# Inisialisasi Client
client = genai.Client(api_key=API_KEY)

# Konfigurasi Tampilan Halaman Web
st.set_page_config(page_title="AI Employee Trainer & Dashboard", page_icon="🤖", layout="wide")

# --- FUNGSI DATABASE UTK MENYIMPAN RIWAYAT CHAT & PERFORMA ---
DB_FILE = "database_chat.csv"

def simpan_ke_database(nama, pertanyaan, skor_pemahaman):
    """Menyimpan data pertanyaan dan performa karyawan ke file CSV"""
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_baru = pd.DataFrame([{
        "Waktu": waktu_sekarang,
        "Nama Karyawan": nama,
        "Pertanyaan": pertanyaan,
        "Skor Pemahaman": int(skor_pemahaman)
    }])
    
    if not os.path.isfile(DB_FILE):
        data_baru.to_csv(DB_FILE, index=False)
    else:
        data_baru.to_csv(DB_FILE, mode='a', header=False, index=False)

def ekstrak_teks_dari_pdf(file_pdf):
    pembaca_pdf = pypdf.PdfReader(file_pdf)
    teks = ""
    for halaman in pembaca_pdf.pages:
        teks += halaman.extract_text() + "\n"
    return teks

def ekstrak_teks_dari_docx(file_docx):
    dokumen = docx.Document(file_docx)
    teks = ""
    for paragraf in dokumen.paragraphs:
        teks += paragraf.text + "\n"
    return teks

# --- SIDEBAR NAVIGASI HALAMAN ---
st.sidebar.title("🚀 Menu Sistem AI")
halaman = st.sidebar.radio("Pilih Tampilan Halaman:", ("📱 Chat Training Karyawan", "📊 Dashboard Performa Admin"))

st.sidebar.write("---")
st.sidebar.header("📁 Pengaturan Dokumen SOP")
opsi_sop = st.sidebar.radio("Pilih Metode Input SOP:", ("Gunakan SOP Kafe Default", "Upload File (PDF / Word / TXT)"))

isi_sop = ""
if opsi_sop == "Gunakan SOP Kafe Default":
    try:
        with open("sop_kafe.txt", 'r', encoding='utf-8') as file:
            isi_sop = file.read()
    except FileNotFoundError:
        isi_sop = "SOP default tidak ditemukan."
else:
    file_diunggah = st.sidebar.file_uploader("Unggah file SOP toko di sini:", type=["pdf", "docx", "txt"])
    if file_diunggah is not None:
        if file_diunggah.name.endswith(".pdf"):
            isi_sop = ekstrak_teks_dari_pdf(file_diunggah)
        elif file_diunggah.name.endswith(".docx"):
            isi_sop = ekstrak_teks_dari_docx(file_diunggah)
        elif file_diunggah.name.endswith(".txt"):
            isi_sop = file_diunggah.read().decode("utf-8")

# ==================== HALAMAN 1: CHAT TRAINING KARYAWAN ====================
if halaman == "📱 Chat Training Karyawan":
    st.title("🤖 AI Employee Trainer")
    st.subheader("Ruang Training Mandiri Karyawan Baru")
    st.write("---")
    
    # Input Nama Karyawan di Awal
    nama_karyawan = st.text_input("Masukkan Nama Lengkapmu sebelum memulai:", placeholder="Contoh: Andika")
    
    if nama_karyawan:
        st.success(f"Selamat belajar, **{nama_karyawan}**! Silakan tanyakan hal apa pun terkait SOP toko di kolom bawah.")
        
        # --- POSISI TOMBOL SARAN PERTANYAAN BARU (SELALU MUNCUL SINKRON DENGAN NAMA) ---
        st.write("💡 **Contoh pertanyaan cepat (klik untuk menanyakan):**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Bagaimana cara menyapa pelanggan?", key="btn1"):
                st.session_state.quick_prompt = "Bagaimana cara menyapa pelanggan?"
        with col2:
            if st.button("💬 Bagaimana aturan pembayaran di kafe?", key="btn2"):
                st.session_state.quick_prompt = "Bagaimana aturan pembayaran di kafe?"
        st.write("---")
        
        # Wadah riwayat chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Logika menangani input teks atau tombol cepat
        prompt = st.chat_input("Tanyakan sesuatu tentang SOP perusahaan...")
        if "quick_prompt" in st.session_state:
            prompt = st.session_state.quick_prompt
            del st.session_state.quick_prompt

        # Input Chat Diproses
        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Instruksi ketat untuk AI + Perintah Penilaian Rahasia
            instruksi_sistem = f"""
            Kamu adalah AI Training Manager. Jawab pertanyaan karyawan dengan ramah hanya berdasarkan SOP ini:
            {isi_sop}
            
            ATURAN TAMBAHAN WAJIB:
            Di baris paling terakhir dari jawabanmu, kamu WAJIB menuliskan kode evaluasi rahasia untuk sistem berupa angka tingkat pemahaman karyawan terhadap SOP (skor dari 10 sampai 100). Format penulisan wajib persis seperti ini: [SKOR: angka].
            Contoh: Jika pertanyaannya sangat cerdas dan relevan beri [SKOR: 95]. Jika pertanyaannya konyol/di luar SOP beri [SKOR: 30].
            """

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=instruksi_sistem, temperature=0.3)
                )
                
                jawaban_mentah = response.text
                
                # Memisahkan jawaban teks dengan skor rahasia agar tidak terlihat oleh karyawan
                skor_terdeteksi = 70 
                if "[SKOR:" in jawaban_mentah:
                    bagian = jawaban_mentah.split("[SKOR:")
                    jawaban_bersih = bagian[0].strip()
                    skor_terdeteksi = bagian[1].replace("]", "").strip()
                else:
                    jawaban_bersih = jawaban_mentah
                
                message_placeholder.markdown(jawaban_bersih)
                
            st.session_state.messages.append({"role": "assistant", "content": jawaban_bersih})
            
            # SIMPAN DATA KE DATABASE CSV
            simpan_ke_database(nama_karyawan, prompt, skor_terdeteksi)
            st.rerun()
    else:
        st.warning("Silakan isi nama kamu terlebih dahulu di kolom atas untuk membuka akses chat AI!")

# ==================== HALAMAN 2: DASHBOARD PERFORMA ADMIN ====================
elif halaman == "📊 Dashboard Performa Admin":
    st.title("🔒 Verifikasi Akses Admin")
    st.subheader("Halaman ini dilindungi. Silakan masukkan kata sandi Anda.")
    st.write("---")
    
    # 1. Kolom Input Password Rahasia
    # Ganti "kopiMaju2026" dengan password apa saja yang diinginkan oleh pemilik toko
    password_input = st.text_input("Masukkan Password Admin:", type="password")
    
    if password_input == "kopiMaju2026":
        st.success("🔓 Akses Diberikan! Selamat Datang, Manajer.")
        st.write("---")
        
        # --- SEMUA KODE DASHBOARD KAMU MASUK KE DALAM SINI ---
        if os.path.isfile(DB_FILE):
            df = pd.read_csv(DB_FILE)
            
            # Statistik Utama
            total_pertanyaan = len(df)
            rata_skor = round(df["Skor Pemahaman"].mean(), 1)
            karyawan_aktif = df["Nama Karyawan"].nunique()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Pertanyaan Masuk", value=total_pertanyaan)
            with col2:
                st.metric(label="Rata-rata Skor Pemahaman Karyawan", value=f"{rata_skor} / 100")
            with col3:
                st.metric(label="Jumlah Karyawan Terdaftar", value=karyawan_aktif)
                
            st.write("---")
            
            # Tabel 1: Performa Karyawan
            st.subheader("📈 Ranking Performa Pemahaman Karyawan")
            df_performa = df.groupby("Nama Karyawan").agg(
                Rata_Rata_Skor=("Skor Pemahaman", "mean"),
                Jumlah_Pertanyaan=("Pertanyaan", "count")
            ).reset_index()
            df_performa["Rata_Rata_Skor"] = df_performa["Rata_Rata_Skor"].round(1)
            st.dataframe(df_performa.sort_values(by="Rata_Rata_Skor", ascending=False), use_container_width=True)
            
            # Tabel 2: Log Pertanyaan Real-time
            st.subheader("📋 Log Pertanyaan Karyawan (Real-time)")
            st.dataframe(df.sort_values(by="Waktu", ascending=False), use_container_width=True)
            
        else:
            st.info("Belum ada data pertanyaan yang masuk.")
            
    elif password_input != "":
        # Jika salah ketik password
        st.error("❌ Password Salah! Akses Ditolak.")