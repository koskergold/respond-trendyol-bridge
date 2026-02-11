import requests
import base64
import os

# 1. Değişkenleri ve yolları tanımla
API_KEY = os.getenv("TRENDYOL_API_KEY")
API_SECRET = os.getenv("TRENDYOL_API_SECRET")
SELLER_ID = os.getenv("TRENDYOL_SELLER_ID")
RESPOND_WEBHOOK = os.getenv("RESPOND_WEBHOOK_URL")
RESPOND_CHANNEL_ID = os.getenv("RESPOND_CHANNEL_ID")
RESPOND_API_TOKEN = os.getenv("RESPOND_API_TOKEN")

cache_file = 'last_question_id.txt'

# --- YENİ EKLENEN KISIM BURASI ---
# 2. Dosya kontrolü (Emniyet Kemeri)
if not os.path.exists(cache_file):
    print(f"ℹ️ {cache_file} bulunamadı, ilk kurulum yapılıyor...")
    with open(cache_file, 'w') as f:
        f.write('0') 
# --------------------------------

# 3. Kimlik doğrulama ayarları
credentials = f"{API_KEY}:{API_SECRET}"
base64_creds = base64.b64encode(credentials.encode()).decode()

headers = {
    'Authorization': f'Basic {base64_creds}',
    'User-Agent': f'{SELLER_ID} - SelfIntegration',
    'Content-Type': 'application/json'
}

# 4. Son soru ID'sini oku
try:
    with open(cache_file, 'r') as f:
        content = f.read().strip()
        last_question_id = int(content) if content else 0
except Exception as e:
    print(f"⚠️ Dosya okuma hatası, ID 0 varsayılıyor: {e}")
    last_question_id = 0

print(f"🚀 Bot başladı! Son ID: {last_question_id}")

# ... Kodun geri kalanı aynı kalabilir
