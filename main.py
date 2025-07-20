from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from docx import Document  # or whatever you're using to generate resumes

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/generate")
async def generate_resume(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    summary: str = Form(...),
    field_of_work: str = Form(...),
    experience_level: str = Form(...),
    years_of_experience: str = Form(...),
    skills: str = Form(...),
    experience: str = Form(...),
    education: str = Form(...),
    projects: str = Form(None),
    certifications: str = Form(None),
    languages: str = Form(None),
    output_format: str = Form(...)
):
    # ✅ Resume generation logic here
    # e.g., generate a DOCX or PDF file using the inputs
    ...
    return {"message": "Resume generated successfully"}
