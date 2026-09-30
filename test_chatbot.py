import pandas as pd
from modules.chatbot import _build_context, SYSTEM_PROMPT

import sys
sys.path.append('.')

df = pd.DataFrame({
    "Subscriber_ID": [1, 2],
    "Subscriber_Name": ["A", "B"],
    "source_ip": ["1.1.1.1", "2.2.2.2"],
    "destination_ip": ["8.8.8.8", "9.9.9.9"],
    "timestamp": ["2023-01-01", "2023-01-02"],
    "domain": ["google.com", "yahoo.com"],
    "protocol": ["HTTP", "HTTPS"],
    "data_volume_bytes": [1000, 2000],
    "is_tor": [False, False],
    "is_foreign_ip": [True, True],
    "is_off_hours": [False, True],
    "Is_Off_Hours": [False, True],
    "Hour_IST": [14, 2],
    "Data_Volume_Bytes": [1000, 2000],
    "Is_TOR": [False, False],
    "Is_Foreign_IP": [False, False],
    "Is_VPN_Suspected": [False, False],
})

analysis_state = {
    "loaded": True,
    "df": df,
    "stats": {"total_sessions": 2},
    "risk_scores": pd.DataFrame({"Subscriber_Name": ["A"], "Subscriber_ID": [1], "Risk_Score": [50], "Risk_Level": ["MEDIUM"], "Total_Sessions": [1]}),
}

api_key = "AQ.Ab8RN6Jz62xrnUISZ02gKoSlnJXWhvAJnO-5e1iLoz3-yQCP2Q"

print("Building context...")
context = _build_context(analysis_state)
full_prompt = SYSTEM_PROMPT.format(context=context) + f"\n\nQuestion: hello"

print("Testing API...")
try:
    from google import genai as google_genai
    client = google_genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=full_prompt,
    )
    answer = response.text.strip()
    print("API SUCCESS:", answer)
except Exception as e:
    import traceback
    traceback.print_exc()

