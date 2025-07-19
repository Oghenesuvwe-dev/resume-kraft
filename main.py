from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid
import os
import tempfile
from docx import Document
from datetime import datetime
from docx2pdf import convert

app = FastAPI()

# Configure templates directory
templates = Jinja2Templates(directory="templates")

# Ensure resumes directory exists
os.makedirs("resumes", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate")
async def generate_resume(
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
    output_format: str = Form(...)
):
    # Create unique filenames based on format
    docx_filename = f"resume_{uuid.uuid4()}.docx"
    docx_filepath = os.path.join("resumes", docx_filename)
    
    # Create the document
    doc = Document()
    
    # Add resume content
    doc.add_heading(full_name, 0)
    
    # Contact information section
    contact_info = doc.add_paragraph()
    contact_info.add_run("Email: ").bold = True
    contact_info.add_run(email)
    contact_info.add_run(" | ").bold = True
    contact_info.add_run("Phone: ").bold = True
    contact_info.add_run(phone)
    contact_info.add_run(" | ").bold = True
    contact_info.add_run("Location: ").bold = True
    contact_info.add_run(location)
    
    # Professional Summary section
    doc.add_heading("Professional Summary", level=1)
    summary_para = doc.add_paragraph()
    summary_para.add_run(f"{experience_level} {field_of_work} • {years_of_experience} Years of Experience\n").bold = True
    summary_para.add_run(summary)
    
    # Skills section
    doc.add_heading("Skills", level=1)
    skills_list = skills.split(",")
    for skill in skills_list:
        doc.add_paragraph(skill.strip(), style="List Bullet")
    
    # Experience section
    doc.add_heading("Work Experience", level=1)
    doc.add_paragraph(experience)
    
    # Education section
    doc.add_heading("Education", level=1)
    doc.add_paragraph(education)
    
    # Optional sections
    if projects:
        doc.add_heading("Projects", level=1)
        doc.add_paragraph(projects)
    
    if certifications:
        doc.add_heading("Certifications", level=1)
        doc.add_paragraph(certifications)
    
    if languages:
        doc.add_heading("Languages", level=1)
        languages_list = languages.split(",")
        for language in languages_list:
            doc.add_paragraph(language.strip(), style="List Bullet")
    
    # Footer with generation date
    footer = doc.sections[0].footer
    footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_para.text = f"Generated on {datetime.now().strftime('%Y-%m-%d')} via Resume Kraft"
    
    # Save the document as DOCX
    doc.save(docx_filepath)
    
    # Handle different output formats
    if output_format == "pdf":
        try:
            # Create PDF filename
            pdf_filename = f"resume_{uuid.uuid4()}.pdf"
            pdf_filepath = os.path.join("resumes", pdf_filename)
            
            # Convert DOCX to PDF
            convert(docx_filepath, pdf_filepath)
            
            # Return the PDF file
            return FileResponse(
                path=pdf_filepath,
                filename=pdf_filename,
                media_type="application/pdf"
            )
        except Exception as e:
            # If PDF conversion fails, return the DOCX file instead
            print(f"PDF conversion failed: {e}. Returning DOCX file instead.")
            return FileResponse(
                path=docx_filepath, 
                filename=docx_filename,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        # Return the DOCX file
        return FileResponse(
            path=docx_filepath, 
            filename=docx_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)