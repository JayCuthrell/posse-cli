import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import your existing logic
from modules.bluesky_api import post_to_bluesky
from modules.gotosocial_api import post_to_gotosocial
from modules.linkedin_api import post_to_linkedin

# Load env vars
load_dotenv()

app = FastAPI()

# Setup templates (we will create a simple HTML UI)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": ""})

@app.post("/", response_class=HTMLResponse)
async def handle_post(
    request: Request,
    message: str = Form(...),
    bluesky: bool = Form(False),
    gotosocial: bool = Form(False),
    linkedin: bool = Form(False)
):
    results = []
    
    # Logic adapted from posse.py
    if not any([bluesky, gotosocial, linkedin]):
        results.append("⚠️ No networks selected.")
    else:
        if bluesky:
            success = post_to_bluesky(message)
            results.append("🦋 Bluesky: " + ("✅ Sent" if success else "❌ Failed"))
        
        if gotosocial:
            success = post_to_gotosocial(message)
            results.append("🐘 GoToSocial: " + ("✅ Sent" if success else "❌ Failed"))
            
        if linkedin:
            success = post_to_linkedin(message)
            results.append("🔗 LinkedIn: " + ("✅ Sent" if success else "❌ Failed"))

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "message": message, 
        "results": results
    })