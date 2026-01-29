# Frappe Apps - Learning Tutor Bot (edubot)

Custom Frappe app that extends [Frappe LMS](https://github.com/frappe/lms) with AI-powered learning assistance.

## 🎯 What This Deploys

This repository deploys a **complete LMS system** including:

1. **Frappe Framework** (v15.x) - Full-stack backend framework
2. **Frappe LMS** (v2.44.0) - Complete learning management system
3. **frappe_apps** (v0.0.1) - Your custom extensions (this repo)

All bundled into a single Docker image: `ghcr.io/th3ee-pop/frappe_apps:latest`

## 📚 Quick Links

- **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Deploy in 5 minutes
- **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️ - System architecture overview
- **[DEPLOYMENT.md](DEPLOYMENT.md)** 📖 - Detailed deployment guide

## Features

- 🎉 **Hello World Demo**: Simple web page and API endpoints to verify deployment
- 🤖 **AI Learning Assistant**: (Coming soon) Intelligent tutoring bot
- 🔄 **CI/CD Pipeline**: Automated testing and Docker builds via GitHub Actions
- 🐳 **Docker Ready**: Production-ready Docker deployment

## Quick Start

### Local Development

1. **Install the app**:
   ```bash
   cd $PATH_TO_YOUR_BENCH
   bench get-app https://github.com/th3ee-pop/frappe_apps --branch develop
   bench --site your-site install-app frappe_apps
   ```

2. **Access Hello World**:
   - Web Page: http://localhost:8000/hello
   - API: http://localhost:8000/api/method/frappe_apps.api.hello

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick deploy with Docker**:
```bash
cd docker
cp .env.example .env
# Edit .env with your settings
./deploy.sh
```

## Project Structure

```
frappe_apps/
├── frappe_apps/
│   ├── www/                    # Web pages
│   │   ├── hello.py           # Hello World page logic
│   │   └── hello.html         # Hello World template
│   ├── api.py                 # API endpoints
│   ├── edubot/                # AI bot module (in development)
│   └── hooks.py               # Frappe hooks configuration
├── docker/                     # Docker deployment files
│   ├── docker-compose.yml     # Production compose file
│   ├── .env.example           # Environment template
│   └── deploy.sh              # Deployment script
├── .github/workflows/         # CI/CD workflows
│   ├── ci.yml                 # Server tests
│   ├── linters.yml            # Code quality
│   └── build.yml              # Docker image build
└── DEPLOYMENT.md              # Deployment guide
```

## API Endpoints

### Public Endpoints

- `GET /hello` - Hello World web page
- `GET /api/method/frappe_apps.api.hello` - Public API (no auth)

### Authenticated Endpoints

- `GET /api/method/frappe_apps.api.hello_authenticated` - Returns user info (requires login)

## Development Workflow

### 1. Make Changes

```bash
cd apps/frappe_apps
# Edit code
```

### 2. Test Locally

```bash
bench --site your-site clear-cache
bench --site your-site run-tests --app frappe_apps
```

### 3. Commit and Push

```bash
git add .
git commit -m "feat: add new feature"
git push origin develop
```

### 4. GitHub Actions Automatically:
- ✅ Runs tests
- ✅ Checks code quality
- ✅ Builds Docker image
- ✅ Pushes to GitHub Container Registry

### 5. Deploy to Server

```bash
ssh user@your-server
cd /opt/frappe_apps/docker
./deploy.sh
```

## CI/CD Pipeline

### Workflows

1. **CI (ci.yml)**: Runs on every push/PR
   - Installs Frappe bench
   - Installs LMS and frappe_apps
   - Runs test suite

2. **Linters (linters.yml)**: Code quality checks
   - Runs pre-commit hooks
   - Python linting with ruff
   - JavaScript linting with eslint

3. **Build (build.yml)**: Docker image build
   - Builds multi-platform image
   - Pushes to ghcr.io
   - Tags: `latest`, `develop`, or version tag

### Docker Images

Images are available at:
```
ghcr.io/th3ee-pop/frappe_apps:latest
ghcr.io/th3ee-pop/frappe_apps:develop
```

Pull the latest image:
```bash
docker pull ghcr.io/th3ee-pop/frappe_apps:latest
```

## Contributing

This app uses `pre-commit` for code formatting and linting.

### Setup Pre-commit

```bash
cd apps/frappe_apps
pre-commit install
```

### Tools Used

- **ruff**: Python linting and formatting
- **eslint**: JavaScript linting
- **prettier**: Code formatting
- **pyupgrade**: Python syntax upgrades

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: bug fix
docs: documentation
test: add tests
chore: maintenance
```

## Testing

### Run Tests

```bash
# All tests
bench --site your-site run-tests --app frappe_apps

# Specific module
bench --site your-site run-tests --module frappe_apps.api
```

### Test Deployment Locally

```bash
cd docker
cp .env.example .env
docker compose up -d
# Access at http://localhost:8080/hello
```

## License

MIT License - see [license.txt](license.txt)
