import imaplib
import email
from email.header import decode_header
import re
import pandas as pd
from datetime import datetime

def fetch_sms_emails():
    # Login to Gmail
    username = "rakshi.a2005@gmail.com"
    password = "vhyv isqf nzaj msmy"  # use App Password (not normal password)
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    # Search for recent forwarded SMS
    status, messages = mail.search(None, '(FROM "smsforwarder@yourphone.com")')
    messages = messages[0].split()

    data = []
    for msg in messages[-5:]:  # get last 5 messages
        _, msg_data = mail.fetch(msg, "(RFC822)")
        msg_content = email.message_from_bytes(msg_data[0][1])
        text = msg_content.get_payload(decode=True).decode(errors="ignore")

        # Extract ₹amount
        amount_match = re.search(r'₹\s?(\d+(?:\.\d{1,2})?)', text)
        amount = float(amount_match.group(1)) if amount_match else 0

        # Extract vendor
        vendor_match = re.search(r'at\s([A-Za-z0-9 ]+)', text)
        vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"

        data.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vendor": vendor,
            "amount": amount,
            "raw_message": text
        })

    mail.logout()
    return pd.DataFrame(data)
