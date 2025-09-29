#!/bin/bash
set -e

echo "🚀 NIST Tracker Deployment Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Check if production config exists
if [ ! -f "instance/config.py" ]; then
    print_warning "No production config found. Creating from example..."
    cp instance/config.example.py instance/config.py
    print_warning "Please edit instance/config.py with your production settings before continuing."
    exit 1
fi

print_status "Production config found"

# Database protection and backup - PRODUCTION SAFE
echo ""
echo "🗄️  Database Management"
echo "======================"

if [ -f "instance/nist_tracker.db" ]; then
    print_status "Found existing production database - creating backup..."

    # Create backup with cleanup
    mkdir -p backups
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    # Clean old backups (keep only 1 revision = remove all existing)
    if ls backups/nist_tracker_*.db 1> /dev/null 2>&1; then
        NIST_COUNT=$(ls backups/nist_tracker_*.db | wc -l)
        rm -f backups/nist_tracker_*.db
        echo "  Removed $NIST_COUNT old backup(s)"
    fi

    # Create new backup
    cp instance/nist_tracker.db "backups/nist_tracker_${TIMESTAMP}.db"
    print_status "Production database backed up as: backups/nist_tracker_${TIMESTAMP}.db"
    print_warning "Existing database preserved - no data loss"
else
    print_warning "No existing database found - fresh deployment"
fi

echo ""

# Build the Docker image
print_status "Building Docker image..."
docker-compose build

# Run database migrations
print_status "Running database migrations..."
docker-compose run --rm nist-tracker flask db upgrade

# Seed the database if needed
if [ "$1" == "--seed" ]; then
    print_status "Seeding database..."
    docker-compose run --rm nist-tracker python seed.py
fi

# Start the services
print_status "Starting services..."
docker-compose up -d

# Wait for the app to be ready
print_status "Waiting for application to start..."
sleep 10

# Check if the app is running
if curl -f http://localhost:5000/auth/login > /dev/null 2>&1; then
    print_status "Application is running successfully!"
    echo ""
    echo "🌐 Access your application at:"
    echo "   • http://localhost:5000 (direct Flask app)"
    echo "   • http://localhost (via nginx - if enabled)"
    echo ""
    echo "📊 Check container status:"
    echo "   docker-compose ps"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
else
    print_error "Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi