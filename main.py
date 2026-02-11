import requests
import base64
import os
import time

API_KEY = os.getenv("TRENDYOL_API_KEY")
API_SECRET = os.getenv("TRENDYOL_API_SECRET")
SELLER_ID = os.getenv("TRENDYOL_SELLER_ID")
RESPOND_WEBHOOK = os.getenv("RESPOND_WEBHOOK_URL")
RESPOND_CHANNEL_ID = os.getenv("RESPOND_CHANNEL_ID")
RESPOND_API_TOKEN = os.getenv("RESPOND_API_TOKEN")

credentials = f"{API_KEY}:{API_SECRET}"
base64_creds = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {base64_creds}",
    "User-Agent": f"{SELLER_ID} - SelfIntegration",
    "Content-Type": "application/json"
}

cache_file = "last_question_id.txt"

try:
    with open(cache_file, "r") as f:
        last_question_id = int(f.read().strip())
except:
    last_question_id = 0

print(f"🚀 Bot başladı! Son ID: {last_question_id}")


# --------------------------------------------------
# Trendyol API request with retry
# --------------------------------------------------
def trendyol_get(url, params, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 200:
                return r
            print("⚠️ Trendyol API status:", r.status_code)
        except Exception as e:
            print("⚠️ Trendyol retry:", e)
        time.sleep(2)
    return None


# --------------------------------------------------
# Pagination ile TÜM soruları çek
# --------------------------------------------------
all_questions = []
page = 0

while True:
    url = f"https://apigw.trendyol.com/integration/qna/sellers/{SELLER_ID}/questions/filter"

    params = {
        "supplierId": SELLER_ID,
        "status": "WAITING_FOR_ANSWER",
        "size": 50,
        "page": page,
        "orderByField": "CreatedDate",
        "orderByDirection": "DESC"
    }

    response = trendyol_get(url, params)
    if not response:
        break

    data = response.json()
    content = data.get("content", [])

    if not content:
        break

    all_questions.extend(content)
    page += 1


print(f"📊 Toplam çekilen soru: {len(all_questions)}")

# --------------------------------------------------
# Yeni soruları filtrele
# --------------------------------------------------
new_questions = [q for q in all_questions if q["id"] > last_question_id]
new_questions.sort(key=lambda x: x["id"])

print(f"🆕 Yeni soru sayısı: {len(new_questions)}")


# --------------------------------------------------
# Respond.io gönder
# --------------------------------------------------
def send_to_respond(question):
    payload = {
        "channelId": RESPOND_CHANNEL_ID,
        "contact": {
            "customId": str(question["customerId"]),
            "firstName": question.get("userName", "Müşteri"),
            "lastName": "Trendyol"
        },
        "message": {
            "type": "text",
            "text": (
                f"📦 Ürün: {question.get('productName','Bilinmiyor')}\n\n"
                f"❓ Soru: {question['text']}\n\n"
                f"👤 Müşteri: {question.get('userName','Anonim')}\n\n"
                f"🆔 Soru ID: {question['id']}"
            )
        }
    }

    headers_webhook = {
        "Authorization": f"Bearer {RESPOND_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(RESPOND_WEBHOOK, json=payload, headers=headers_webhook, timeout=20)
        return r.status_code in (200, 201)
    except Exception as e:
        print("❌ Webhook exception:", e)
        return False


# --------------------------------------------------
# Gönderim
# --------------------------------------------------
for question in new_questions:

    if not (RESPOND_WEBHOOK and RESPOND_CHANNEL_ID and RESPOND_API_TOKEN):
        print("❌ Respond bilgileri eksik")
        break

    ok = send_to_respond(question)

    if ok:
        print(f"✅ Gönderildi: {question['id']}")
        last_question_id = question["id"]

        with open(cache_file, "w") as f:
            f.write(str(last_question_id))
    else:
        print("❌ Gönderilemedi. İşlem durdu.")
        break


print("✅ Kontrol tamamlandı")
