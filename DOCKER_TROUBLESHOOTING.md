# Docker Deployment Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Missing CSS Files (404 errors for .css bundles)

**Symptoms:**
- Browser shows 404 errors for files like `website.bundle.*.css` and `lms.bundle.*.css`
- Pages load but styling is broken
- Browser console shows "Failed to load resource: the server responded with a status of 404"

**Root Cause:**
Assets weren't built during Docker deployment, or the build process failed silently.

**Solution:**

**Option A: Quick Fix (Rebuild assets in running container)**

```bash
# SSH to your CentOS server
ssh user@your-centos-server
cd /opt/lms-deployment/frappe_apps/docker

# Run the fix script
curl -O https://raw.githubusercontent.com/th3ee-pop/frappe_apps/main/fix_docker_assets.sh
chmod +x fix_docker_assets.sh
./fix_docker_assets.sh
```

**Option B: Manual Fix**

```bash
# SSH to your server
ssh user@your-centos-server
cd /opt/lms-deployment/frappe_apps/docker

# Enter the backend container
docker compose exec backend bash

# Build all assets
bench build --force

# This will take 2-5 minutes and should show:
# ✔ Application Assets Linked
# Done in Xs

# Exit the container
exit

# Clear browser cache and reload
```

**Option C: Rebuild Docker image with assets**

If the issue persists, the Docker build process might need modification.

---

### Issue 2: Chat Widget Not Appearing on /lms Pages

**Symptoms:**
- Chat widget works on `/hello` but not on `/lms/*` paths
- Works fine on localhost but not on Docker deployment
- No JavaScript errors in console

**Root Cause:**
The LMS frontend in the Docker image is pulled directly from GitHub and doesn't include our custom chat widget modification. On localhost, you manually edited `apps/lms/frontend/index.html` and rebuilt, but this change isn't in the Docker image.

**Solution:**

**Step 1: Patch LMS in Docker Container**

```bash
# SSH to your server
ssh user@your-centos-server
cd /opt/lms-deployment/frappe_apps/docker

# Enter backend container
docker compose exec backend bash

# Navigate to LMS frontend
cd apps/lms/frontend

# Check if already patched
grep -q "chat-widget.css" index.html && echo "Already patched" || echo "Needs patching"

# If needs patching, apply the patch
sed -i.bak '/twitter:description/,/<\/head>/ {
    /<\/head>/ i\
\t\t<!-- AI Chat Widget from frappe_apps -->\
\t\t<link type="text/css" rel="stylesheet" href="/assets/frappe_apps/css/chat-widget.css">\
\t\t<script type="text/javascript" src="/assets/frappe_apps/js/chat-widget.js" defer></script>
}' index.html

# Verify the patch
grep "chat-widget" index.html
# Should show 2 lines with the CSS and JS tags

# Rebuild LMS frontend (this takes 15-20 seconds)
yarn build

# Exit container
exit

# Clear cache
docker compose exec backend bench clear-cache
docker compose exec backend bench clear-website-cache
```

**Step 2: Verify**

```bash
# Test from server
curl http://localhost:8080/lms | grep chat-widget
# Should return 2 lines if successful

# Test from your browser
# Open http://YOUR_SERVER_IP:8080/lms
# Hard refresh with Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
# Purple chat button should appear in bottom-right
```

**Step 3: Make it Permanent**

To avoid repeating this after every deployment, add this to your deployment workflow:

```bash
# Create a post-deployment script
cat > docker/post-deploy.sh <<'EOF'
#!/bin/bash
echo "Running post-deployment setup..."

# Patch LMS if needed
docker compose exec backend bash -c "
  cd apps/lms/frontend && \
  if ! grep -q 'chat-widget.css' index.html; then \
    sed -i.bak '/twitter:description/,/<\/head>/ { /<\/head>/ i\\
\t\t<!-- AI Chat Widget from frappe_apps -->\\
\t\t<link type=\"text/css\" rel=\"stylesheet\" href=\"/assets/frappe_apps/css/chat-widget.css\">\\
\t\t<script type=\"text/javascript\" src=\"/assets/frappe_apps/js/chat-widget.js\" defer></script>
}' index.html && \
    yarn build && \
    echo '✓ LMS patched and rebuilt'
  fi
"

# Clear caches
docker compose exec backend bench clear-cache
docker compose exec backend bench clear-website-cache

echo "✅ Post-deployment complete"
EOF

chmod +x docker/post-deploy.sh
```

Then run it after each deployment:
```bash
cd /opt/lms-deployment/frappe_apps/docker
sudo ./deploy.sh
sudo ./post-deploy.sh
```

---

## Diagnostic Commands

### Check if Assets Exist

```bash
# Check Frappe assets
docker compose exec backend ls -la sites/assets/frappe/dist/css/

# Check LMS assets
docker compose exec backend ls -la sites/assets/lms/dist/css/

# Check frappe_apps assets
docker compose exec backend ls -la sites/assets/frappe_apps/css/

# All should show files without errors
```

### Check if Chat Widget is Patched

```bash
# Check LMS index.html for chat widget
docker compose exec backend grep "chat-widget" apps/lms/frontend/index.html

# Check built LMS HTML
docker compose exec backend grep "chat-widget" lms/public/frontend/index.html

# Both should return 2 lines
```

### Check Logs for Errors

```bash
# Check backend logs
docker compose logs backend --tail 100

# Check for build errors
docker compose logs backend | grep -i "error\|failed"

# Check for 404s
docker compose logs frontend | grep "404"
```

### Verify Services are Running

```bash
# All services should be "Up"
docker compose ps

# Expected output:
# backend      Up
# frontend     Up
# mariadb      Up
# redis-*      Up
# websocket    Up
# scheduler    Up
# queue-*      Up
```

---

## Complete Rebuild (Nuclear Option)

If nothing works, rebuild everything:

```bash
cd /opt/lms-deployment/frappe_apps/docker

# Stop and remove everything (WARNING: This deletes data!)
docker compose down -v

# Pull latest image
docker compose pull

# Start services
docker compose up -d

# Wait for services to start (check with: docker compose ps)
sleep 30

# Create site and install apps
docker compose run --rm create-site

# Build assets
docker compose exec backend bench build --force

# Patch LMS
docker compose exec backend bash -c "
  cd apps/lms/frontend && \
  sed -i.bak '/twitter:description/,/<\/head>/ { /<\/head>/ i\\
\t\t<!-- AI Chat Widget from frappe_apps -->\\
\t\t<link type=\"text/css\" rel=\"stylesheet\" href=\"/assets/frappe_apps/css/chat-widget.css\">\\
\t\t<script type=\"text/javascript\" src=\"/assets/frappe_apps/js/chat-widget.js\" defer></script>
}' index.html && \
  yarn build
"

# Clear caches
docker compose exec backend bench clear-cache
```

---

## Browser Issues

### Clear Browser Cache

**Chrome/Edge:**
1. Press F12 to open DevTools
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

**Firefox:**
1. Press Ctrl+Shift+Delete
2. Select "Cached Web Content"
3. Click "Clear Now"

**Safari:**
1. Preferences → Advanced → Show Develop menu
2. Develop → Empty Caches
3. Cmd+R to reload

### Disable Browser Cache (for testing)

1. Open DevTools (F12)
2. Go to Network tab
3. Check "Disable cache"
4. Keep DevTools open while testing

---

## Prevention

### Automated Post-Deployment

Add this to your `docker/deploy.sh` at the end:

```bash
# At the end of deploy.sh, add:
echo "Running post-deployment setup..."

# Build assets
docker compose exec backend bench build --force

# Patch LMS if needed
docker compose exec backend bash -c "
  cd apps/lms/frontend && \
  if ! grep -q 'chat-widget.css' index.html; then \
    # Apply patch
    sed -i.bak '/twitter:description/,/<\/head>/ { /<\/head>/ i\\
\t\t<!-- AI Chat Widget -->\\
\t\t<link type=\"text/css\" rel=\"stylesheet\" href=\"/assets/frappe_apps/css/chat-widget.css\">\\
\t\t<script type=\"text/javascript\" src=\"/assets/frappe_apps/js/chat-widget.js\" defer></script>
}' index.html
    # Rebuild
    yarn build
  fi
"

# Clear caches
docker compose exec backend bench clear-cache
docker compose exec backend bench clear-website-cache

echo "✅ Deployment complete!"
```

---

## Quick Reference

### Most Common Fix

```bash
# 90% of issues are solved by:
cd /opt/lms-deployment/frappe_apps/docker

# Rebuild assets
docker compose exec backend bench build --force

# Patch and rebuild LMS
docker compose exec backend bash -c "cd apps/lms/frontend && \
  grep -q chat-widget index.html || \
  (sed -i.bak '/twitter:description/,/<\/head>/ { /<\/head>/ i\\
\t\t<link type=\"text/css\" rel=\"stylesheet\" href=\"/assets/frappe_apps/css/chat-widget.css\">\\
\t\t<script type=\"text/javascript\" src=\"/assets/frappe_apps/js/chat-widget.js\" defer></script>
}' index.html && yarn build)"

# Clear caches
docker compose exec backend bench clear-cache
```

Then hard-refresh your browser (Ctrl+Shift+R).

---

## Getting Help

If issues persist:

1. **Collect logs:**
   ```bash
   docker compose logs backend > backend.log
   docker compose logs frontend > frontend.log
   docker compose ps > services.txt
   ```

2. **Check browser console:**
   - Press F12
   - Go to Console tab
   - Screenshot any errors (red text)

3. **Create GitHub issue:**
   - https://github.com/th3ee-pop/frappe_apps/issues
   - Include logs and screenshots
   - Describe steps taken

---

## Success Indicators

When everything works, you should see:

1. **No 404 errors** in browser console
2. **Purple chat button** in bottom-right on all pages
3. **Proper styling** on all pages (Frappe and LMS)
4. **Chat widget opens** when clicking the button
5. **Chat responds** to messages

Test URLs:
- http://YOUR_SERVER:8080/hello (should show styled page with chat)
- http://YOUR_SERVER:8080/lms (should show LMS with chat)
- http://YOUR_SERVER:8080/api/method/frappe_apps.api.hello (should return JSON)
