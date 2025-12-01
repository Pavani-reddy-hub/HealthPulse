from flask import Flask, request, render_template_string
import random
import google.generativeai as genai
import os

app = Flask(__name__)

# ------------------- GEMINI AI CONFIG -------------------
# Make sure you have set your environment variable before running:
# On Windows: set GOOGLE_API_KEY=YOUR_API_KEY
# On Mac/Linux: export GOOGLE_API_KEY=YOUR_API_KEY
genai.configure(api_key=os.environ.get("AIzaSyA4XkXRe3a-KYyCr8xyTj5V3N6VcRlziok"))

# ------------------- DATA -------------------
SYMPTOMS = [
    "Fever", "Cough", "Headache", "Fatigue", "Nausea", "Chest Pain", "Cold", "Body Pain"
]

TIPS = [
    "Drink 8 glasses of water daily to stay hydrated.",
    "Get at least 7 hours of sleep every night.",
    "Eat fresh fruits and green vegetables daily."
]

HOME_REMEDIES = {
    "Fever": [
        "Drink tulsi and ginger tea twice a day.",
        "Apply a cool wet cloth on your forehead.",
        "Eat light food like soup and khichdi."
    ],
    "Cough": [
        "Mix honey with warm water or ginger juice.",
        "Steam inhalation with eucalyptus oil.",
        "Avoid cold drinks and dusty areas."
    ],
    "Headache": [
        "Massage your temples with peppermint oil.",
        "Drink plenty of water — dehydration causes headaches.",
        "Rest your eyes and avoid screen time."
    ],
    "Fatigue": [
        "Drink lemon water with honey.",
        "Take small power naps during the day.",
        "Do light stretching exercises."
    ],
    "Nausea": [
        "Sip on ginger tea or chew fresh ginger.",
        "Avoid oily or spicy food.",
        "Take deep breaths and rest."
    ],
    "Chest Pain": [
        "Drink warm water slowly.",
        "Avoid heavy meals and smoking.",
        "Consult a doctor if pain persists."
    ],
    "Cold": [
        "Take steam inhalation twice daily.",
        "Drink turmeric milk at night.",
        "Avoid cold beverages."
    ],
    "Body Pain": [
        "Take a warm bath with Epsom salt.",
        "Do light stretching or yoga.",
        "Apply pain relief balm or Volini gel."
    ]
}

MEDICINES = {
    "Fever": [
        {"name": "Paracetamol 500mg", "use": "Take 1 tablet every 6 hours if fever > 100°F", "price": "₹20/strip"},
        {"name": "Dolo-650", "use": "After meals, for high fever", "price": "₹35/strip"},
        {"name": "Crocin", "use": "Every 8 hours if fever persists", "price": "₹30/strip"}
    ],
    "Cough": [
        {"name": "Benadryl", "use": "2 tsp twice a day after meals", "price": "₹80/bottle"},
        {"name": "Ascoril LS", "use": "1 tsp thrice a day", "price": "₹95/bottle"},
        {"name": "Chericof", "use": "2 tsp morning and night", "price": "₹90/bottle"}
    ],
    "Headache": [
        {"name": "Saridon", "use": "After food if pain is mild", "price": "₹25/strip"},
        {"name": "Disprin", "use": "Dissolve in water once daily", "price": "₹20/strip"},
        {"name": "Ibuprofen", "use": "Every 8 hours for severe pain", "price": "₹45/strip"}
    ],
    "Cold": [
        {"name": "Sinarest", "use": "After meals, twice a day", "price": "₹30/strip"},
        {"name": "Cetirizine", "use": "Before sleep for sneezing relief", "price": "₹25/strip"},
        {"name": "Steam inhalation", "use": "3 times daily", "price": "Free home remedy"}
    ]
}

# ------------------- TEMPLATE -------------------
TEMPLATE_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>HealthPulse AI</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f8f9;
            margin: 40px;
            color: #333;
        }
        h1 { color: #0077b6; text-align: center; }
        .layout { display: flex; justify-content: space-between; gap: 20px; }
        .side { width: 25%; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        .main { width: 70%; background: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        h3 { color: #023e8a; }
        button { background: #0077b6; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #023e8a; }
        input, select { padding: 10px; margin: 5px 0; width: 90%; }
        ul { padding-left: 20px; }
        li { margin-bottom: 6px; }
    </style>
</head>
<body>
    <h1>🏥 HealthPulse AI</h1>

    <div class="layout">
        <div class="side">
            <h3>🤖 AI Diagnosis</h3>
            <form method="POST" action="/ai_diagnosis">
                <select name="symptom" required>
                    <option value="">Select Symptom</option>
                    {% for s in symptoms %}
                    <option value="{{ s }}">{{ s }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="extra" placeholder="Describe more symptoms (optional)">
                <button type="submit">Check</button>
            </form>
            <hr>
            <h3>💊 Medicine Info</h3>
            <form method="POST" action="/medicine">
                <select name="symptom" required>
                    {% for s in symptoms %}
                    <option value="{{ s }}">{{ s }}</option>
                    {% endfor %}
                </select>
                <button type="submit">Show</button>
            </form>
            <hr>
            <h3>🏥 Hospital Finder</h3>
            <form method="POST" action="/hospitals">
                <input type="text" name="city" placeholder="Enter City" required>
                <button type="submit">Search</button>
            </form>
            <hr>
            <h3>🌿 Daily Health Tip</h3>
            <p>{{ random_tip }}</p>
        </div>

        <div class="main">
            {% if result %}
                <h2>🩺 AI Diagnosis Result</h2>
                <p>{{ result }}</p>
            {% endif %}

            {% if remedies %}
                <h2>🏠 Home Remedies</h2>
                <ul>
                {% for r in remedies %}
                    <li>{{ r }}</li>
                {% endfor %}
                </ul>
            {% endif %}

            {% if medicines %}
                <h2>💊 Recommended Medicines</h2>
                <table border="1" cellpadding="6" cellspacing="0">
                    <tr><th>Name</th><th>When to Take</th><th>Price</th></tr>
                    {% for med in medicines %}
                        <tr><td>{{ med.name }}</td><td>{{ med.use }}</td><td>{{ med.price }}</td></tr>
                    {% endfor %}
                </table>
            {% endif %}

            {% if hospitals %}
                <h2>🏥 Hospitals in {{ city }}</h2>
                <ul>
                {% for h in hospitals %}
                    <li><b>{{ h.name }}</b> — {{ h.city }} — 📞 {{ h.contact }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# ------------------- ROUTES -------------------
@app.route('/')
def home():
    return render_template_string(
        TEMPLATE_DASHBOARD,
        symptoms=SYMPTOMS,
        random_tip=random.choice(TIPS)
    )

@app.route('/ai_diagnosis', methods=['POST'])
def ai_diagnosis():
    symptom = request.form['symptom']
    extra = request.form.get('extra', "")
    prompt = f"The patient has {symptom}. {extra}. Explain likely disease and precautions in short points."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        result = response.text
    except Exception as e:
        result = f"AI Error: {e}"

    remedies = HOME_REMEDIES.get(symptom, ["No remedies available."])

    return render_template_string(
        TEMPLATE_DASHBOARD,
        symptoms=SYMPTOMS,
        random_tip=random.choice(TIPS),
        result=result,
        remedies=remedies
    )

@app.route('/medicine', methods=['POST'])
def medicine():
    symptom = request.form['symptom']
    medicines = MEDICINES.get(symptom, [])
    remedies = HOME_REMEDIES.get(symptom, [])
    return render_template_string(
        TEMPLATE_DASHBOARD,
        symptoms=SYMPTOMS,
        random_tip=random.choice(TIPS),
        medicines=medicines,
        remedies=remedies
    )

@app.route('/hospitals', methods=['POST'])
def hospitals():
    city = request.form['city']
    HOSPITALS = [
        {"name": "Apollo Hospitals", "city": "Hyderabad", "contact": "040-27707777"},
        {"name": "Yashoda Hospitals", "city": "Hyderabad", "contact": "040-45674567"},
        {"name": "Fortis Hospital", "city": "Bihar", "contact": "080-66664567"},
        {"name": "AIIMS", "city": "Delhi", "contact": "011-26588500"},
        {"name": "Renovo", "city": "Medchal", "contact": "040-27707777"},
        {"name": "Srikar", "city": "Kompally", "contact": "040-45674567"}
    ]
    filtered = [h for h in HOSPITALS if city.lower() in h['city'].lower()]
    if not filtered:
        filtered = [{"name": "No hospitals found", "city": city, "contact": "-"}]

    return render_template_string(
        TEMPLATE_DASHBOARD,
        symptoms=SYMPTOMS,
        random_tip=random.choice(TIPS),
        hospitals=filtered,
        city=city
    )

# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
