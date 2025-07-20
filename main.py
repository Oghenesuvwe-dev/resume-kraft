from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from utils.resume_generator import generate_resume_file  # Ensure this exists and is implemented

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# 👇 Redirect root path to form
@app.get("/", include_in_schema=False)
def redirect_to_form():
    return RedirectResponse("/form")

# 👇 Serve the form
@app.get("/form", response_class=HTMLResponse)
def serve_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# 👇 Generate resume from form input
@app.post("/generate")
def generate_resume(
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
    projects: str = Form(""),
    certifications: str = Form(""),
    languages: str = Form(""),
    output_format: str = Form("docx")
):
    # Process form data and generate resume
    resume_path = generate_resume_file(
        full_name=full_name,
        email=email,
        phone=phone,
        location=location,
        summary=summary,
        field_of_work=field_of_work,
        experience_level=experience_level,
        years_of_experience=years_of_experience,
        skills=skills,
        experience=experience,
        education=education,
        projects=projects,
        certifications=certifications,
        languages=languages,
        output_format=output_format
    )

    return FileResponse(resume_path, media_type="application/octet-stream", filename=os.path.basename(resume_path))
