import frappe
from frappe import _


def inject_chat_widget():
    """
    Inject chat widget assets into every HTML response
    This ensures the widget appears on ALL pages including LMS SPA
    """
    if frappe.response.get("type") == "page":
        html = frappe.response.get("message", "")
        if isinstance(html, str) and "</head>" in html:
            # Inject CSS before </head>
            css_tag = '<link type="text/css" rel="stylesheet" href="/assets/frappe_apps/css/chat-widget.css">'
            js_tag = '<script type="text/javascript" src="/assets/frappe_apps/js/chat-widget.js"></script>'

            html = html.replace("</head>", f"{css_tag}\n{js_tag}\n</head>")
            frappe.response["message"] = html


def update_website_context(context):
    """
    Add chat widget assets to website context
    This hook is called for all website pages
    """
    # Add our CSS and JS to the page context
    if not context.get("head_html"):
        context["head_html"] = ""

    context["head_html"] += '''
        <link type="text/css" rel="stylesheet" href="/assets/frappe_apps/css/chat-widget.css">
        <script type="text/javascript" src="/assets/frappe_apps/js/chat-widget.js" defer></script>
    '''
