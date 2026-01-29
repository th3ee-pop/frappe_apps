#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Frappe LMS + Apps Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env file with your configuration!${NC}"
    exit 1
fi

# Load environment variables
source .env

# Pull latest images
echo -e "${YELLOW}Pulling latest Docker images...${NC}"
docker compose pull

# Stop existing services
echo -e "${YELLOW}Stopping existing services...${NC}"
docker compose down

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker compose up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Run configurator
echo -e "${YELLOW}Running configurator...${NC}"
docker compose run --rm configurator

# Create site if needed
echo -e "${YELLOW}Creating/updating site...${NC}"
docker compose run --rm create-site

# Show status
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Site URL: http://localhost:${HTTP_PORT:-8080}${NC}"
echo -e "${GREEN}Hello World: http://localhost:${HTTP_PORT:-8080}/hello${NC}"
echo -e "${GREEN}API Test: http://localhost:${HTTP_PORT:-8080}/api/method/frappe_apps.api.hello${NC}"
echo ""
echo -e "${YELLOW}View logs:${NC} docker compose logs -f"
echo -e "${YELLOW}Stop services:${NC} docker compose down"
echo -e "${YELLOW}Restart services:${NC} docker compose restart"
echo ""

# Show running containers
docker compose ps
