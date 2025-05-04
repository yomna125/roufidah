from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import math
from openai import OpenAI  # ✅ متوافق مع الإصدار الجديد

app = Flask(__name__)
CORS(app)

# ✅ مفتاح OpenAI (حدثه بمفتاحك الحقيقي)
client = OpenAI(api_key="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")

# بيانات المستشفيات
hospitals = [
    {"name": "مجمع الدمام الطبي", "lat": 26.43209, "lng": 50.08371},
    {"name": "مستشفى القطيف المركزي", "lat": 26.52433, "lng": 49.96678},
    {"name": "مستشفى الجبيل العام", "lat": 26.99445, "lng": 49.65962},
    {"name": "مستشفى رأس تنورة العام", "lat": 26.71263, "lng": 50.06662},
    {"name": "مستشفى الأمير سلطان بالعُرَيِّرَة", "lat": 25.97166, "lng": 48.87059},
    {"name": "مستشفى الخفجي العام", "lat": 28.41996, "lng": 48.47182},
    {"name": "مستشفى القرية العليا العام", "lat": 27.56126, "lng": 47.70875},
    {"name": "مستشفى بقيق العام", "lat": 25.92551, "lng": 49.64767},
    {"name": "مستشفى النعيرية العام", "lat": 27.47249, "lng": 48.46598},
]

def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_nearest_hospital(user_lat, user_lng):
    nearest = None
    min_dist = float('inf')
    for hospital in hospitals:
        dist = calculate_distance(user_lat, user_lng, hospital['lat'], hospital['lng'])
        if dist < min_dist:
            min_dist = dist
            nearest = hospital
    return nearest, min_dist

@app.route('/')
def index():
    return render_template('index.html')  # تأكد أن index.html في مجلد templates

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    lat = data.get("lat")
    lng = data.get("lng")

    # إذا المستخدم سأل عن أقرب مستشفى والموقع موجود
    if lat and lng and ("أقرب مستشفى" in message or "وين المستشفى" in message):
        nearest, distance = find_nearest_hospital(lat, lng)
        return jsonify({
            "reply": f"📍 تم تحديد موقعك.\n🏥 أقرب مستشفى هو: {nearest['name']}، ويبعد تقريبًا {distance:.2f} كم."
        })

    # الرد باستخدام GPT من OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد صحي ذكي تساعد المستخدمين في الإجابة على الأسئلة الطبية أو الطارئة."},
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"❌ حدث خطأ في الاتصال بـ OpenAI: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
