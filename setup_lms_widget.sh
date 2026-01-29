#!/bin/bash
# Setup script to patch LMS frontend with chat widget
# This script should be run after installing frappe_apps

set -e

echo "🔧 Patching LMS frontend for chat widget integration..."

# Find the LMS frontend directory
if [ -d "../lms/frontend" ]; then
    LMS_FRONTEND="../lms/frontend"
elif [ -d "apps/lms/frontend" ]; then
    LMS_FRONTEND="apps/lms/frontend"
elif [ -d "/home/frappe/frappe-bench/apps/lms/frontend" ]; then
    LMS_FRONTEND="/home/frappe/frappe-bench/apps/lms/frontend"
else
    echo "❌ Could not find LMS frontend directory"
    exit 1
fi

INDEX_FILE="$LMS_FRONTEND/index.html"

if [ ! -f "$INDEX_FILE" ]; then
    echo "❌ LMS index.html not found at $INDEX_FILE"
    exit 1
fi

# Check if already patched
if grep -q "frappe_apps/css/chat-widget.css" "$INDEX_FILE"; then
    echo "✓ LMS frontend already patched with chat widget"
    exit 0
fi

# Backup original file
cp "$INDEX_FILE" "$INDEX_FILE.backup"
echo "✓ Created backup: $INDEX_FILE.backup"

# Patch the file
# Find the line with twitter:description and add our scripts after it
sed -i.tmp '/twitter:description/,/<\/head>/ {
    /<\/head>/ i\
		<!-- AI Chat Widget from frappe_apps -->\
		<link type="text/css" rel="stylesheet" href="/assets/frappe_apps/css/chat-widget.css">\
		<script type="text/javascript" src="/assets/frappe_apps/js/chat-widget.js" defer></script>
}' "$INDEX_FILE"

rm -f "$INDEX_FILE.tmp"

echo "✓ LMS index.html patched successfully"

# Rebuild LMS frontend if yarn is available
if command -v yarn &> /dev/null; then
    echo "🔨 Rebuilding LMS frontend..."
    cd "$LMS_FRONTEND"
    yarn build
    echo "✓ LMS frontend rebuilt successfully"
else
    echo "⚠️  yarn not found. Please manually rebuild LMS frontend:"
    echo "   cd $LMS_FRONTEND && yarn build"
fi

echo "✅ Chat widget integration complete!"
