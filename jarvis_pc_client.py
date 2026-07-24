import time
import urllib.request
import urllib.parse
import json
import subprocess
import ctypes
import os

# Render Sunucu Adresi
SERVER_URL = "https://my-jarvis-us.onrender.com/api/pc/poll"
# Güvenlik Tokenı (Render panelinde ayarladığın şifre ile birebir aynı olmalıdır!)
JARVIS_TOKEN = "JarvisStarkDefaultToken123!"

# Windows Sanal Tuş Kodları (Virtual Key Codes)
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

def press_key(vk_code):
    """Belirtilen sanal tuşa basıp çeker."""
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0) # Key Up
    except Exception as e:
        print(f"[HATA] Tuş simülasyonu başarısız: {e}")

def execute_command(cmd_data):
    """Sunucudan gelen komutu işletim sisteminde çalıştırır."""
    action = cmd_data.get("action")
    print(f"\n[Komut Alındı] Aksiyon: {action}")
    
    if action == "lock":
        print("[İşlem] Bilgisayar kilitleniyor...")
        ctypes.windll.user32.LockWorkStation()
        
    elif action == "sleep":
        print("[İşlem] Bilgisayar uyku moduna alınıyor...")
        # SetSuspendState: 0 (Suspend/Sleep), 1 (Force), 0 (Disable Wake Events)
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
    elif action == "shutdown":
        print("[İşlem] Bilgisayar 10 saniye içinde kapatılacak...")
        os.system("shutdown /s /t 10")
        
    elif action == "abort_shutdown":
        print("[İşlem] Bilgisayar kapatma işlemi iptal edildi...")
        os.system("shutdown /a")
        
    elif action == "media_play_pause":
        print("[İşlem] Oynat/Durdur tetikleniyor...")
        press_key(VK_MEDIA_PLAY_PAUSE)
        
    elif action == "media_next":
        print("[İşlem] Sonraki parça tetikleniyor...")
        press_key(VK_MEDIA_NEXT_TRACK)
        
    elif action == "media_prev":
        print("[İşlem] Önceki parça tetikleniyor...")
        press_key(VK_MEDIA_PREV_TRACK)
        
    elif action == "volume_up":
        print("[İşlem] Ses yükseltiliyor...")
        # Sesi kademeli artırmak için 3 kez tetikleyelim
        for _ in range(3):
            press_key(VK_VOLUME_UP)
            time.sleep(0.05)
            
    elif action == "volume_down":
        print("[İşlem] Ses kısılıyor...")
        for _ in range(3):
            press_key(VK_VOLUME_DOWN)
            time.sleep(0.05)
            
    elif action == "volume_mute":
        print("[İşlem] Ses sessize alınıyor...")
        press_key(VK_VOLUME_MUTE)
        
    else:
        print(f"[UYARI] Tanımlanamayan aksiyon: {action}")

def main():
    print("=========================================")
    print("      Jarvis Windows PC Controller       ")
    print("=========================================")
    print(f"Hedef Sunucu: {SERVER_URL}")
    print("Sunucudan komut bekleniyor... Kapatmak için Ctrl+C tuşlarına basın.")
    print("-----------------------------------------")
    
    while True:
        try:
            req = urllib.request.Request(
                SERVER_URL, 
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'X-Jarvis-Token': JARVIS_TOKEN
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    res_data = json.loads(response.read().decode('utf-8'))
                    commands = res_data.get("commands", [])
                    for cmd in commands:
                        execute_command(cmd)
        except urllib.error.URLError as url_err:
            # Sunucu uyanırken veya internet kesintilerinde sessizce bekleyelim
            pass
        except Exception as e:
            print(f"[HATA] Beklenmedik bağlantı hatası: {e}")
            
        time.sleep(2) # Her 2 saniyede bir sunucuyu sorgula (Long polling taklidi)

if __name__ == "__main__":
    main()
