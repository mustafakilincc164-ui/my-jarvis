import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API Ayarları
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Jarvis Ayarları
JARVIS_NAME = os.getenv("JARVIS_NAME", "Jarvis")
JARVIS_VOICE_SPEED = int(os.getenv("JARVIS_VOICE_SPEED", 175))

# Asistan Karakteri / Sistem Talimatı
SYSTEM_INSTRUCTION = (
    f"Sen kullanıcının kişisel yapay zeka asistanı olan {JARVIS_NAME}'sin. "
    "Tony Stark'ın Jarvis'i gibi davran: saygılı, hafif iğneleyici, esprili, son derece zeki, "
    "teknik detaylara hakim ve yardımseversin. Kullanıcıya hitap ederken 'Efendim' kelimesini "
    "kullanabilirsin. Yanıtlarını kısa, net ve anlaşılır tut. Konuşma diliyle yaz (seslendirme için uygun olsun)."
)
