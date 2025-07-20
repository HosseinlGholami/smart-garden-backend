# Smart Garden System Setup Guide

## Overview
This smart garden system has been refactored to use real database data instead of mock data. The garden selection is now integrated into the navigation bar with role-based access controls.

## Quick Setup

### 1. Create Seed Data
Run the following command to create the necessary seed data including the Haj-Ebi garden and test users:

```bash
# Using Docker Compose
docker compose exec app python manage.py create_seed_data

# Or if running locally
python manage.py create_seed_data
```

This command will create:
- ✅ Admin user: `admin@admin.com` (password: `admin`) - Manager role
- ✅ Staff user: `staff@admin.com` (password: `staff123`) - Staff role  
- ✅ Haj-Ebi garden with proper access permissions
- ✅ 4 valves for the garden
- ✅ Power and pump records
- ✅ Sample schedules
- ✅ System logs
- ✅ Water usage data
- ✅ Power consumption data

### 2. Login and Use
1. Navigate to the frontend application
2. Login with either:
   - **Manager**: `admin@admin.com` / `admin` (can switch gardens)
   - **Staff**: `staff@admin.com` / `staff123` (fixed to assigned garden)
3. The garden selector is now in the sidebar (desktop) or mobile header
4. All dashboard data is specific to the selected garden

## Changes Made

### Frontend Changes
- ❌ Removed all mock data logic
- ❌ Removed dashboard-level garden selection
- ✅ Garden selector moved to navbar/sidebar
- ✅ Added Garden Context for state management
- ✅ Role-based garden selection restrictions
- ✅ API calls now always use real backend
- ✅ All data is garden-specific

### Backend Changes
- ✅ All API endpoints now require garden_id parameter
- ✅ Proper permission checking for garden access
- ✅ Garden-specific data filtering
- ✅ System status, power, and pump are garden-specific

### Role-Based Access Control
- **Admin/Manager**: Can select between multiple gardens if they have access
- **Staff**: Automatically assigned to their first available garden, cannot change
- **Visual Indicators**: Role badges show user's access level for each garden

## Navigation & Garden Selection

### Desktop (Sidebar)
- Garden selector appears at the top of the sidebar
- Shows current garden with role indicator
- Dropdown available for admin/manager users
- Staff users see a non-interactive display with explanation

### Mobile (Header)
- Garden selector appears below the main header
- Compact design optimized for mobile screens
- Same role-based restrictions apply

## User Roles & Permissions

- **Admin**: Full access to garden management and controls
- **Manager**: Can control garden operations and view all data  
- **Staff**: Can view and operate garden components, fixed garden assignment

### Garden Selection Behavior:
- **Admin/Manager with multiple gardens**: Interactive dropdown selector
- **Admin/Manager with one garden**: Non-interactive display (no dropdown)
- **Staff users**: Always assigned to first available garden, cannot change

## API Endpoints

All major endpoints now require a `garden_id` parameter:

- `GET /api/garden/valves/?garden_id=1` - Get valves for a garden
- `GET /api/garden/system/?garden_id=1` - Get system status
- `GET /api/garden/power/?garden_id=1` - Get power status
- `GET /api/garden/pump/?garden_id=1` - Get pump status
- `GET /api/garden/logs/?garden_id=1` - Get system logs
- `GET /api/garden/schedules/?garden_id=1` - Get schedules

## Current Setup

After running the seed data command, you'll have:

🏡 **Garden**: Haj-Ebi  
📍 **Location**: Haj-Ebi Farm, Northern Section  
👤 **Manager User**: admin@admin.com (can select gardens)  
👤 **Staff User**: staff@admin.com (fixed to Haj-Ebi)  
🚰 **Valves**: 4 valves with different durations  
📅 **Schedules**: 3 sample schedules (2 active, 1 inactive)  
📊 **Data**: Recent logs, usage data, and power consumption  

The system now provides a streamlined navigation experience with proper role-based access controls! 