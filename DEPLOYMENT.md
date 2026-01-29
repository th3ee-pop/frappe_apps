# Deployment Guide - Frappe LMS with frappe_apps

This guide explains how to deploy your Frappe LMS + frappe_apps to a CentOS server using Docker.

## Prerequisites

- CentOS 7/8 server with 2GB+ RAM
- Docker and Docker Compose installed
- Domain name (optional, can use IP)
- GitHub account with access to repository

## Quick Start (Local Testing)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/th3ee-pop/frappe_apps.git
   cd frappe_apps/docker
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

3. **Run deployment**:
   ```bash
   ./deploy.sh
   ```

4. **Access your site**:
   - Main Site: http://localhost:8080
   - Hello World: http://localhost:8080/hello
   - API Test: http://localhost:8080/api/method/frappe_apps.api.hello

## Production Deployment on CentOS

### Step 1: Install Docker

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional)
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Step 3: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/th3ee-pop/frappe_apps.git
cd frappe_apps/docker
```

### Step 4: Configure Environment

```bash
# Copy example env file
sudo cp .env.example .env

# Edit configuration
sudo nano .env
```

Example `.env` for production:
```bash
SITE_NAME=lms.yourdomain.com
ADMIN_PASSWORD=your_secure_password_here
DB_ROOT_PASSWORD=your_db_password_here
HTTP_PORT=8080
IMAGE_TAG=latest
```

### Step 5: Configure Firewall

```bash
# Open HTTP port
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# Or for port 80:
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

### Step 6: Deploy

```bash
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### Step 7: Verify Deployment

```bash
# Check running containers
docker compose ps

# View logs
docker compose logs -f

# Test endpoints
curl http://localhost:8080/hello
curl http://localhost:8080/api/method/frappe_apps.api.hello
```

## Updating the Deployment

When you push new code to GitHub, it triggers a Docker build. To update your server:

```bash
cd /opt/frappe_apps/docker

# Pull latest code
sudo git pull origin main  # or develop

# Pull latest image
sudo docker compose pull

# Restart services
sudo docker compose down
sudo docker compose up -d

# Or use the deploy script
sudo ./deploy.sh
```

## CI/CD Workflow

1. **Develop locally**:
   ```bash
   cd /Users/chensirui/my-bench/apps/frappe_apps
   # Make changes to code
   ```

2. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin develop  # or main
   ```

3. **GitHub Actions automatically**:
   - Runs tests (CI workflow)
   - Builds Docker image (Build workflow)
   - Pushes to GitHub Container Registry

4. **Update server**:
   ```bash
   ssh user@your-centos-server
   cd /opt/frappe_apps/docker
   sudo ./deploy.sh
   ```

## Troubleshooting

### Check logs
```bash
docker compose logs backend
docker compose logs mariadb
docker compose logs -f  # Follow all logs
```

### Restart services
```bash
docker compose restart backend
docker compose restart  # Restart all
```

### Reset everything
```bash
docker compose down -v  # Remove volumes (DANGER: deletes data!)
docker compose up -d
```

### Enter container shell
```bash
docker compose exec backend bash
```

### Database access
```bash
docker compose exec mariadb mysql -u root -p
# Enter DB_ROOT_PASSWORD when prompted
```

## Useful Commands

```bash
# View running containers
docker compose ps

# Stop all services
docker compose down

# Start all services
docker compose up -d

# View resource usage
docker stats

# Backup database
docker compose exec backend bench --site lms.localhost backup

# Restore database
docker compose exec backend bench --site lms.localhost restore /path/to/backup.sql
```

## Security Recommendations

1. **Change default passwords** in `.env`
2. **Use strong passwords** for admin and database
3. **Configure SSL/TLS** with nginx reverse proxy
4. **Enable firewall** and only open necessary ports
5. **Regular backups** of database and files
6. **Keep Docker images updated**

## Monitoring

### Health checks
```bash
# Check if site is responding
curl http://localhost:8080/api/method/ping

# Check custom API
curl http://localhost:8080/api/method/frappe_apps.api.hello
```

### Resource monitoring
```bash
# Real-time stats
docker stats

# Disk usage
docker system df
```

## Advanced Configuration

### Using a Custom Domain

1. Point your domain DNS to server IP
2. Update `.env`:
   ```bash
   SITE_NAME=lms.yourdomain.com
   ```
3. Redeploy:
   ```bash
   ./deploy.sh
   ```

### SSL with Let's Encrypt

Add nginx reverse proxy in front:

```yaml
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
```

## Support

For issues:
- Check logs: `docker compose logs -f`
- GitHub Issues: https://github.com/th3ee-pop/frappe_apps/issues
- Frappe Forum: https://discuss.frappe.io
