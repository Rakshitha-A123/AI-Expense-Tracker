# 💰 Real-Time Expense Tracker

## 📘 Overview
The **Expense Tracker** is a smart real-time expense management system that automatically records bank transactions from your SMS inbox.  
It uses:
- 📱 **MacroDroid** (Android app) to capture incoming SMS messages  
- ⚡ **FastAPI Backend** to process and store the transaction data  
- 🌐 **Streamlit Frontend** to display transactions, totals, and charts live  

---

## 🚀 Features
- 🔄 Real-time SMS-based transaction updates  
- 📊 Visual expense tracking with interactive charts  
- 🧠 Automatic extraction of transaction details using regex  
- 📧 Email alerts when spending exceeds a set limit  
- 🔐 Simple login interface  
- 💻 WebSocket integration for live data sync between backend and frontend  

---

## 🛠️ Tech Stack
| Component | Technology |
|------------|-------------|
| Frontend | Streamlit |
| Backend | FastAPI + WebSocket |
| Data Handling | JSON |
| Automation | MacroDroid (Android) |
| Visualization | Plotly |
| Email Alerts | Gmail SMTP |
