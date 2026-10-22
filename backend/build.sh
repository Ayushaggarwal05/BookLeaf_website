#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "==> Running database migrations..."
python -m alembic -c backend/alembic.ini upgrade head

echo "==> Running idempotent dataset seed and demo account provisioning..."
python backend/seed.py

echo "==> Build completed successfully!"
