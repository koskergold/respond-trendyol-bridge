import requests
import base64
import os

# Environment variables'dan al
API_KEY = os.getenv("TRENDYOL_API_KEY")
API_SECRET = os.getenv("TRENDYOL_API_SECRET")
SELLER_ID = os.getenv("TRENDYOL_SELLER_ID")
RESPOND_WEBHOOK = os.getenv("RESPOND_WEBHOOK_URL")

credentials = f"{API_KEY}:{API_SECRET}"
base64_creds = base64.b64encode(credentials.encode()).decode()

headers = {
    'Authorization': f'Basic {base64_creds}',
    'User-Agent': f'{SELLER_ID} - SelfIntegration',
    'Content-Type': 'application/json'
}

# Son soru ID'sini GitHub Actions cache'den al
cache_file = 'last_question_id.txt'
try:
    with open(cache_file, 'r') as f:
        last_question_id = int(f.read().strip())
except:
    last_question_id = 0

print(f"🚀 Bot başladı! Son ID: {last_question_id}")

try:
    url = f"https://apigw.trendyol.com/integration/qna/sellers/{SELLER_ID}/questions/filter"
    params = {
        'supplierId': SELLER_ID,
        'status': 'WAITING_FOR_ANSWER',
        'size': 50,
        'orderByField': 'CreatedDate',
        'orderByDirection': 'DESC'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        questions = response.json().get('content', [])
        print(f"📊 Toplam {len(questions)} soru bulundu")
        
        new_questions = [q for q in questions if q['id'] > last_question_id]
        
        if new_questions:
            print(f"🆕 {len(new_questions)} yeni soru!")
            
            for question in reversed(new_questions):
                if RESPOND_WEBHOOK:
                    payload = {
                        "message": {
                            "type": "text",
                            "text": f"📦 Ürün: {question.get('productName', 'Bilinmiyor')}\n\n❓ Soru: {question['text']}\n\n👤 Müşteri: {question.get('userName', 'Anonim')}"
                        },
                        "contact": {
                            "customId": str(question['customerId']),
                            "firstName": question.get('userName', 'Müşteri')
                        },
                        "metadata": {
                            "questionId": str(question['id']),
                            "productName": question.get('productName', ''),
                            "source": "trendyol"
                        }
                    }
                    
                    webhook_response = requests.post(RESPOND_WEBHOOK, json=payload, timeout=10)
                    
                    if webhook_response.status_code in [200, 201]:
                        print(f"✅ Soru #{question['id']} gönderildi")
                        last_question_id = question['id']
                    else:
                        print(f"❌ Webhook hatası: {webhook_response.status_code}")
                else:
                    print(f"⚠️ Webhook URL yok")
                    last_question_id = question['id']
        else:
            print("💤 Yeni soru yok")
        
        # Son ID'yi kaydet
        with open(cache_file, 'w') as f:
            f.write(str(last_question_id))
    else:
        print(f"⚠️ API Hatası: {response.status_code}")
        
except Exception as e:
    print(f"❌ Hata: {str(e)}")

print("✅ Kontrol tamamlandı!")
