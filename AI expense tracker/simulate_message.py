import asyncio
import websockets
import json

async def send_transaction():
    uri = "ws://localhost:5000/ws"
    async with websockets.connect(uri) as websocket:
        new_tx = {
            "date": "2025-11-03 23:40",
            "vendor": "Zomato",
            "amount": 349.0,
            "category": "Food",
            "raw_message": "Dinner from Zomato ₹349"
        }
        await websocket.send(json.dumps(new_tx))
        print("✅ Sent new transaction to backend!")

asyncio.run(send_transaction())
