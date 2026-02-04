import os
import re
import json
import requests
from groq import Groq

# ------------------------------------------------------------------
# PASTE YOUR GROQ KEY BELOW
# ------------------------------------------------------------------
client = Groq(api_key="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") 

SYSTEM_PROMPT = """
ROLE: You are 'Sarla Devi', a 72-year-old confused Indian grandmother.
TASK: Engage the scammer. Act confused but interested.
GOAL: Keep them talking to extract their UPI ID, Bank Details, or Phone Number.
RULES:
1. Never admit you know it's a scam.
2. Make typos (e.g., "ok beta", "wait checking", "net slow").
3. Ask for their UPI/Bank details so you can "send money".
"""

# --- Section 12: Intelligence Extraction ---
def extract_intel(text):
    return {
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "phishingLinks": re.findall(r'https?://\S+', text),
        "phoneNumbers": re.findall(r'[6-9]\d{9}', text),
        "suspiciousKeywords": re.findall(r'(?i)(urgent|verify|block|kyc|expiry|suspend)', text)
    }

# --- Section 12: Mandatory Callback ---
def send_guvi_callback(session_id, history_len, intel, scam_detected=True):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": history_len,
        "extractedIntelligence": intel,
        "agentNotes": "Scammer engaged. Attempting to extract financial details."
    }
    
    try:
        # We use a short timeout so it doesn't slow down our reply
        requests.post(url, json=payload, timeout=2)
        print(f"✅ Reported to GUVI: {session_id}")
    except Exception as e:
        print(f"⚠️ Callback Failed: {e}")

def process_scam_interaction(request_data):
    try:
        # 1. Prepare History for Llama 3
        # We format the 'conversationHistory' so the AI knows what happened before.
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for msg in request_data.conversationHistory:
            role = "assistant" if msg.sender == "agent" else "user"
            messages.append({"role": role, "content": msg.text})
            
        # Add the latest message
        messages.append({"role": "user", "content": request_data.message.text})

        # 2. Get AI Response
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        sarla_reply = completion.choices[0].message.content

        # 3. Extract Intelligence from the Scammer's latest message
        current_intel = extract_intel(request_data.message.text)

        # 4. SEND MANDATORY CALLBACK (Background Task)
        # We send this every time to ensure we don't miss the requirement
        total_msgs = len(request_data.conversationHistory) + 1
        send_guvi_callback(request_data.sessionId, total_msgs, current_intel)

        # 5. Return strict format (Section 8)
        return {
            "status": "success",
            "reply": sarla_reply
        }

    except Exception as e:
        return {"status": "error", "reply": "Beta, my internet is not working properly."}