# Database Schema — Mining AI System

Database: `mining_ai_db` (MySQL 8.0)

## Tables

### `sensor_readings`
Stores all sensor readings captured every 2 seconds.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | Primary key |
| timestamp | DATETIME (indexed) | YES | UTC reading time |
| vibration | FLOAT | YES | Vibration level |
| temperature | FLOAT | YES | Temperature °C |
| pressure | FLOAT | YES | Pressure kPa |
| gas_level | FLOAT | YES | Gas level ppm |
| dust_level | FLOAT | YES | Dust mg/m³ |
| health_score | FLOAT | YES | Calculated score (0–100) |

### `alerts`
Stores all triggered alerts and their resolution status.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | — |
| timestamp | DATETIME (indexed) | YES | When alert fired |
| alert_type | VARCHAR(50) | YES | `danger` or `warning` |
| message | VARCHAR(255) | YES | Human-readable message |
| severity | VARCHAR(50) | YES | `CRITICAL` or `WARNING` |
| equipment_id | VARCHAR(50) | YES | Source equipment ID |
| resolved | BOOLEAN | YES | Default: FALSE |
| resolved_at | DATETIME | YES | Nullable until resolved |

### `equipment`
Master registry of all mining equipment.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | — |
| equipment_name | VARCHAR(100) UNIQUE | NO | e.g. "Drill-01" |
| equipment_type | VARCHAR(50) | YES | Drill, Conveyor, etc. |
| status | VARCHAR(50) | YES | Good / Fair / Critical |
| health_score | FLOAT | YES | Default: 100 |
| last_maintenance | DATETIME | YES | Last service timestamp |
| total_operating_hours | FLOAT | YES | Default: 0 |
| created_at | DATETIME | YES | Record creation time |
| updated_at | DATETIME | YES | Auto-updated on change |

### `maintenance_records`
History of all maintenance activities per equipment.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | — |
| equipment_id | INT (FK → equipment.id) | YES | Linked equipment |
| maintenance_date | DATETIME (indexed) | YES | When maintenance done |
| maintenance_type | VARCHAR(100) | YES | Preventive / Corrective |
| description | VARCHAR(255) | YES | Work description |
| cost | FLOAT | YES | Cost in currency |
| duration_hours | FLOAT | YES | Time taken |
| technician_name | VARCHAR(100) | YES | Who performed it |

### `route_records`
Route efficiency history for mine path optimization.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | — |
| timestamp | DATETIME (indexed) | YES | When recorded |
| route_name | VARCHAR(50) | YES | e.g. "Route A" |
| distance | FLOAT | YES | Distance in meters |
| time_taken | FLOAT | YES | Time in minutes |
| efficiency | FLOAT | YES | Score 0–100 |
| fuel_consumed | FLOAT | YES | Liters |

### `hazard_zones`
Map coordinates and risk levels for hazardous areas.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | — |
| zone_name | VARCHAR(100) UNIQUE | YES | e.g. "Tunnel-7B" |
| x_coordinate | FLOAT | YES | Map X position |
| y_coordinate | FLOAT | YES | Map Y position |
| risk_level | FLOAT | YES | 0–100 |
| zone_type | VARCHAR(50) | YES | Gas / Dust / Structural |
| last_checked | DATETIME | YES | Last inspection time |

### `robot_status`
Current and historical status of autonomous robots.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INT AUTO_INCREMENT PK | NO | — |
| robot_id | VARCHAR(50) UNIQUE (indexed) | NO | e.g. "R-001" |
| location | VARCHAR(100) | YES | Current tunnel/zone |
| battery_level | FLOAT | YES | 0–100% |
| current_task | VARCHAR(100) | YES | Mapping / Inspection / Charging |
| status | VARCHAR(50) | YES | Active / Idle / Charging |
| last_update | DATETIME | YES | Last ping timestamp |

## Relationships

```
equipment (1) ──── (many) maintenance_records
```

All other tables are independent (no foreign keys beyond the above).
