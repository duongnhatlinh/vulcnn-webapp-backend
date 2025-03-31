#!/bin/bash

# Start API service
cd backend/api && flask run --host=0.0.0.0 --port=5000 &

# Start microservices
cd ../normalization_service && flask run --host=0.0.0.0 --port=5001 &
cd ../pdg_generator_service && flask run --host=0.0.0.0 --port=5002 &
cd ../image_generator_service && flask run --host=0.0.0.0 --port=5003 &
cd ../prediction_service && flask run --host=0.0.0.0 --port=5004 &
cd ../results_service && flask run --host=0.0.0.0 --port=5005 &

# Wait for all background processes
wait