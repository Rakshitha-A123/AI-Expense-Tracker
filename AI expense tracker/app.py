import streamlit as st
import websockets
import asyncio
import json
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- EMAIL ALERT FUNCTION ----------------
def send_email_alert(subject, message):
    sender_email = "rakshi.a2005@gmail.com"
    app_password = "vhyv isqf nzaj msmy"  # use Gmail App Password
    receiver_email = "rakshi.a2005@gmail.com"

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)

        print("📧 Email alert sent successfully!")
    except Exception as e:
        print(f"⚠️ Error sending email: {e}")

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="💰 AI Expense Tracker", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "limit" not in st.session_state:
    st.session_state.limit = 0
if "transactions" not in st.session_state:
    st.session_state.transactions = []

st.title("💰 AI-Powered Real-Time Expense Tracker")

# --- LOGIN ---
if not st.session_state.logged_in:
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
        else:
            st.warning("Please enter both username and password.")
else:
    st.sidebar.success(f"👋 Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.transactions = []
        st.rerun()

    # --- LIMIT SETTING ---
    st.sidebar.header("⚙️ Settings")
    st.session_state.limit = st.sidebar.number_input(
        "💸 Set Monthly Limit (₹)", min_value=0, value=st.session_state.limit
    )

    st.markdown(f"### 📊 Current Limit: **₹{st.session_state.limit}**")

    # --- PARSE MESSAGES ---
    def process_message(message):
        try:
            data = json.loads(message)
            if isinstance(data, dict) and "amount" in data:
                return [data]
            elif isinstance(data, list):
                return data
            else:
                st.warning("⚠️ Unexpected message structure.")
                return []
        except json.JSONDecodeError:
            st.warning("⚠️ Invalid data format from backend.")
            return []

    async def get_latest_data():
        uri = "ws://10.65.9.116:5000/ws"

        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send("fetch")
                data = await websocket.recv()
                new_transactions = process_message(data)
                if new_transactions:
                    st.session_state.transactions.extend(new_transactions)
                    st.success("✅ New transaction received!")
        except Exception as e:
            st.error(f"⚠️ Could not fetch data: {e}")

    if st.button("🔄 Fetch Recent Data"):
        asyncio.run(get_latest_data())

    # --- DISPLAY TRANSACTIONS ---
    if st.session_state.transactions:
        df = pd.DataFrame(st.session_state.transactions)
        st.write("### 📋 Recent Transactions")
        st.dataframe(df)

        total = df["amount"].sum()
        st.markdown(f"### 💵 Total Spent: **₹{total}**")

        fig = px.bar(df, x="category", y="amount", title="Expense Summary by Category", color="category")
        st.plotly_chart(fig, use_container_width=True)

        if total > st.session_state.limit and st.session_state.limit > 0:
            st.error("🚨 You’ve exceeded your spending limit!")

            # --- Send email alert once ---
            if "alert_sent" not in st.session_state or not st.session_state.alert_sent:
                send_email_alert(
                    "🚨 Expense Limit Exceeded!",
                    f"Hi {st.session_state.username},\n\nYour spending of ₹{total} has exceeded your set limit of ₹{st.session_state.limit}.\n\nPlease review your expenses!"
                )
                st.session_state.alert_sent = True
        else:
            st.info(f"💡 Remaining: ₹{st.session_state.limit - total}")
            st.session_state.alert_sent = False
    else:
        st.info("⚠️ No transaction data yet.")
