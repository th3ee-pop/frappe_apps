# Quick Start Guide - Deploy Complete Frappe LMS System

This guide gets your **complete LMS system** (Frappe + LMS + frappe_apps) running in minutes.

## What You're Deploying

Your Docker image includes:
- ✅ **Frappe Framework** (backend)
- ✅ **Frappe LMS** (full learning management system)
- ✅ **frappe_apps** (your custom extensions)

All in one image: `ghcr.io/th3ee-pop/frappe_apps:latest`

---

## Step 1: Wait for Docker Build ⏳

First, check if GitHub Actions finished building your Docker image:

**Check build status:**
```bash
open https://github.com/th3ee-pop/frappe_apps/actions
```

Wait for the **"Build Docker Image"** workflow to complete (green checkmark).
- First build: ~30-45 minutes
- Subsequent builds: ~10-15 minutes (cached)

---

## Step 2: Quick Local Test (Optional but Recommended)

Test on your Mac before deploying to CentOS:

```bash
# Navigate to docker directory
cd /Users/chensirui/my-bench/apps/frappe_apps/docker

# Create environment file
cp .env.example .env

# Deploy
./deploy.sh

# Wait ~2-3 minutes for services to start
```

**Access your site:**
- Main site: http://localhost:8080
- LMS interface: http://localhost:8080/lms
- Your Hello World: http://localhost:8080/hello
- API test: http://localhost:8080/api/method/frappe_apps.api.hello

**Login:**
- Username: `Administrator`
- Password: `admin`

**Stop when done:**
```bash
docker compose down
```

---

## Step 3: Deploy to CentOS Server

### 3.1 Install Docker on CentOS

SSH into your server:
```bash
ssh user@your-centos-server
```

Install Docker:
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker --version
docker compose version
```

### 3.2 Deploy Application

```bash
# Create deployment directory
sudo mkdir -p /opt/lms-deployment
cd /opt/lms-deployment

# Clone your repository
sudo git clone https://github.com/th3ee-pop/frappe_apps.git
cd frappe_apps/docker

# Create environment file
sudo cp .env.example .env

# IMPORTANT: Edit environment variables
sudo nano .env
```

**Edit .env file:**
```bash
# Change these values!
SITE_NAME=lms.yourdomain.com  # Or lms.localhost for testing
ADMIN_PASSWORD=your_strong_password_here
DB_ROOT_PASSWORD=your_db_password_here
HTTP_PORT=8080
IMAGE_TAG=latest
```

Save and exit (Ctrl+X, Y, Enter)

### 3.3 Configure Firewall

```bash
# Open port 8080
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-ports
```

### 3.4 Deploy!

```bash
# Make deploy script executable
sudo chmod +x deploy.sh

# Deploy
sudo ./deploy.sh
```

This will:
1. Pull the Docker image (includes Frappe + LMS + frappe_apps)
2. Start all services (database, redis, backend, workers)
3. Create the site
4. Install LMS and frappe_apps
5. Show access information

**Wait ~3-5 minutes** for everything to start.

---

## Step 4: Verify Deployment

### Check Services

```bash
# View running containers
docker compose ps

# All services should be "Up" or "Exited" (configurator/create-site)
```

### Check Logs

```bash
# Follow all logs
docker compose logs -f

# Check specific service
docker compose logs backend
docker compose logs mariadb

# Press Ctrl+C to exit
```

### Test Endpoints

```bash
# From the server
curl http://localhost:8080/hello
curl http://localhost:8080/api/method/frappe_apps.api.hello
curl http://localhost:8080/lms

# From your browser (replace YOUR_IP)
http://YOUR_SERVER_IP:8080/hello
http://YOUR_SERVER_IP:8080/lms
```

### Access Web Interface

**Open in browser:**
```
http://YOUR_SERVER_IP:8080
```

**Login:**
- Username: `Administrator`
- Password: (what you set in .env, default: `admin`)

### Test Complete System

1. **Frappe Framework:**
   - Go to Desk → Settings
   - Check installed apps: frappe, lms, frappe_apps ✅

2. **LMS Features:**
   - Go to `/lms`
   - Browse courses
   - Check modules: Courses, Batches, Certificates

3. **Your Custom Features:**
   - Go to `/hello`
   - Should see "Hello World from frappe_apps!" 🎉
   - Test API: `/api/method/frappe_apps.api.hello`

---

## Step 5: Update Deployment (Future Changes)

When you make changes and push to GitHub:

### On Your Mac (Development):

```bash
cd /Users/chensirui/my-bench/apps/frappe_apps

# Make changes to code
nano frappe_apps/www/hello.py

# Commit and push
git add .
git commit -m "feat: update hello page"
git push origin main
```

### Wait for Build:

GitHub Actions automatically:
1. Runs tests ✅
2. Builds new Docker image ✅
3. Pushes to ghcr.io ✅

Check: https://github.com/th3ee-pop/frappe_apps/actions

### On CentOS Server (Update):

```bash
ssh user@your-centos-server
cd /opt/lms-deployment/frappe_apps/docker

# Pull latest image and restart
sudo ./deploy.sh
```

Done! Your changes are live.

---

## Common Commands

### View Logs
```bash
docker compose logs -f
docker compose logs backend -f
```

### Restart Services
```bash
docker compose restart
docker compose restart backend
```

### Stop Everything
```bash
docker compose down
```

### Start Everything
```bash
docker compose up -d
```

### Enter Backend Container
```bash
docker compose exec backend bash

# Inside container:
bench --site lms.localhost list-apps
bench --site lms.localhost migrate
bench --site lms.localhost clear-cache
exit
```

### Backup Database
```bash
docker compose exec backend bench --site lms.localhost backup --with-files

# Backups saved in container's sites folder
# Copy to host:
docker cp $(docker compose ps -q backend):/home/frappe/frappe-bench/sites/lms.localhost/private/backups ./backups/
```

---

## Troubleshooting

### "Site not found" error:

```bash
# Check if site was created
docker compose exec backend bench list-sites

# If not listed, create it:
docker compose run --rm create-site
```

### "App not installed" error:

```bash
# Check installed apps
docker compose exec backend bench --site lms.localhost list-apps

# Should show: frappe, lms, frappe_apps
# If missing, install:
docker compose exec backend bench --site lms.localhost install-app lms
docker compose exec backend bench --site lms.localhost install-app frappe_apps
```

### Port 8080 already in use:

```bash
# Check what's using it
sudo lsof -i :8080

# Or change port in .env:
HTTP_PORT=8081
```

### Services not starting:

```bash
# Check detailed logs
docker compose logs mariadb
docker compose logs redis-cache

# Restart specific service
docker compose restart mariadb
```

### Complete reset (DANGER - deletes all data):

```bash
docker compose down -v
docker compose up -d
docker compose run --rm create-site
```

---

## Next Steps

1. ✅ Verify Hello World works
2. ✅ Explore LMS features
3. 🔄 Set up SSL/TLS (for production)
4. 🔄 Configure automated backups
5. 🔄 Add monitoring (Prometheus/Grafana)
6. 🔄 Develop your AI assistant features

---

## Security Checklist (Before Going Live)

- [ ] Change default admin password
- [ ] Change database root password
- [ ] Disable developer mode
- [ ] Set up SSL/TLS with Let's Encrypt
- [ ] Configure firewall (only allow 80, 443)
- [ ] Set up regular backups
- [ ] Enable fail2ban
- [ ] Review user permissions
- [ ] Set up monitoring/alerts

---

## Resources

- **Your Repository**: https://github.com/th3ee-pop/frappe_apps
- **GitHub Actions**: https://github.com/th3ee-pop/frappe_apps/actions
- **Frappe LMS Docs**: https://docs.frappe.io/learning
- **Frappe Framework**: https://frappeframework.com
- **Architecture Guide**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Full Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Support

**Issues?**
- Check logs: `docker compose logs -f`
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
- Open issue: https://github.com/th3ee-pop/frappe_apps/issues
- LMS community: https://discuss.frappe.io

---

**Ready to deploy? Start at Step 1! ☝️**
