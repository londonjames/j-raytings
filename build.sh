#!/bin/bash
# Build script for Vercel deployment
# Builds the frontend app

cd frontend
npm install
npm run build
cd ..

