import os
from flask import Flask, request, jsonify
from core.brain import JarvisBrain

app = Flask(__name__)

# Jarvis Beynini yükle
try:
    brain = JarvisBrain()
    print("[Sistem] Jarvis Yapay Zeka Beyni başarıyla yüklendi!")
except Exception as e:
    print(f"[HATA] Beyin yüklenirken hata oluştu: {e}")
    brain = None

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
    return jsonify(result)

if __name__ == "__main__":
    # Render, Koyeb veya Hugging Face Spaces PORT ortam değişkenini kullanır
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
