"""
Basic tests for Mining AI System
Run: pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_predictive_maintenance_training():
    """Test that the predictive maintenance model trains successfully"""
    from main import PredictiveMaintenanceSystem
    sys = PredictiveMaintenanceSystem()
    data = sys.generate_synthetic_data(n_samples=200)
    accuracy = sys.train(data)
    assert accuracy > 0.7, f"Expected accuracy > 0.7, got {accuracy}"
    assert sys.is_trained is True


def test_hazard_detection_training():
    """Test that the hazard detection model trains successfully"""
    from main import HazardDetectionSystem
    sys = HazardDetectionSystem()
    data = sys.generate_hazard_data(n_samples=200)
    accuracy = sys.train(data)
    assert accuracy > 0.7, f"Expected accuracy > 0.7, got {accuracy}"
    assert sys.is_trained is True


def test_mine_optimization_training():
    """Test that the mine optimization model trains successfully"""
    from main import MineOptimizationSystem
    sys = MineOptimizationSystem()
    data = sys.generate_production_data(n_days=60)
    score = sys.train(data)
    assert score > 0.5, f"Expected R² > 0.5, got {score}"
    assert sys.is_trained is True


def test_maintenance_score_calculation():
    """Test health score calculation logic"""
    from main import calculate_maintenance_score

    # Normal data - score should be 100
    normal_data = {'vibration': 80, 'temperature': 50, 'gasLevel': 3}
    assert calculate_maintenance_score(normal_data) == 100

    # High vibration - score should drop
    high_vib_data = {'vibration': 130, 'temperature': 50, 'gasLevel': 3}
    assert calculate_maintenance_score(high_vib_data) == 80

    # Critical gas - score should drop significantly
    high_gas_data = {'vibration': 80, 'temperature': 50, 'gasLevel': 8}
    assert calculate_maintenance_score(high_gas_data) == 75


def test_synthetic_data_shape():
    """Test that synthetic data has correct shape and columns"""
    from main import PredictiveMaintenanceSystem
    sys = PredictiveMaintenanceSystem()
    data = sys.generate_synthetic_data(n_samples=100)
    assert len(data) == 120  # 100 normal + 20 failure (20%)
    assert 'vibration' in data.columns
    assert 'temperature' in data.columns
    assert 'pressure' in data.columns
    assert 'failure' in data.columns
