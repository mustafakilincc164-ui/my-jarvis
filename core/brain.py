import os
import json
import random
import torch
import google.generativeai as genai

from config import settings
from core.nlp import tokenize, stem, bag_of_words, turkish_lower
from core.model import NeuralNet
from core.tools import get_system_status, get_time_and_date, open_website, run_application

class JarvisBrain:
    def __init__(self):
        # 1. Yerel PyTorch modelini yükle
        self.model_path = "model.pth"
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"'{self.model_path}' bulunamadı! Lütfen önce 'train.py' betiğini çalıştırarak modeli eğitin."
            )
            
        # Cihaz belirle (CPU)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model verilerini yükle
        self.data = torch.load(self.model_path, map_location=self.device)
        self.input_size = self.data["input_size"]
        self.hidden_size = self.data["hidden_size"]
        self.output_size = self.data["output_size"]
        self.all_words = self.data["all_words"]
        self.tags = self.data["tags"]
        self.model_state = self.data["model_state"]
        
        # Modeli ilklendir ve ağırlıkları yükle
        self.model = NeuralNet(self.input_size, self.hidden_size, self.output_size).to(self.device)
        self.model.load_state_dict(self.model_state)
        self.model.eval() # Çıkarım modu
        
        # Olası yanıtlar için veri setini yükle
        with open("core/dataset.json", "r", encoding="utf-8") as f:
            self.intents = json.load(f)["intents"]

        # 2. Bulut Gemini API'sini ilklendir
        self.gemini_enabled = False
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(
                    model_name="gemini-flash-latest",
                    system_instruction=settings.SYSTEM_INSTRUCTION
                )
                self.gemini_enabled = True
                print("[Sistem] Gemini API Bulut Entegrasyonu başarıyla aktifleştirildi!")
            except Exception as e:
                print(f"[UYARI] Gemini API başlatılamadı: {e}")
        else:
            print("[UYARI] GEMINI_API_KEY tanımlanmamış veya varsayılan değerde. Bulut özellikleri pasif.")

    def get_response(self, user_input: str) -> str:
        """Kullanıcının girdisine karşılık Jarvis'in metin yanıtını döner (Terminal uyumlu)."""
        res = self.get_response_structured(user_input)
        return res["response"]

    def get_response_structured(self, user_input: str) -> dict:
        """Kullanıcı girdisini yerel sinir ağıyla sınıflandırır, yanıt ve aksiyon detaylarını sözlük olarak döner (Bulut/API uyumlu)."""
        try:
            # 1. Girdiyi önişle ve yerel tahminde bulun
            tokens = tokenize(user_input)
            X = bag_of_words(tokens, self.all_words)
            X = torch.tensor(X, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            # 2. Tahmin yap
            outputs = self.model(X)
            _, predicted = torch.max(outputs, dim=1)
            tag = self.tags[predicted.item()]
            
            # Olasılık skorunu hesapla (Softmax)
            probs = torch.softmax(outputs, dim=1)
            prob = probs[0][predicted.item()].item()
            
            print(f"\n[Sistem] Yerel Tahmin Edilen Sınıf: '{tag}' (%{prob*100:.2f})")
            
            # 3. Güven eşiği kontrolü (%70) - Yerel komutlar için
            if prob > 0.70:
                # Eşleşen niyeti bul
                intent_info = next((item for item in self.intents if item["tag"] == tag), None)
                
                # Karşılık gelen aksiyonları çalıştır
                if tag == "saat_sorgusu":
                    return {"response": get_time_and_date(), "action": "none"}
                    
                elif tag == "sistem_sorgusu":
                    # Bulut ortamında sistem durumunu kontrol etmek yerel bilgisayarı yansıtmaz
                    # Bu nedenle özel bir açıklama dönüyoruz
                    return {
                        "response": "Şu an bulut üzerinden bağlandığımız için bilgisayarınızın donanım durumuna erişemiyorum efendim. Ancak sistemlerim genel olarak aktif.",
                        "action": "none"
                    }
                    
                elif tag == "web_acma":
                    lower_input = turkish_lower(user_input)
                    site_name = "Google"
                    site_url = "https://google.com"
                    
                    if "youtube" in lower_input:
                        site_name = "YouTube"
                        site_url = "https://youtube.com"
                    elif "github" in lower_input:
                        site_name = "GitHub"
                        site_url = "https://github.com"
                    elif "gmail" in lower_input:
                        site_name = "Gmail"
                        site_url = "https://gmail.com"
                        
                    return {
                        "response": f"{site_name} adresi telefonunuzda açılıyor, efendim.",
                        "action": "open_url",
                        "url": site_url
                    }
                    
                elif tag == "uygulama_acma":
                    return {
                        "response": "Bulut sunucu üzerinden yerel bilgisayarınızda uygulama çalıştıramam efendim.",
                        "action": "none"
                    }
                
                # Diğer etiketler için şablondan rastgele yanıt seç
                if intent_info and "responses" in intent_info:
                    return {"response": random.choice(intent_info["responses"]), "action": "none"}
            
            # 4. Güven eşiği altındaysa veya bilinmeyen bir soruysa Gemini API'sine yönlendir (Hibrit Fallback)
            if self.gemini_enabled:
                print(f"[Sistem] Düşük güven skoru veya genel soru algılandı. Bulut Gemini API'ye gönderiliyor...")
                try:
                    response = self.gemini_model.generate_content(user_input)
                    return {
                        "response": response.text,
                        "action": "none"
                    }
                except Exception as gemini_ex:
                    return {
                        "response": f"Üzgünüm efendim, buluttaki yapay zekama bağlanırken bir sorunla karşılaştım: {str(gemini_ex)}",
                        "action": "none"
                    }
            
            # Gemini de pasifse fallback yanıtı ver
            return {
                "response": "Sizi tam olarak anlayamadım efendim. Bu komut yerel veritabanımda tanımlı değil.",
                "action": "none"
            }
            
        except Exception as e:
            return {
                "response": f"Üzgünüm efendim, yerel düşünme modülümde bir hata oluştu: {str(e)}",
                "action": "none"
            }
            
    def clear_history(self):
        """Yerel beyinde sohbet geçmişine gerek yoktur."""
        pass
