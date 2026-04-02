# API Reference — Mining AI System

Base URL: `http://localhost:5000`

## Authentication
No authentication required (development mode). For production, add JWT or API key middleware.

---

## Sensor Endpoints

### GET `/api/all-data`
Returns all live dashboard data in one call.

**Response:**
```json
{
  "sensorData": [...],
  "alerts": [...],
  "equipment": [...],
  "routes": [...],
  "hazardZones": [...],
  "robots": [...],
  "maintenanceScore": 85
}
```

### GET `/api/sensors/history?limit=100`
Returns the last N sensor readings from the database.

### GET `/api/sensors/latest`
Returns the single most recent sensor reading.

---

## Alert Endpoints

### GET `/api/alerts/history?limit=50`
Returns last N alerts ordered by timestamp descending.

### PUT `/api/alerts/resolve/<alert_id>`
Marks an alert as resolved and sets `resolved_at` timestamp.

---

## Equipment Endpoints

### GET `/api/equipment`
Returns all equipment records.

### POST `/api/equipment`
Creates a new equipment record.

**Body:**
```json
{
  "equipment_name": "Drill-06",
  "equipment_type": "Drill",
  "status": "Good",
  "health_score": 100
}
```

### GET `/api/equipment/<id>`
Returns a single equipment record.

### PUT `/api/equipment/<id>`
Updates equipment status, health score, or operating hours.

### DELETE `/api/equipment/<id>`
Removes equipment record.

---

## Maintenance Endpoints

### POST `/api/maintenance/record`
Logs a maintenance activity and resets equipment health to 100.

**Body:**
```json
{
  "equipment_id": 1,
  "maintenance_type": "Preventive",
  "description": "Oil change and belt inspection",
  "cost": 450.00,
  "duration_hours": 3.5,
  "technician_name": "Ravi Kumar"
}
```

### GET `/api/maintenance/equipment/<id>`
Returns maintenance history for a specific piece of equipment.

---

## Route Endpoints

### POST `/api/routes/record`
Records route performance data.

**Body:**
```json
{
  "route_name": "Route A",
  "distance": 450,
  "time_taken": 28,
  "efficiency": 92,
  "fuel_consumed": 85.5
}
```

### GET `/api/routes/history?limit=50`
Returns route optimization history.

---

## Hazard Zone Endpoints

### GET `/api/hazard-zones`
Returns all registered hazard zones.

### POST `/api/hazard-zones`
Creates a new hazard zone record.

**Body:**
```json
{
  "zone_name": "Tunnel-9A",
  "x_coordinate": 200,
  "y_coordinate": 350,
  "risk_level": 78,
  "zone_type": "Gas Buildup"
}
```

---

## Robot Endpoints

### GET `/api/robots`
Returns all robot statuses.

### POST `/api/robots`
Creates or updates a robot record (upsert by `robot_id`).

**Body:**
```json
{
  "robot_id": "R-004",
  "location": "Level-3",
  "battery_level": 92,
  "current_task": "Inspection",
  "status": "Active"
}
```

### PUT `/api/robots/<robot_id>`
Updates a specific robot's status.

### DELETE `/api/robots/<robot_id>`
Removes a robot record.

---

## System Endpoints

### GET `/api/statistics`
Returns aggregate system metrics:
- Total/critical/warning alert counts
- Average health score, vibration, temperature, gas
- Equipment and maintenance record counts

### GET `/api/health-check`
Returns database connectivity and server status.

---

## WebSocket Events

**Namespace:** `/mining`

Connect: `const socket = io('http://localhost:5000/mining')`

| Event | Direction | Data |
|-------|-----------|------|
| `connect` | Client → Server | — |
| `connection_response` | Server → Client | `{ status: "Connected to Mining AI System" }` |
| `sensor_update` | Server → Client | `{ sensorData, alerts, maintenance_score }` |

Updates are broadcast every 2 seconds.
