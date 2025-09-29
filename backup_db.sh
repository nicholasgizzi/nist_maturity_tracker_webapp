#!/bin/bash
set -e

echo "🗄️  NIST Tracker Database Backup Script"
echo "======================================="

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

# Create backups directory if it doesn't exist
mkdir -p backups

# Clean up old backups first (keep only 1 revision = remove all existing)
print_info "Cleaning up old backups (keeping only 1 revision)..."

# Remove ALL existing nist_tracker backups
if ls backups/nist_tracker_*.db 1> /dev/null 2>&1; then
    NIST_COUNT=$(ls backups/nist_tracker_*.db | wc -l)
    rm -f backups/nist_tracker_*.db
    print_info "Removed $NIST_COUNT old nist_tracker backup(s)"
fi

# Remove ALL existing production_data backups
if ls backups/production_data_*.db 1> /dev/null 2>&1; then
    PROD_COUNT=$(ls backups/production_data_*.db | wc -l)
    rm -f backups/production_data_*.db
    print_info "Removed $PROD_COUNT old production_data backup(s)"
fi

# Get current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup current instance database
if [ -f "instance/nist_tracker.db" ]; then
    print_info "Backing up current instance database..."
    cp instance/nist_tracker.db "backups/nist_tracker_${TIMESTAMP}.db"
    print_status "Instance database backed up as: backups/nist_tracker_${TIMESTAMP}.db"
else
    print_warning "No instance database found to backup"
fi

# Backup production database if it exists
if [ -f "production_data.db" ]; then
    print_info "Backing up production database..."
    cp production_data.db "backups/production_data_${TIMESTAMP}.db"
    print_status "Production database backed up as: backups/production_data_${TIMESTAMP}.db"
else
    print_warning "No production database found to backup"
fi

# Show current backups (should only be 1 of each)
print_info "Current database backups:"
ls -la backups/ 2>/dev/null || echo "No backups directory found"

echo ""
print_status "Database backup complete - only most recent revision kept!"
echo ""
echo "📋 Available operations:"
echo "   • Restore instance DB:    cp backups/nist_tracker_*.db instance/nist_tracker.db"
echo "   • Restore production DB:  cp backups/production_data_*.db production_data.db"
echo "   • View backups:           ls -la backups/"