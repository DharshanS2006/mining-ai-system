"""
Underground Mining AI System - Complete with MySQL Database Integration
Run: python main.py

MySQL Setup:
1. Create database: CREATE DATABASE mining_ai_db;
2. Update credentials in SQLALCHEMY_DATABASE_URI
3. pip install PyMySQL Flask-SQLAlchemy
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LinearRegression
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# FLASK APP & DATABASE SETUP
# ============================================================================

app = Flask(__name__, template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# MySQL Configuration
# IMPORTANT: Change these credentials to match your MySQL setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:password@localhost:3306/mining_ai_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'connect_args': {
        'connect_timeout': 10,
    }
}

db = SQLAlchemy(app)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class SensorReading(db.Model):
    """Store sensor readings over time"""
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    vibration = db.Column(db.Float)
    temperature = db.Column(db.Float)
    pressure = db.Column(db.Float)
    gas_level = db.Column(db.Float)
    dust_level = db.Column(db.Float)
    health_score = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'vibration': round(self.vibration, 2) if self.vibration is not None else None,
            'temperature': round(self.temperature, 2) if self.temperature is not None else None,
            'pressure': round(self.pressure, 2) if self.pressure is not None else None,
            'gas_level': round(self.gas_level, 2) if self.gas_level is not None else None,
            'dust_level': round(self.dust_level, 2) if self.dust_level is not None else None,
            'health_score': round(self.health_score, 2) if self.health_score is not None else None
        }

class Alert(db.Model):
    """Store alert history"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    alert_type = db.Column(db.String(50))
    message = db.Column(db.String(255))
    severity = db.Column(db.String(50))
    equipment_id = db.Column(db.String(50))
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'equipment_id': self.equipment_id,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class Equipment(db.Model):
    """Store equipment information"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(100), unique=True, index=True)
    equipment_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    health_score = db.Column(db.Float, default=100)
    last_maintenance = db.Column(db.DateTime)
    total_operating_hours = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_name': self.equipment_name,
            'equipment_type': self.equipment_type,
            'status': self.status,
            'health_score': self.health_score,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'total_operating_hours': self.total_operating_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MaintenanceRecord(db.Model):
    """Store maintenance history"""
    __tablename__ = 'maintenance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    maintenance_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    maintenance_type = db.Column(db.String(100))
    description = db.Column(db.String(255))
    cost = db.Column(db.Float)
    duration_hours = db.Column(db.Float)
    technician_name = db.Column(db.String(100))
    
    equipment = db.relationship('Equipment', backref='maintenance_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'maintenance_date': self.maintenance_date.isoformat(),
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'cost': self.cost,
            'duration_hours': self.duration_hours,
            'technician_name': self.technician_name
        }

class RouteRecord(db.Model):
    """Store route optimization history"""
    __tablename__ = 'route_records'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    route_name = db.Column(db.String(50))
    distance = db.Column(db.Float)
    time_taken = db.Column(db.Float)
    efficiency = db.Column(db.Float)
    fuel_consumed = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'route_name': self.route_name,
            'distance': self.distance,
            'time_taken': self.time_taken,
            'efficiency': self.efficiency,
            'fuel_consumed': self.fuel_consumed
        }

class HazardZone(db.Model):
    """Store hazard zone data"""
    __tablename__ = 'hazard_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_name = db.Column(db.String(100), unique=True)
    x_coordinate = db.Column(db.Float)
    y_coordinate = db.Column(db.Float)
    risk_level = db.Column(db.Float)
    zone_type = db.Column(db.String(50))
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'zone_name': self.zone_name,
            'x_coordinate': self.x_coordinate,
            'y_coordinate': self.y_coordinate,
            'risk_level': self.risk_level,
            'zone_type': self.zone_type,
            'last_checked': self.last_checked.isoformat()
        }

class RobotStatus(db.Model):
    """Store robot status and tracking"""
    __tablename__ = 'robot_status'
    
    id = db.Column(db.Integer, primary_key=True)
    robot_id = db.Column(db.String(50), unique=True, index=True)
    location = db.Column(db.String(100))
    battery_level = db.Column(db.Float)
    current_task = db.Column(db.String(100))
    status = db.Column(db.String(50))
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'robot_id': self.robot_id,
            'location': self.location,
            'battery_level': self.battery_level,
            'current_task': self.current_task,
            'status': self.status,
            'last_update': self.last_update.isoformat()
        }

# ============================================================================
# PREDICTIVE MAINTENANCE SYSTEM
# ============================================================================

class PredictiveMaintenanceSystem:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        
    def generate_synthetic_data(self, n_samples=1000):
        np.random.seed(42)
        normal_data = {
            'vibration': np.random.normal(80, 15, n_samples),
            'temperature': np.random.normal(50, 10, n_samples),
            'pressure': np.random.normal(90, 8, n_samples),
            'operating_hours': np.random.uniform(0, 5000, n_samples),
            'failure': np.zeros(n_samples)
        }
        n_failures = int(n_samples * 0.2)
        failure_data = {
            'vibration': np.random.normal(130, 20, n_failures),
            'temperature': np.random.normal(70, 12, n_failures),
            'pressure': np.random.normal(75, 10, n_failures),
            'operating_hours': np.random.uniform(3000, 5000, n_failures),
            'failure': np.ones(n_failures)
        }
        df_normal = pd.DataFrame(normal_data)
        df_failure = pd.DataFrame(failure_data)
        df = pd.concat([df_normal, df_failure], ignore_index=True)
        return df.sample(frac=1).reset_index(drop=True)
    
    def train(self, data):
        X = data[['vibration', 'temperature', 'pressure', 'operating_hours']]
        y = data['failure']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.model.fit(X_train_scaled, y_train)
        self.anomaly_detector.fit(X_train_scaled)
        self.is_trained = True
        return self.model.score(X_test_scaled, y_test)

# ============================================================================
# HAZARD DETECTION SYSTEM
# ============================================================================

class HazardDetectionSystem:
    def __init__(self):
        self.gas_detector = SVC(kernel='rbf', probability=True, random_state=42)
        self.risk_classifier = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_hazard_data(self, n_samples=800):
        np.random.seed(42)
        safe_data = {
            'gas_level': np.random.normal(2, 1, int(n_samples * 0.7)),
            'dust_level': np.random.normal(20, 5, int(n_samples * 0.7)),
            'temperature': np.random.normal(45, 5, int(n_samples * 0.7)),
            'humidity': np.random.normal(60, 10, int(n_samples * 0.7)),
            'vibration': np.random.normal(30, 8, int(n_samples * 0.7)),
            'hazard': np.zeros(int(n_samples * 0.7))
        }
        hazard_data = {
            'gas_level': np.random.normal(8, 2, int(n_samples * 0.3)),
            'dust_level': np.random.normal(60, 15, int(n_samples * 0.3)),
            'temperature': np.random.normal(70, 10, int(n_samples * 0.3)),
            'humidity': np.random.normal(85, 8, int(n_samples * 0.3)),
            'vibration': np.random.normal(80, 20, int(n_samples * 0.3)),
            'hazard': np.ones(int(n_samples * 0.3))
        }
        df_safe = pd.DataFrame(safe_data)
        df_hazard = pd.DataFrame(hazard_data)
        df = pd.concat([df_safe, df_hazard], ignore_index=True)
        return df.sample(frac=1).reset_index(drop=True)
    
    def train(self, data):
        X = data[['gas_level', 'dust_level', 'temperature', 'humidity', 'vibration']]
        y = data['hazard']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.gas_detector.fit(X_train_scaled, y_train)
        self.risk_classifier.fit(X_train_scaled, y_train)
        self.is_trained = True
        return self.risk_classifier.score(X_test_scaled, y_test)

# ============================================================================
# MINE OPTIMIZATION SYSTEM
# ============================================================================

class MineOptimizationSystem:
    def __init__(self):
        self.production_model = LinearRegression()
        self.is_trained = False
        
    def generate_production_data(self, n_days=180):
        np.random.seed(42)
        data = {
            'equipment_count': np.random.randint(5, 15, n_days),
            'worker_hours': np.random.randint(100, 300, n_days),
            'downtime_hours': np.random.randint(0, 20, n_days),
            'fuel_consumed': np.random.uniform(500, 2000, n_days)
        }
        data['production_tons'] = (
            data['equipment_count'] * 50 +
            data['worker_hours'] * 0.8 -
            data['downtime_hours'] * 30 +
            np.random.normal(0, 100, n_days)
        )
        return pd.DataFrame(data)
    
    def train(self, data):
        X = data[['equipment_count', 'worker_hours', 'downtime_hours', 'fuel_consumed']]
        y = data['production_tons']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.production_model.fit(X_train, y_train)
        self.is_trained = True
        return self.production_model.score(X_test, y_test)

# ============================================================================
# INITIALIZE SYSTEMS
# ============================================================================

maintenance_sys = PredictiveMaintenanceSystem()
hazard_sys = HazardDetectionSystem()
optimization_sys = MineOptimizationSystem()

# ============================================================================
# REAL-TIME SENSOR SIMULATION
# ============================================================================

sensor_data_buffer = []
alerts_buffer = []

def simulate_sensors():
    while True:
        time.sleep(2)
        new_data = {
            'time': datetime.now().strftime('%H:%M:%S'),
            'vibration': float(np.random.normal(80, 15)),
            'temperature': float(np.random.normal(50, 10)),
            'pressure': float(np.random.normal(90, 8)),
            'gasLevel': float(np.random.normal(3, 1.5)),
            'dust': float(np.random.normal(25, 8))
        }
        
        sensor_data_buffer.append(new_data)
        if len(sensor_data_buffer) > 20:
            sensor_data_buffer.pop(0)
        
        maint_score = calculate_maintenance_score(new_data)
        
        with app.app_context():
            try:
                sensor_record = SensorReading(
                    vibration=new_data['vibration'],
                    temperature=new_data['temperature'],
                    pressure=new_data['pressure'],
                    gas_level=new_data['gasLevel'],
                    dust_level=new_data['dust'],
                    health_score=maint_score
                )
                db.session.add(sensor_record)
                db.session.commit()
            except Exception as e:
                print(f"Error saving sensor data: {e}")
                db.session.rollback()
        
        if new_data['gasLevel'] > 7:
            alert = {'type': 'danger', 'msg': 'High gas level detected!', 'time': new_data['time']}
            alerts_buffer.append(alert)
            
            with app.app_context():
                try:
                    alert_record = Alert(
                        alert_type='danger',
                        message='High gas level detected!',
                        severity='CRITICAL',
                        equipment_id='SYSTEM'
                    )
                    db.session.add(alert_record)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving alert: {e}")
                    db.session.rollback()
            
            if len(alerts_buffer) > 8:
                alerts_buffer.pop(0)
        
        if new_data['vibration'] > 120:
            alert = {'type': 'warning', 'msg': 'Abnormal vibration detected', 'time': new_data['time']}
            alerts_buffer.append(alert)
            
            with app.app_context():
                try:
                    alert_record = Alert(
                        alert_type='warning',
                        message='Abnormal vibration detected',
                        severity='WARNING',
                        equipment_id='SYSTEM'
                    )
                    db.session.add(alert_record)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving alert: {e}")
                    db.session.rollback()
            
            if len(alerts_buffer) > 8:
                alerts_buffer.pop(0)
        
        with app.app_context():
            socketio.emit('sensor_update', {
                'sensorData': sensor_data_buffer,
                'alerts': alerts_buffer,
                'maintenance_score': maint_score
            }, namespace='/mining')

def calculate_maintenance_score(latest_data):
    score = 100 - (
        (latest_data['vibration'] > 120 and 20 or 0) +
        (latest_data['temperature'] > 60 and 15 or 0) +
        (latest_data['gasLevel'] > 5 and 25 or 0)
    )
    return max(0, score)

# ============================================================================
# API ROUTES - FRONTEND
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/all-data', methods=['GET'])
def get_all_data():
    equipment = [
        {'name': 'Drill-01', 'health': max(50, 85 + np.random.normal(0, 5)), 'status': 'Good'},
        {'name': 'Conveyor-A', 'health': max(50, 72 + np.random.normal(0, 5)), 'status': 'Fair'},
        {'name': 'Ventilator-3', 'health': max(50, 45 + np.random.normal(0, 5)), 'status': 'Critical'},
        {'name': 'Hauler-02', 'health': max(50, 91 + np.random.normal(0, 5)), 'status': 'Good'},
        {'name': 'Loader-05', 'health': max(50, 68 + np.random.normal(0, 5)), 'status': 'Fair'}
    ]
    
    routes = [
        {'route': 'Route A', 'distance': 450, 'time': 28, 'efficiency': 92},
        {'route': 'Route B', 'distance': 520, 'time': 35, 'efficiency': 78},
        {'route': 'Route C', 'distance': 380, 'time': 22, 'efficiency': 95}
    ]
    
    hazard_zones = [
        {'zone': 'Tunnel-7B', 'x': 150, 'y': 220, 'risk': 85, 'type': 'Gas Buildup'},
        {'zone': 'Shaft-3A', 'x': 300, 'y': 180, 'risk': 65, 'type': 'Structural'},
        {'zone': 'Level-4C', 'x': 450, 'y': 320, 'risk': 45, 'type': 'Dust'},
        {'zone': 'Chamber-2', 'x': 250, 'y': 280, 'risk': 72, 'type': 'Temperature'}
    ]
    
    robots = [
        {'id': 'R-001', 'location': 'Tunnel-5', 'battery': max(10, 78 + np.random.normal(0, 3)), 'task': 'Mapping', 'status': 'Active'},
        {'id': 'R-002', 'location': 'Shaft-2', 'battery': max(10, 45 + np.random.normal(0, 3)), 'task': 'Inspection', 'status': 'Active'},
        {'id': 'R-003', 'location': 'Base', 'battery': min(100, 100 + np.random.normal(0, 2)), 'task': 'Charging', 'status': 'Idle'}
    ]
    
    return jsonify({
        'sensorData': sensor_data_buffer,
        'alerts': alerts_buffer,
        'equipment': equipment,
        'routes': routes,
        'hazardZones': hazard_zones,
        'robots': robots,
        'maintenanceScore': calculate_maintenance_score(sensor_data_buffer[-1]) if sensor_data_buffer else 0
    })

# ============================================================================
# DATABASE API ROUTES
# ============================================================================

@app.route('/api/sensors/history', methods=['GET'])
def get_sensor_history():
    try:
        limit = request.args.get('limit', 100, type=int)
        readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(limit).all()
        return jsonify([reading.to_dict() for reading in readings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/history', methods=['GET'])
def get_alerts_history():
    try:
        limit = request.args.get('limit', 50, type=int)
        alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(limit).all()
        return jsonify([alert.to_dict() for alert in alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipment', methods=['GET', 'POST'])
def manage_equipment():
    try:
        if request.method == 'POST':
            data = request.json
            equipment = Equipment(
                equipment_name=data['equipment_name'],
                equipment_type=data['equipment_type'],
                status=data.get('status', 'Good'),
                health_score=data.get('health_score', 100)
            )
            db.session.add(equipment)
            db.session.commit()
            return jsonify(equipment.to_dict()), 201
        equipment_list = Equipment.query.all()
        return jsonify([eq.to_dict() for eq in equipment_list])
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipment/<int:eq_id>', methods=['GET', 'PUT', 'DELETE'])
def get_equipment(eq_id):
    try:
        equipment = Equipment.query.get_or_404(eq_id)
        if request.method == 'PUT':
            data = request.json
            equipment.status = data.get('status', equipment.status)
            equipment.health_score = data.get('health_score', equipment.health_score)
            equipment.total_operating_hours = data.get('total_operating_hours', equipment.total_operating_hours)
            db.session.commit()
        elif request.method == 'DELETE':
            db.session.delete(equipment)
            db.session.commit()
            return jsonify({'message': 'Equipment deleted'}), 200
        return jsonify(equipment.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/maintenance/record', methods=['POST'])
def record_maintenance():
    try:
        data = request.json
        record = MaintenanceRecord(
            equipment_id=data['equipment_id'],
            maintenance_type=data['maintenance_type'],
            description=data.get('description', ''),
            cost=data.get('cost', 0),
            duration_hours=data.get('duration_hours', 0),
            technician_name=data.get('technician_name', 'Unknown')
        )
        db.session.add(record)
        equipment = Equipment.query.get(data['equipment_id'])
        if equipment:
            equipment.last_maintenance = datetime.utcnow()
            equipment.health_score = 100
        db.session.commit()
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/maintenance/equipment/<int:eq_id>', methods=['GET'])
def get_maintenance_history(eq_id):
    try:
        records = MaintenanceRecord.query.filter_by(equipment_id=eq_id).order_by(MaintenanceRecord.maintenance_date.desc()).all()
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/routes/record', methods=['POST'])
def record_route():
    try:
        data = request.json
        record = RouteRecord(
            route_name=data['route_name'],
            distance=data['distance'],
            time_taken=data['time_taken'],
            efficiency=data['efficiency'],
            fuel_consumed=data.get('fuel_consumed', 0)
        )
        db.session.add(record)
        db.session.commit()
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/routes/history', methods=['GET'])
def get_routes_history():
    try:
        limit = request.args.get('limit', 50, type=int)
        records = RouteRecord.query.order_by(RouteRecord.timestamp.desc()).limit(limit).all()
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hazard-zones', methods=['GET', 'POST'])
def manage_hazard_zones():
    try:
        if request.method == 'POST':
            data = request.json
            zone = HazardZone(
                zone_name=data['zone_name'],
                x_coordinate=data['x_coordinate'],
                y_coordinate=data['y_coordinate'],
                risk_level=data['risk_level'],
                zone_type=data['zone_type']
            )
            db.session.add(zone)
            db.session.commit()
            return jsonify(zone.to_dict()), 201
        zones = HazardZone.query.all()
        return jsonify([zone.to_dict() for zone in zones])
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/robots', methods=['GET', 'POST'])
def manage_robots():
    try:
        if request.method == 'POST':
            data = request.json
            robot = RobotStatus.query.filter_by(robot_id=data['robot_id']).first()
            if robot:
                robot.location = data.get('location', robot.location)
                robot.battery_level = data.get('battery_level', robot.battery_level)
                robot.current_task = data.get('current_task', robot.current_task)
                robot.status = data.get('status', robot.status)
                robot.last_update = datetime.utcnow()
            else:
                robot = RobotStatus(
                    robot_id=data['robot_id'],
                    location=data.get('location', 'Unknown'),
                    battery_level=data.get('battery_level', 100),
                    current_task=data.get('current_task', 'Idle'),
                    status=data.get('status', 'Idle')
                )
                db.session.add(robot)
            db.session.commit()
            return jsonify(robot.to_dict()), 201
        robots = RobotStatus.query.all()
        return jsonify([robot.to_dict() for robot in robots])
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/robots/<robot_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_single_robot(robot_id):
    try:
        robot = RobotStatus.query.filter_by(robot_id=robot_id).first_or_404()
        if request.method == 'PUT':
            data = request.json
            robot.location = data.get('location', robot.location)
            robot.battery_level = data.get('battery_level', robot.battery_level)
            robot.current_task = data.get('current_task', robot.current_task)
            robot.status = data.get('status', robot.status)
            robot.last_update = datetime.utcnow()
            db.session.commit()
        elif request.method == 'DELETE':
            db.session.delete(robot)
            db.session.commit()
            return jsonify({'message': 'Robot deleted'}), 200
        return jsonify(robot.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        total_alerts = Alert.query.count()
        critical_alerts = Alert.query.filter_by(severity='CRITICAL').count()
        warning_alerts = Alert.query.filter_by(severity='WARNING').count()
        avg_health = db.session.query(db.func.avg(SensorReading.health_score)).scalar() or 0
        total_sensors = SensorReading.query.count()
        equipment_count = Equipment.query.count()
        total_maintenance = MaintenanceRecord.query.count()
        avg_vibration = db.session.query(db.func.avg(SensorReading.vibration)).scalar() or 0
        avg_temperature = db.session.query(db.func.avg(SensorReading.temperature)).scalar() or 0
        avg_gas = db.session.query(db.func.avg(SensorReading.gas_level)).scalar() or 0
        return jsonify({
            'total_alerts': total_alerts,
            'critical_alerts': critical_alerts,
            'warning_alerts': warning_alerts,
            'average_health_score': round(avg_health, 2),
            'total_sensor_readings': total_sensors,
            'equipment_count': equipment_count,
            'total_maintenance_records': total_maintenance,
            'average_vibration': round(avg_vibration, 2),
            'average_temperature': round(avg_temperature, 2),
            'average_gas_level': round(avg_gas, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/resolve/<int:alert_id>', methods=['PUT'])
def resolve_alert(alert_id):
    try:
        alert = Alert.query.get_or_404(alert_id)
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
        return jsonify(alert.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensors/latest', methods=['GET'])
def get_latest_sensor():
    try:
        sensor = SensorReading.query.order_by(SensorReading.timestamp.desc()).first()
        if sensor:
            return jsonify(sensor.to_dict())
        return jsonify({'message': 'No sensor data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-check', methods=['GET'])
def health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect', namespace='/mining')
def handle_connect():
    print(f"✅ Client connected")
    emit('connection_response', {'status': 'Connected to Mining AI System'})

@socketio.on('disconnect', namespace='/mining')
def handle_disconnect():
    print(f"❌ Client disconnected")

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🏗️  UNDERGROUND MINING AI SYSTEM - WITH MYSQL DATABASE")
    print("=" * 70)
    
    with app.app_context():
        try:
            print("📊 Initializing MySQL Database...")
            db.create_all()
            print("✅ Database tables created successfully!")

            print("🚀 Training AI Systems...")
            maint_data = maintenance_sys.generate_synthetic_data()
            maintenance_sys.train(maint_data)

            hazard_data = hazard_sys.generate_hazard_data()
            hazard_sys.train(hazard_data)

            prod_data = optimization_sys.generate_production_data()
            optimization_sys.train(prod_data)

            print("✅ All systems trained and ready!\n")
        except Exception as e:
            print(f"❌ Database Error: {e}")
            print("⚠️  Make sure MySQL is running and credentials are correct!")
            exit(1)
    
    print(f"\n📡 Server running at: http://localhost:5000")
    print(f"🔄 Real-time WebSocket updates enabled")
    print("=" * 70 + "\n")
    
    sensor_thread = threading.Thread(target=simulate_sensors, daemon=True)
    sensor_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
