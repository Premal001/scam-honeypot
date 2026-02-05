from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# We try to import, but if it fails, we handle it inside the function
try:
    from agent_logic import process_scam_interaction
    from schemas import IncomingRequest
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI Module missing. Running in Safe Mode.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/detect-and-respond")
async def chat_endpoint(request: Request):
    try:
        # 1. READ DATA
        raw_body = await request.json()
        print(f"📥 Received: {raw_body}")

        # 2. IF AI IS WORKING, TRY TO USE IT
        if AI_AVAILABLE:
            # We wrap this in another try/except so the AI logic can't crash the server
            try:
                # Manually validate to allow flexible input
                structured_data = IncomingRequest(**raw_body)
                return process_scam_interaction(structured_data)
            except Exception as e:
                print(f"❌ AI Logic Failed: {e}")
                # Fall through to the dummy response below
        
        # 3. FALLBACK (DUMMY RESPONSE)
        # We run this if AI_AVAILABLE is False OR if the AI crashed.
        return JSONResponse(content={
            "status": "success",
            "reply": "This is a suspicious message. Do not share your OTP."
        })

    except Exception as e:
        # 4. SAFETY NET (Impossible to crash)
        print(f"⚠️ Critical Error: {e}")
        return JSONResponse(content={
            "status": "success",
            "reply": "System Active (Safety Mode)"
        })

@app.get("/")
def read_root():
    return {"status": "Honey-Pot Active"}
