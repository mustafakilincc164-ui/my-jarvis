import os
import time
import random
import glob
import asyncio
import edge_tts
from flask import Flask, request, jsonify
from core.brain import JarvisBrain

app = Flask(__name__)

# static/voices klasörünü oluştur
VOICES_DIR = os.path.join(app.root_path, "static", "voices")
os.makedirs(VOICES_DIR, exist_ok=True)

# Jarvis Beynini yükle
try:
    brain = JarvisBrain()
    print("[Sistem] Jarvis Yapay Zeka Beyni başarıyla yüklendi!")
except Exception as e:
    print(f"[HATA] Beyin yüklenirken hata oluştu: {e}")
    brain = None

def detect_language(text: str) -> str:
    # Türkçe'ye özgü karakterler ve sık kullanılan kelimeler
    turkish_chars = set("ıışğğççoöuüİŞĞÇÖÜ")
    turkish_words = {"ve", "bir", "bu", "ne", "da", "de", "için", "efendim", "saat", "sistem", "açılıyor", "merhaba", "tamam", "girdiniz"}
    text_lower = text.lower()
    
    if any(char in turkish_chars for char in text) or any(word in text_lower.split() for word in turkish_words):
        return "tr"
    return "en"

def clean_old_voices():
    """Disk alanını korumak için 5 dakikadan eski ses dosyalarını siler."""
    try:
        now = time.time()
        cutoff = now - 300 # 5 dakika (300 saniye)
        for f in glob.glob(os.path.join(VOICES_DIR, "voice_*.mp3")):
            if os.path.getmtime(f) < cutoff:
                try:
                    os.remove(f)
                except Exception:
                    pass
    except Exception as e:
        print(f"[UYARI] Eski ses dosyaları temizlenirken hata: {e}")

def generate_tts_sync(text: str, filename: str) -> str:
    lang = detect_language(text)
    
    if lang == "tr":
        # Türkçe Ahmet (Kullanıcı seçimi: Robotik Hızlı -> pitch="+0Hz", rate="+15%")
        voice = "tr-TR-AhmetNeural"
        pitch = "+0Hz"
        rate = "+15%"
    else:
        # İngilizce Ryan (Kullanıcı seçimi: Orijinal Ryan -> pitch="+0Hz", rate="+0%")
        voice = "en-GB-RyanNeural"
        pitch = "+0Hz"
        rate = "+0%"
        
    filepath = os.path.join(VOICES_DIR, filename)
    
    async def _generate():
        communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
        await communicate.save(filepath)
        
    # Asenkron fonksiyonu senkron olarak çalıştır
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_generate())
    finally:
        loop.close()
        
    return filename

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Jarvis Yapay Zeka Bulut Sunucusu Aktif!"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    if not brain:
        return jsonify({
            "response": "Sistem hatası: Yapay zeka beyni yüklenemedi.",
            "action": "none"
        }), 500
        
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({
            "response": "Boş mesaj gönderdiniz efendim.",
            "action": "none"
        }), 400
        
    # Yapay zekadan yanıt al
    result = brain.get_response_structured(user_message)
    response_text = result.get("response", "")
    
    # Yapay zeka sesini sunucu tarafında oluştur
    if response_text:
        # Eski dosyaları temizle
        clean_old_voices()
        
        # Benzersiz dosya adı oluştur
        filename = f"voice_{int(time.time())}_{random.randint(1000, 9999)}.mp3"
        try:
            generate_tts_sync(response_text, filename)
            # İstek atılan host URL'ye göre dinamik audio_url oluştur
            base_url = request.host_url.rstrip('/')
            result["audio_url"] = f"{base_url}/static/voices/{filename}"
        except Exception as tts_err:
            print(f"[HATA] TTS üretilemedi: {tts_err}")
            result["audio_url"] = ""
            
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
