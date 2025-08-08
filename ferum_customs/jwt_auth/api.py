import frappe
import jwt
from datetime import datetime, timedelta

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        user = frappe.get_doc("User", usr)

        if user.two_factor_auth_enabled:
            return {"status": "2fa_required", "user": user.name}

        token = get_jwt(user)
        return {"status": "success", "token": token}

    except frappe.exceptions.AuthenticationError:
        frappe.local.response["http_status_code"] = 401
        return {"status": "error", "message": "Invalid credentials"}

@frappe.whitelist()
def get_qr_code_secret_for_user(user):
    user_doc = frappe.get_doc("User", user)
    return user_doc.get_qr_code_secret()

@frappe.whitelist()
def confirm_otp(user, otp):
    user_doc = frappe.get_doc("User", user)
    if user_doc.confirm_otp(otp):
        token = get_jwt(user_doc)
        return {"status": "success", "token": token}
    else:
        frappe.local.response["http_status_code"] = 401
        return {"status": "error", "message": "Invalid OTP"}

def get_jwt(user):
    payload = {
        "usr": user.name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, frappe.conf.get("app_secret_key"), algorithm="HS256")
