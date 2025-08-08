import frappe

def send_telegram_notification(doc, method):
    if doc.priority == "Urgent":
        # Logic to send Telegram notification
        pass
