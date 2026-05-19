import os
from google import genai
from google.genai import types

# 1. Masukkan API Key Google Gemini yang kamu salin tadi di sini
API_KEY = "MASUKKAN_API_KEY_GEMINI_KAMU_DI_SINI"

# Inisialisasi Google GenAI Client
client = genai.Client(api_key=API_KEY)

def baca_sop(nama_file):
    """Fungsi untuk membaca isi dokumen SOP file teks"""
    with open(nama_file, 'r', encoding='utf-8') as file:
        return file.read()

def tanya_ai_trainer():
    # Membaca file SOP yang sudah kita buat
    isi_sop = baca_sop("sop_kafe.txt")
    
    # SYSTEM PROMPT: Instruksi ketat agar AI bertindak sebagai Trainer
    # Kamu bisa mengubah instruksi bahasa Mandarin di sini nanti!
    instruksi_sistem = f"""
    Kamu adalah AI Training Manager untuk karyawan baru. 
    Tugasmu adalah menjawab pertanyaan karyawan dengan ramah, jelas, dan tegas hanya berdasarkan Dokumen SOP di bawah ini.
    
    DOKUMEN SOP PERUSAHAAN:
    {isi_sop}
    
    ATURAN KETAT:
    1. Jika pertanyaan karyawanTIDAK ADA di dalam Dokumen SOP, jawab dengan: "Maaf, hal tersebut tidak diatur dalam SOP resmi perusahaan."
    2. Jawablah menggunakan bahasa Indonesia yang profesional.
    """
    
    print("=== AI TRAINING KARYAWAN READY ===")
    print("Ketik 'keluar' untuk menyudahi sesi training.\n")
    
    while True:
        # Mengambil input pertanyaan dari karyawan baru lewat terminal
        pertanyaan = input("Pertanyaan Karyawan: ")
        
        if pertanyaan.lower() == 'keluar':
            print("Sesi training selesai. Semangat bekerja!")
            break
            
        # Mengirim instruksi dan pertanyaan ke model Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=pertanyaan,
            config=types.GenerateContentConfig(
                system_instruction=instruksi_sistem,
                temperature=0.3 # Suhu rendah agar AI konsisten dan tidak mengarang bebas
            )
        )
        
        print(f"Jawaban AI Manager: {response.text}\n")

# Menjalankan program utama
if __name__ == "__main__":
    tanya_ai_trainer()