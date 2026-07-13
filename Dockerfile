FROM python:3.10-slim

WORKDIR /app

# Gerekli sistem paketlerini kur (derleme araçları vb.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# İmaj boyutunu küçük tutmak için PyTorch CPU versiyonunu önceden kuruyoruz
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Gereksinimler dosyasını kopyala ve diğer paketleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Flask API için portu dışa aç
EXPOSE 5000

# API sunucusunu çalıştır
CMD ["python", "app.py"]
