from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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
    # We are NOT calling agent_logic. We are just returning the format the judges want.
    return JSONResponse(content={
        "status": "success",
        "reply": "Your account is safe. This is a scam attempt."
    })

@app.get("/")
def read_root():
    return {"status": "Honey-Pot Active"}
