from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Initialize FastAPI app
app = FastAPI()

# Mount static files (e.g., CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set the directory for templates (e.g., HTML forms)
templates = Jinja2Templates(directory="templates")

# Root route for displaying form
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# (Example) Handle form submission - update this to match your actual form
@app.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    # Add other form fields as needed...
):
    return templates.TemplateResponse("success.html", {
        "request": request,
        "name": full_name,
        "email": email
    })

# Start the app with a dynamic port for Render compatibility
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render sets this dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port)