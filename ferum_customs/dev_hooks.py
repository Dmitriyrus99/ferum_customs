"""Local development hooks for customizing Frappe/ERPNext behavior.

This file allows you to add overrides or additional hook definitions
specific to your local development environment. 

You can extend fixtures, define custom hooks for events, and more.

Example: To extend fixtures, uncomment and modify the line below:
fixtures = ["demo_fixture"]

You can also define custom hooks for events, such as:
doc_events = {
    "Your DocType": {
        "on_update": "path.to.your.method",
        "on_delete": "path.to.your.method"
    }
}

Make sure to implement the methods referenced in doc_events securely.
"""

# Example: extend fixtures
# fixtures = ["demo_fixture"]

# Example: define custom hooks
# doc_events = {
#     "Your DocType": {
#         "on_update": "path.to.your.method",
#         "on_delete": "path.to.your.method"
#     }
# }
