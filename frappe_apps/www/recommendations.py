"""
Recommendations page - Shows AI-powered course recommendations
This page hosts a Vue.js component
"""

import frappe
from frappe import _


def get_context(context):
    """Build context for the recommendations page"""
    context.no_cache = 1
    context.title = _("Course Recommendations")

    # Pass user info to the page
    if frappe.session.user != "Guest":
        context.user = frappe.session.user
        context.full_name = frappe.db.get_value("User", frappe.session.user, "full_name")
    else:
        # Redirect guests to login
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    return context
