#!/bin/bash
# Fix missing assets and chat widget in Docker deployment

echo "🔧 Fixing Docker deployment issues..."

# Function to run commands in Docker container
docker_exec() {
    docker compose exec backend "$@"
}

# 1. Build all assets
echo "📦 Building Frappe and LMS assets..."
docker_exec bench build --force

# 2. Patch LMS frontend for chat widget
echo "🔧 Patching LMS frontend..."
docker_exec bash -c "cd apps/lms/frontend && \
    if ! grep -q 'chat-widget.css' index.html; then \
        sed -i.bak '/twitter:description/,/<\/head>/ { /<\/head>/ i\
\t\t<!-- AI Chat Widget from frappe_apps -->\
\t\t<link type=\"text/css\" rel=\"stylesheet\" href=\"/assets/frappe_apps/css/chat-widget.css\">\
\t\t<script type=\"text/javascript\" src=\"/assets/frappe_apps/js/chat-widget.js\" defer></script>
}' index.html && echo '✓ LMS index.html patched'; \
    else \
        echo '✓ LMS already patched'; \
    fi"

# 3. Rebuild LMS frontend
echo "🏗️  Rebuilding LMS frontend..."
docker_exec bash -c "cd apps/lms/frontend && yarn build"

# 4. Clear caches
echo "🧹 Clearing caches..."
docker_exec bench clear-cache
docker_exec bench clear-website-cache

# 5. Verify assets
echo "✅ Verifying assets..."
docker_exec ls -la sites/assets/frappe/dist/css/
docker_exec ls -la sites/assets/lms/dist/css/
docker_exec ls -la sites/assets/frappe_apps/css/

echo ""
echo "✅ Fix complete! Please refresh your browser with Ctrl+Shift+R"
echo ""
echo "Test URLs:"
echo "  - http://YOUR_SERVER_IP:8080/hello"
echo "  - http://YOUR_SERVER_IP:8080/lms"
