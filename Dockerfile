# Base image olarak Python 3.11 kullan
FROM python:3.11

# Çalışma dizini
WORKDIR /app

# Tüm dosyaları konteynıra kopyala
COPY . /app

# pip güncelle
RUN pip install --upgrade pip

# Gereken kütüphaneleri yükle
RUN pip install -r requirements.txt

# Botu çalıştır
CMD ["python", "bot/command_bot.py"]
