# AI CP Disaster – AI Disaster Social Response Analyzer

An AI-powered disaster analysis and emergency-response prototype.

## Project Overview

This project analyzes disaster-related images and news reports, verifies information, identifies locations, and generates emergency resource recommendations for verified reports.

## Run Locally

### Requirements
- Python 3.11
- MongoDB running at `127.0.0.1:27017`
- Project virtual environment (`.venv311`)
- Required AI model files

### Terminal 1 — Backend

From the project folder, open PowerShell:

```powershell
Set-Location "YOUR_PROJECT_FOLDER"
.\.venv311\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Backend: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### Terminal 2 — Frontend

Open a second PowerShell window:

```powershell
Set-Location "YOUR_PROJECT_FOLDER"
py -3.11 -m http.server 5501 --directory frontend
```

### Open the application

`http://127.0.0.1:5501/splash.html`

Replace `YOUR_PROJECT_FOLDER` with the path where you extracted the project.

## Resource Requests and Batch Analytics

The resource form saves request details to MongoDB. The admin dashboard lists those requests and exports them as CSV for Excel.

The Big Data Batch Analytics section uses MongoDB aggregation pipelines to summarize saved disaster analyses and resource requests by disaster, location, and resource type.

This is a local batch-processing prototype. It does not collect social-media streams or use HDFS, Hadoop/MapReduce, Kafka, or Spark, and it does not forecast future risk.

## Technology Stack

- Frontend: HTML5, CSS, JavaScript
- Backend: Python, FastAPI
- Disaster image classification: TensorFlow/Keras
- News evidence and location extraction: Google News RSS and NLP integrations
- Database: MongoDB
- Batch analytics: MongoDB aggregation pipelines
- Location display: Google Maps search links

Flutter Web, Hadoop/HDFS, MapReduce, Kafka, Spark, and predictive risk analysis are not implemented in this repository.