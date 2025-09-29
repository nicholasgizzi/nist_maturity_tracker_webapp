# Production Deployment Guide

## Database Safety Protocol

**🚨 IMPORTANT: Your production database is protected!**

The `relaunch.sh` script has been updated to **NEVER overwrite existing databases** to protect your production data.

### How Database Management Works:

1. **If `instance/nist_tracker.db` exists** (production scenario):
   - ✅ **Database is preserved** - no changes made
   - Script will NOT overwrite your production data
   - All existing risks, systems, and assessments remain intact

2. **If no `instance/nist_tracker.db` exists** (fresh deployment):
   - Script looks for `production_data.db` as backup source
   - Only copies if no existing database found

### Production Deployment Steps:

```bash
# 1. Backup your current database (recommended)
./backup_db.sh

# 2. Deploy updates safely
./relaunch.sh

# 3. Your production data remains intact!
```

### Manual Database Operations (if needed):

```bash
# Backup current database
./backup_db.sh

# Restore from specific backup
cp backups/nist_tracker_YYYYMMDD_HHMMSS.db instance/nist_tracker.db

# Force reset to production_data.db (CAUTION!)
cp production_data.db instance/nist_tracker.db
```

### Database Files:
- `instance/nist_tracker.db` - **Active production database** (protected)
- `production_data.db` - Backup/reference copy
- `backups/` - Timestamped database backups

## Container Deployment

Both development and containerized versions use the same database:
- **Development**: http://localhost:5001
- **Containerized**: http://localhost:5002

The containerized version mounts the `instance/` directory, so both share the same protected database.

## Executive Presentation Ready

Your NIST maturity tracker is now ready for executive presentations with:
- ✅ Professional dashboard styling
- ✅ Proper risk register sorting
- ✅ Production database protection
- ✅ Complete NIST framework assessment workflow