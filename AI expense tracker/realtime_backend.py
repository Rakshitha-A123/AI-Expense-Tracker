from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
import json, re, datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []
transactions = []  # store all received transactions


# 🔹 WebSocket Endpoint (for Streamlit)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print(f"🟢 New client connected. Total clients: {len(clients)}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"📩 Received from sender: {data}")

            if data == "fetch":
                await websocket.send_text(json.dumps(transactions))
            else:
                try:
                    transaction = json.loads(data)
                    if isinstance(transaction, dict) and "amount" in transaction:
                        transactions.append(transaction)
                        for client in clients:
                            await client.send_text(json.dumps([transaction]))
                except json.JSONDecodeError:
                    print("⚠️ Invalid JSON received.")
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("🔴 Client disconnected.")


# 🔹 SMS Endpoint (for MacroDroid)
@app.post("/sms")
async def receive_sms(request: Request):
    """Receive SMS from MacroDroid and convert to transaction format."""
    data = await request.json()
    print("📩 Received SMS:", data)

    message = data.get("message", "").strip()

    # 🧠 Extract amount (Rs.20.00 or ₹20.00)
    amount_match = re.search(r'(?:Rs\.?|₹)\s?(\d+(?:\.\d{1,2})?)', message, re.IGNORECASE)
    amount = float(amount_match.group(1)) if amount_match else 0.0

    # 🧠 Detect type (credited/debited)
    txn_type = "Debited" if re.search(r'\bdebited\b', message, re.IGNORECASE) else (
        "Credited" if re.search(r'\bcredited\b', message, re.IGNORECASE) else "Unknown"
    )

    # 🧠 Extract vendor or receiver name (after 'to' or 'from')
    vendor_match = re.search(r'\b(?:to|from)\s+([A-Za-z\s.&]+?)(?:\.|UPI|$)', message, re.IGNORECASE)
    vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"

    # 🧠 Extract date (like 23-06-25)
    date_match = re.search(r'on\s+(\d{2}-\d{2}-\d{2})', message)
    if date_match:
        date = datetime.datetime.strptime(date_match.group(1), "%d-%m-%y").strftime("%Y-%m-%d %H:%M")
    else:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # 🧠 Extract bank name (optional)
    bank_match = re.search(r'-([A-Za-z ]+)$', message)
    bank = bank_match.group(1).strip() if bank_match else "Unknown Bank"

    transaction = {
        "date": date,
        "vendor": vendor,
        "amount": amount,
        "type": txn_type,
        "bank": bank,
        "raw_message": message,
        "category": f"{txn_type} Transaction"
    }

    transactions.append(transaction)
    print(f"✅ Parsed transaction: {transaction}")

    # Broadcast to all connected Streamlit clients
    for client in clients:
        await client.send_text(json.dumps([transaction]))

    return {"status": "✅ SMS received and sent to Streamlit"}


@app.get("/")
def home():
    return {"message": "✅ Realtime backend running"}
