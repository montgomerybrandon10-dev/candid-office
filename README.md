# Candid Office

Consent-based upload page for team photos and text files.

- Landing page requires Accept
- After Accept, users select and upload photos + .txt files
- Originals stay on their device
- Uploaded copies are stored under /uploads/{session}/

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Admin view of received files: `/admin`
