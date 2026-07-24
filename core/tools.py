import os
import sys
import webbrowser
import psutil
import datetime
import subprocess
import requests
import xml.etree.ElementTree as ET

def get_system_status() -> str:
    """Bilgisayarın CPU, bellek durumunu ve bataryasını sorgular."""
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    battery = psutil.sensors_battery()
    battery_info = ""
    if battery:
        percent = battery.percent
        plugged = "Şarj ediliyor" if battery.power_plugged else "Fişe takılı değil"
        battery_info = f", Batarya Seviyesi: %{percent} ({plugged})"
        
    return f"İşlemci Kullanımı: %{cpu_usage}, Bellek Kullanımı: %{memory_usage}{battery_info}."

def get_time_and_date() -> str:
    """Mevcut tarih ve saati Türkçe formatta döner (Türkiye saat dilimi UTC+3'e uyarlanmıştır)."""
    # Türkiye UTC+3 saat diliminde olduğu için
    tz_turkey = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(tz_turkey)
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    gun = gunler[now.weekday()]
    return now.strftime(f"Saat %H:%M, Tarih %d.%m.%Y ({gun})")

def open_website(url: str) -> str:
    """Kullanıcının talep ettiği web sitesini varsayılan tarayıcıda açar."""
    # Güvenlik önlemi: URL'nin geçerli bir protokol içerdiğinden emin olalım
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    webbrowser.open(url)
    return f"{url} adresi tarayıcınızda açılıyor, efendim."

def run_application(app_name: str) -> str:
    """Windows üzerinde kod editörü, tarayıcı gibi uygulamaları açar."""
    app_map = {
        "not defteri": "notepad.exe",
        "hesap makinesi": "calc.exe",
        "tarayıcı": "chrome.exe",
        "chrome": "chrome.exe",
        "paint": "mspaint.exe",
        "kod editörü": "code"
    }
    
    app_lower = app_name.lower()
    command = app_map.get(app_lower)
    
    if command:
        try:
            subprocess.Popen(command, shell=True)
            return f"{app_name} uygulamasını başlatıyorum, efendim."
        except Exception as e:
            return f"{app_name} başlatılırken bir hata oluştu: {str(e)}"
    else:
        # Eğer eşleşmezse doğrudan komut isteminde çalıştırmaya çalışalım
        try:
            subprocess.Popen(app_name, shell=True)
            return f"'{app_name}' komutunu sisteme gönderdim efendim."
        except Exception as e:
            return f"Üzgünüm efendim, '{app_name}' uygulamasını bulamadım."

def get_weather(city: str = "Bursa") -> str:
    """wttr.in üzerinden anlık hava durumunu Türkçe olarak sorgular."""
    try:
        url = f"https://wttr.in/{city}?format=%C,+Sıcaklık:+%t+(Hissedilen:+%f)&lang=tr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"{city} şehri için hava durumu: {response.text.strip()} efendim."
        return f"{city} için hava durumu bilgisi şu an alınamadı efendim."
    except Exception as e:
        return f"Hava durumu sorgulanırken bir hata oluştu efendim: {str(e)}"

def get_news() -> str:
    """NTV Haber RSS Feed üzerinden son 3 son dakika haberini çeker."""
    try:
        url = "https://www.ntv.com.tr/son-dakika.rss"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # Atom formatında entry'leri çek
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            if not entries:
                return "Şu an güncel haber başlıklarına erişemiyorum efendim."
            
            news_list = []
            for i, entry in enumerate(entries[:3]):
                title = entry.find('{http://www.w3.org/2005/Atom}title')
                if title is not None:
                    news_list.append(f"{i+1}. {title.text}")
            
            return "İşte son dakika haber başlıkları efendim: " + " | ".join(news_list)
        return "Şu an güncel haber bültenine erişemiyorum efendim."
    except Exception as e:
        return f"Haber bülteni çekilirken bir hata oluştu efendim: {str(e)}"

# Kullanılabilecek tüm fonksiyonları listeleyen bir sözlük
AVAILABLE_TOOLS = {
    "get_system_status": get_system_status,
    "get_time_and_date": get_time_and_date,
    "open_website": open_website,
    "run_application": run_application,
    "get_weather": get_weather,
    "get_news": get_news
}
