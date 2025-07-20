from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.resume_generator import generate_resume_file
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Redirect root path to form
@app.get("/", include_in_schema=False)
def redirect_to_form():
    return RedirectResponse("/form")

# Serve the form
@app.get("/form", response_class=HTMLResponse)
def serve_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# For backward compatibility, also serve the form at root
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate")
async def generate(
    request: Request,
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
    output_format: str = Form(...),
    other_field_value: str = Form(None)
):
    try:
        # If field_of_work is "other", use the other_field_value
        if field_of_work == "other" and other_field_value:
            field_of_work = other_field_value
            
        data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "location": location,
            "summary": summary,
            "field_of_work": field_of_work,
            "experience_level": experience_level,
            "years_of_experience": years_of_experience,
            "skills": skills,
            "experience": experience,
            "education": education,
            "projects": projects,
            "certifications": certifications,
            "languages": languages,
            "output_format": output_format
        }
        
        resume_path = generate_resume_file(data)
        filename = f"resume_{full_name.replace(' ', '_')}.{output_format}"
        
        # Create a download URL
        download_url = f"/download/{os.path.basename(resume_path)}"
        
        # Return the success template with download information
        return templates.TemplateResponse(
            "success.html", 
            {
                "request": request,
                "full_name": full_name,
                "field_of_work": field_of_work,
                "output_format": output_format,
                "download_url": download_url
            }
        )
    except Exception as e:
        return HTMLResponse(f"Internal Error: {str(e)}", status_code=500)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"resumes/{filename}"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )