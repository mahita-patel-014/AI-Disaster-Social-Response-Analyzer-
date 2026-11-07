# AI CP Disaster

Disaster image analysis, news verification, and emergency-response prototype.

## Run locally

Requirements: Python 3.10 or 3.11, MongoDB running at `127.0.0.1:27017`, and the model files in this repository.

From the project root in PowerShell:

```powershell
Copy-Item .env.example .env
# Edit .env and set ADMIN_USERNAME, ADMIN_EMAIL, and a strong ADMIN_PASSWORD.
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

In a second PowerShell window:

```powershell
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500/splash.html`. API docs: `http://127.0.0.1:8000/docs`.

## Resource requests and batch analytics

The resource form saves request details to MongoDB. The admin dashboard lists those requests and exports them as CSV for Excel. The form does not email or otherwise send the request to an external recipient.

The final admin section, **Big Data Batch Analytics**, runs MongoDB aggregation pipelines over saved disaster analyses and resource requests. It summarizes reports by disaster and location and resource needs by disaster, location, and resource type. This is a local batch-processing prototype over records already in the application's database.

This prototype does not collect social-media streams, use HDFS, Hadoop/MapReduce, Kafka, or Spark, or forecast future risk. Its current data volume is limited to the records saved in MongoDB; it demonstrates the aggregation workflow, not a production Big Data deployment.

## Current technology coverage

- Frontend: HTML5, CSS, and JavaScript.
- Backend: Python and FastAPI REST APIs.
- Disaster image classification: TensorFlow/Keras model.
- News evidence and location extraction: Google News RSS and NLP model integrations.
- Database: MongoDB for users, analysis history, and resource requests.
- Batch analytics prototype: MongoDB aggregation pipelines surfaced in the admin dashboard.
- Location display: Google Maps search links; no Google Maps API key or real-time tracking is configured.

Flutter Web, Tailwind/Bootstrap, social-media/government feed ingestion, Hadoop/HDFS, MapReduce, Kafka, Spark, a trained text-aid classifier, and predictive risk analysis are not implemented in this repository and require separate infrastructure, datasets, or credentials.
