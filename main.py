"""
Candid Office — Consent-based file collection
Team members click Accept, then upload photos and text files.
Nothing is deleted from their devices.
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
import uuid
import time

app = FastAPI(title="Candid Office")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def landing():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candid Office</title>
    <style>
      body { font-family: system-ui, sans-serif; background: #0f0f1a; color: #f5f6fa; margin: 0; padding: 2rem 1rem; text-align: center; }
      .card { background: #1a1a2e; max-width: 420px; margin: 2rem auto; padding: 2rem 1.5rem; border-radius: 16px; }
      h1 { margin-top: 0; font-size: 1.8rem; }
      p { color: #a0a0b0; line-height: 1.5; }
      button { background: #6c5ce7; color: white; border: none; padding: 0.9rem 1.4rem; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; width: 100%; margin-top: 1rem; }
      .note { font-size: 0.85rem; margin-top: 1.5rem; }
    </style>
    </head>
    <body>
      <div class="card">
        <h1>Candid Office</h1>
        <p>Join to securely share photos and text files with the team.</p>
        <p><strong>Your originals stay on your phone.</strong> Only copies you choose are uploaded.</p>
        <form action="/accept" method="post">
          <button type="submit">Accept & Join</button>
        </form>
        <p class="note">By clicking Accept you agree to upload selected files. Nothing is accessed or deleted from your device automatically.</p>
      </div>
    </body>
    </html>
    """

@app.post("/accept", response_class=HTMLResponse)
async def accept():
    session = str(uuid.uuid4())[:8]
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload — Candid Office</title>
    <style>
      body {{ font-family: system-ui, sans-serif; background: #0f0f1a; color: #f5f6fa; margin: 0; padding: 1.5rem 1rem; }}
      .card {{ background: #1a1a2e; max-width: 480px; margin: 0 auto; padding: 1.5rem; border-radius: 16px; }}
      h2 {{ margin-top: 0; }}
      input[type=file] {{ width: 100%; margin: 0.8rem 0; }}
      button {{ background: #6c5ce7; color: white; border: none; padding: 0.85rem; border-radius: 10px; font-weight: 600; width: 100%; cursor: pointer; }}
      label {{ display: block; margin-top: 1rem; font-weight: 500; }}
    </style>
    </head>
    <body>
      <div class="card">
        <h2>Upload Files</h2>
        <p>Select the photos and text files you want to share. Your originals remain on your device.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="hidden" name="session" value="{session}">
          <label>Photos</label>
          <input type="file" name="photos" accept="image/*" multiple>
          <label>Text files</label>
          <input type="file" name="texts" accept=".txt,.text" multiple>
          <button type="submit">Upload Selected Files</button>
        </form>
      </div>
    </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(session: str = Form(...), photos: list[UploadFile] = File(default=[]), texts: list[UploadFile] = File(default=[])):
    saved = []
    folder = UPLOAD_DIR / session
    folder.mkdir(exist_ok=True)
    for f in photos + texts:
        if f.filename:
            dest = folder / f"{int(time.time())}_{f.filename}"
            content = await f.read()
            dest.write_bytes(content)
            saved.append(f.filename)
    files_list = "<br>".join(saved) if saved else "No files selected."
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Done</title>
    <style>body{{font-family:system-ui,sans-serif;background:#0f0f1a;color:#f5f6fa;margin:0;padding:2rem 1rem;text-align:center;}}.card{{background:#1a1a2e;max-width:420px;margin:0 auto;padding:2rem 1.5rem;border-radius:16px;}}.success{{color:#00b894;font-size:1.2rem;}}</style></head>
    <body><div class="card"><p class="success">Upload complete</p><p>Files received (copies only — originals remain on your phone):</p><p>{files_list}</p><p><a href="/" style="color:#6c5ce7;">Back</a></p></div></body></html>
    """

@app.get("/admin")
async def admin():
    sessions = []
    if UPLOAD_DIR.exists():
        for d in UPLOAD_DIR.iterdir():
            if d.is_dir():
                files = [f.name for f in d.iterdir() if f.is_file()]
                sessions.append({"session": d.name, "files": files})
    return {"uploads": sessions}
