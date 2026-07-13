import pyttsx3
import speech_recognition as sr
from config import settings
import sys

class JarvisVoice:
    def __init__(self):
        # Text-to-Speech Motorunu İlklendir
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', settings.JARVIS_VOICE_SPEED)
            
            # Türkçe ses aramaya çalış
            voices = self.engine.getProperty('voices')
            turkish_voice_found = False
            for voice in voices:
                if "tr" in voice.id.lower() or "turkish" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    turkish_voice_found = True
                    break
            
            # Eğer Türkçe ses bulunamazsa ilk sesi varsayılan olarak bırak
            if not turkish_voice_found and voices:
                self.engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"[UYARI] Ses çıkış motoru başlatılamadı: {e}", file=sys.stderr)
            self.engine = None

        # Speech-to-Text Mikrofon İlklendir
        self.recognizer = sr.Recognizer()
        # Gürültü toleransını ayarla
        self.recognizer.dynamic_energy_threshold = True

    def speak(self, text: str):
        """Jarvis'in verilen metni seslendirmesini sağlar."""
        print(f"\n{settings.JARVIS_NAME}: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[HATA] Seslendirme sırasında bir sorun oluştu: {e}")
        else:
            # Ses motoru yoksa sadece ekrana yazdırır (geliştirme ortamları için yedek)
            pass

    def listen(self) -> str:
        """Kullanıcının mikrofondan söylediği Türkçe cümleyi metne dönüştürür."""
        if not sys.stdin.isatty():
            # Eğer interaktif bir terminalde değilsek yazı girişine zorla (veya hata alma)
            return input("Siz (yazın): ")
            
        with sr.Microphone() as source:
            print("\nDinliyorum... Efendim?")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Algılanıyor...")
                
                # Google Speech Recognition ile Türkçe metne çevir
                query = self.recognizer.recognize_google(audio, language="tr-TR")
                print(f"Siz: {query}")
                return query
            except sr.WaitTimeoutError:
                # Kullanıcı konuşmadı
                return ""
            except sr.UnknownValueError:
                # Ses anlaşılamadı
                self.speak("Sizi tam olarak anlayamadım efendim. Tekrar söyler misiniz?")
                return ""
            except Exception as e:
                # Mikrofon yoksa veya başka hata varsa konsol girdi moduna geç
                print(f"\n[Sistem] Mikrofon algılanamadı veya hata oluştu ({e}). Yazılı moda geçiliyor.")
                return input("Siz (yazın): ")
