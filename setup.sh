#!/bin/bash

# Create necessary directories
mkdir -p data/uploads
mkdir -p data/normalized
mkdir -p data/pdgs
mkdir -p data/images
mkdir -p data/reports

# Install Python requirements in each service
cd backend/api && pip install -r requirements.txt
cd ../normalization_service && pip install -r requirements.txt
cd ../pdg_generator_service && pip install -r requirements.txt
cd ../image_generator_service && pip install -r requirements.txt
cd ../prediction_service && pip install -r requirements.txt
cd ../results_service && pip install -r requirements.txt
cd ../..

# Initialize database
cd backend/api
python -c "from app import db; db.create_all()"