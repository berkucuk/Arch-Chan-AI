#!/bin/bash
read -p "Groq AI api key: " api_key
if [ -f .env ]; then
    if grep -q "Groq_Api_Key=" .env; then
        sed -i "s/^Groq_Api_Key=.*/Groq_Api_Key=${api_key}/" .env
        echo "API anahtarı güncellendi."
    else
        echo "Groq_Api_Key=${api_key}" >> .env
        echo "API anahtarı .env dosyasına eklendi."
    fi
else
    echo "Groq_Api_Key=${api_key}" > .env
    echo ".env dosyası oluşturuldu ve API anahtarı eklendi."
fi

sudo pacman -S python-virtualenv libpng --noconfirm --needed
chmod +x Arch-Chan-AI.desktop
mkdir -p ~/.local/share/applications/
cp Arch-Chan-AI.desktop ~/.local/share/applications/
sudo mkdir /usr/share/Arch-Chan-AI
sudo cp .env /usr/share/Arch-Chan-AI
sudo python3 -m venv /usr/share/Arch-Chan-AI/python-env
sudo /usr/share/Arch-Chan-AI/python-env/bin/pip3 install -r requirements.txt
sudo cp arch-chan.py /usr/share/Arch-Chan-AI
sudo cp -r icons /usr/share/Arch-Chan-AI
