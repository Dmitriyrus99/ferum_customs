app_name = "jwt_auth"
app_title = "JWT Auth"
app_publisher = "Your Name"
app_description = "JWT Authentication for Frappe"
app_email = "your@email.com"
app_license = "MIT"

override_whitelisted_methods = {
    "frappe.core.doctype.user.user.get_qr_code_secret_for_user": "jwt_auth.api.get_qr_code_secret_for_user",
    "frappe.core.doctype.user.user.confirm_otp": "jwt_auth.api.confirm_otp"
}

api_endpoint_methods = {
    "/api/method/jwt_auth.api.login": {
        "post": True
    }
}

