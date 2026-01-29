import frappe

def get_context(context):
    """Context for hello.html template"""
    context.title = "Hello World - Frappe Apps"
    context.message = "Hello World from frappe_apps! 🎉"
    context.timestamp = frappe.utils.now()
    context.user = frappe.session.user
    return context
