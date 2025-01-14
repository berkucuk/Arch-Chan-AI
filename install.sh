#!/bin/bash
# Groq AI API anahtarı
read -p "Groq AI API key: " groq_api_key
if [ -f .env ]; then
    if grep -q "Groq_Api_Key=" .env; then
        sed -i "s/^Groq_Api_Key=.*/Groq_Api_Key=${groq_api_key}/" .env
        echo "Groq API anahtarı güncellendi."
    else
        echo "Groq_Api_Key=${groq_api_key}" >> .env
        echo "Groq API anahtarı .env dosyasına eklendi."
    fi
else
    echo "Groq_Api_Key=${groq_api_key}" > .env
    echo ".env dosyası oluşturuldu ve Groq API anahtarı eklendi."
fi

# WeatherAPI anahtarı
read -p "WeatherAPI key: " weather_api_key
if [ -f .env ]; then
    if grep -q "Weather_Api_Key=" .env; then
        sed -i "s/^Weather_Api_Key=.*/Weather_Api_Key=${weather_api_key}/" .env
        echo "WeatherAPI anahtarı güncellendi."
    else
        echo "Weather_Api_Key=${weather_api_key}" >> .env
        echo "WeatherAPI anahtarı .env dosyasına eklendi."
    fi
else
    echo "Weather_Api_Key=${weather_api_key}" > .env
    echo ".env dosyası oluşturuldu ve WeatherAPI anahtarı eklendi."
fi

sudo pacman -S python-virtualenv libpng --noconfirm --needed
sudo apt install python3-venv
chmod +x Linux-Chan-AI.desktop
mkdir -p ~/.local/share/applications/
cp Linux-Chan-AI.desktop ~/.local/share/applications/
sudo mkdir /usr/share/Linux-Chan-AI
sudo cp .env /usr/share/Linux-Chan-AI
sudo python3 -m venv /usr/share/Linux-Chan-AI/python-env
sudo /usr/share/Linux-Chan-AI/python-env/bin/pip3 install -r requirements.txt
sudo cp linux-chan.py /usr/share/Linux-Chan-AI
sudo cp -r icons /usr/share/Linux-Chan-AI
sudo mkdir /usr/share/Linux-Chan-AI/temp_voice
