# WhistleBlower — Cloud Run Deployment

## Prerequisites
- Google Cloud project with billing enabled
- gcloud CLI authenticated: `gcloud auth login`
- Cloud Run API enabled: `gcloud services enable run.googleapis.com`

## Deploy in 3 commands
```bash
export PROJECT_ID=your-gcp-project-id
export GEMINI_API_KEY=your-gemini-api-key

gcloud builds submit --config deployment/cloudbuild.yaml \
  --substitutions=_GEMINI_API_KEY=$GEMINI_API_KEY \
  --project=$PROJECT_ID
```

## Run locally with Docker
```bash
docker build -t whistle-blower .
docker run -p 8080:8080 -e GEMINI_API_KEY=$GEMINI_API_KEY whistle-blower
```

## After deployment
Cloud Run will return a URL like:
https://whistle-blower-xxxxx-uc.a.run.app

Test it with:
```bash
curl https://whistle-blower-xxxxx-uc.a.run.app/health
```

Note: The interactive agent requires `adk run app` locally. 
The Cloud Run deployment exposes the MCP server for API access.
