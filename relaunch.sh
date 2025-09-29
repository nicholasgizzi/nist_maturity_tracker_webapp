#!/bin/bash
set -e

echo "🚀 NIST Tracker Relaunch Script"
echo "==============================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Stop any existing processes
print_info "Stopping existing services..."

# Kill any existing Flask processes on ports 5001/5002
pkill -f "flask run --port 5001" 2>/dev/null || true
pkill -f "flask run --port 5002" 2>/dev/null || true

# Stop Docker containers
docker-compose down 2>/dev/null || true

print_status "Existing services stopped"

# Database management - PRODUCTION SAFE
print_info "Checking database configuration..."

if [ -f "instance/nist_tracker.db" ]; then
    print_status "Found existing database - preserving production data"
    print_info "Creating backup before proceeding..."

    # Create backup with cleanup
    mkdir -p backups
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    # Clean old backups (keep only 1 revision)
    if ls backups/nist_tracker_*.db 1> /dev/null 2>&1; then
        ls -t backups/nist_tracker_*.db | tail -n +2 | xargs rm -f 2>/dev/null || true
    fi

    # Create new backup
    cp instance/nist_tracker.db "backups/nist_tracker_${TIMESTAMP}.db"
    print_status "Database backed up as: backups/nist_tracker_${TIMESTAMP}.db"
    print_info "Database will NOT be overwritten to protect production data"
elif [ -f "production_data.db" ]; then
    print_info "No existing database found, copying from production_data.db..."
    cp production_data.db instance/nist_tracker.db
    print_status "Production database copied to instance directory"
else
    print_warning "No database found - application will create new empty database"
    print_warning "Run database migrations if needed: flask db upgrade"
fi

print_info "Database check complete - production data preserved"

# Start development server
print_info "Starting development server on port 5001..."
source venv/bin/activate
export FLASK_ENV=development
nohup flask run --port 5001 > dev_server.log 2>&1 &
DEV_PID=$!
sleep 3

# Check if development server started
if curl -s http://localhost:5001/auth/login > /dev/null; then
    print_status "Development server running at http://localhost:5001"
else
    print_warning "Development server may have issues - check dev_server.log"
fi

# Start containerized version
print_info "Starting containerized version on port 5002..."
docker-compose up -d > /dev/null 2>&1

# Wait for container to be ready
sleep 5

# Check if containerized version started
if curl -s http://localhost:5002/auth/login > /dev/null; then
    print_status "Containerized version running at http://localhost:5002"
else
    print_warning "Containerized version may have issues - check docker logs"
fi

echo ""
echo "🌐 Access your application:"
echo "   • Development:  http://localhost:5001"
echo "   • Containerized: http://localhost:5002"
echo ""
echo "📝 Useful commands:"
echo "   • Check logs:     tail -f dev_server.log"
echo "   • Docker logs:    docker-compose logs -f"
echo "   • Stop all:       docker-compose down && pkill -f 'flask run'"
echo ""
print_status "NIST Tracker is ready for executive presentation!"