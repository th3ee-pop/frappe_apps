import frappe
from frappe import _
import time

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

@frappe.whitelist()
def send_chat_message(message, context=None):
    """
    Handle chat messages from the AI assistant widget

    Args:
        message (str): User's message
        context (dict): Optional context about current page (course, lesson, etc.)

    Returns:
        dict: AI response with message and metadata
    """
    # Get current user info
    user = frappe.session.user
    user_name = frappe.db.get_value("User", user, "full_name") or user

    # Simulate AI processing (replace with actual AI integration later)
    time.sleep(0.5)  # Simulate thinking time

    # Simple response logic (to be replaced with AI provider)
    message_lower = message.lower()

    if "hello" in message_lower or "hi" in message_lower:
        response_text = f"Hello {user_name}! I'm your learning assistant. How can I help you today?"
    elif "course" in message_lower:
        response_text = "I can help you with course information, progress tracking, and learning recommendations. What would you like to know?"
    elif "help" in message_lower:
        response_text = "I'm here to assist you with:\n- Course navigation and content\n- Learning progress and achievements\n- Assignment and quiz help\n- General LMS questions\n\nWhat would you like help with?"
    else:
        response_text = f"I received your message: '{message}'. This is a demo response. AI integration coming soon!"

    return {
        "success": True,
        "message": response_text,
        "user": user,
        "timestamp": frappe.utils.now(),
        "context": context
    }
