import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def hello():
    """Simple Hello World API endpoint"""
    return {
        "message": "Hello World from frappe_apps API!",
        "app": "frappe_apps",
        "version": frappe.get_attr("frappe_apps.__version__"),
        "user": frappe.session.user,
        "timestamp": frappe.utils.now(),
        "status": "success"
    }

@frappe.whitelist()
def hello_authenticated():
    """Hello World API that requires authentication"""
    return {
        "message": f"Hello {frappe.session.user}!",
        "user_info": {
            "email": frappe.session.user,
            "full_name": frappe.db.get_value("User", frappe.session.user, "full_name"),
        },
        "timestamp": frappe.utils.now(),
        "status": "authenticated"
    }
