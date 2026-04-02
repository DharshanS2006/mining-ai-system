-- ============================================================
-- Underground Mining AI System - Database Initialization
-- Run: mysql -u root -p < scripts/init_db.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS mining_ai_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mining_ai_db;

-- Tables are auto-created by SQLAlchemy on first run.
-- This script sets up the database with proper character set.

-- Optional: Create a dedicated user for the app
-- CREATE USER 'mining_user'@'localhost' IDENTIFIED BY 'your_secure_password';
-- GRANT ALL PRIVILEGES ON mining_ai_db.* TO 'mining_user'@'localhost';
-- FLUSH PRIVILEGES;

SELECT 'Database mining_ai_db created successfully!' AS status;
