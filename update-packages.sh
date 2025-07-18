cat requirements.txt | cut -d = -f1 | xargs -I{} pip install {} --break-system-packages
