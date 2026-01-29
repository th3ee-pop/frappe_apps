import frappe
from frappe import _
import os


def after_install():
    """
    Called after frappe_apps is installed
    Automatically patches LMS to include chat widget
    """
    patch_lms_frontend()


def patch_lms_frontend():
    """
    Patch LMS frontend index.html to include chat widget
    This allows the widget to appear on LMS SPA pages
    """
    try:
        # Get the path to LMS frontend index.html
        bench_path = frappe.utils.get_bench_path()
        lms_index_path = os.path.join(bench_path, "apps", "lms", "frontend", "index.html")

        if not os.path.exists(lms_index_path):
            frappe.log_error(f"LMS index.html not found at {lms_index_path}", "Chat Widget Installation")
            return

        # Read the current content
        with open(lms_index_path, 'r') as f:
            content = f.read()

        # Check if already patched
        if "frappe_apps/css/chat-widget.css" in content:
            print("✓ LMS frontend already patched with chat widget")
            return

        # Add chat widget scripts before </head>
        chat_widget_code = '''		<!-- AI Chat Widget from frappe_apps -->
		<link type="text/css" rel="stylesheet" href="/assets/frappe_apps/css/chat-widget.css">
		<script type="text/javascript" src="/assets/frappe_apps/js/chat-widget.js" defer></script>
	</head>'''

        # Replace </head> with our patched version
        if "</head>" in content:
            patched_content = content.replace("</head>", chat_widget_code)

            # Write back to file
            with open(lms_index_path, 'w') as f:
                f.write(patched_content)

            print("✓ LMS frontend patched successfully with chat widget")
            print(f"  Modified: {lms_index_path}")
            print("  Note: Run 'cd apps/lms/frontend && yarn build' to rebuild LMS frontend")
        else:
            frappe.log_error("Could not find </head> tag in LMS index.html", "Chat Widget Installation")

    except Exception as e:
        frappe.log_error(f"Failed to patch LMS frontend: {str(e)}", "Chat Widget Installation")
        print(f"✗ Failed to patch LMS frontend: {str(e)}")
