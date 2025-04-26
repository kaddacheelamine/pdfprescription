from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import weasyprint
from datetime import datetime
import tempfile
import jinja2
import supabase
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def send(f,t,s):
# Email details
  from_email = f
  to_email = t
  subject = s
  html = """
  <html lang="ar" dir="rtl">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">

      <title>Rushita - وصفتك الطبية الرقمية</title>
      <style>
          body {
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
              margin: 0;
              padding: 0;
              background-color: #f5f5f5;
              color: #333;
              direction: rtl;
          }
          .container {
              max-width: 600px;
              margin: 0 auto;
              background-color: #ffffff;
              border-radius: 8px;
              overflow: hidden;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          }
          .header {
              background-color: #1e88e5;
              color: white;
              padding: 20px;
              text-align: center;
          }
          .logo {
              font-size: 28px;
              font-weight: bold;
              letter-spacing: 1px;
          }
          .content {
              padding: 30px;
          }
          .prescription-info {
              background-color: #f1f8ff;
              border-radius: 6px;
              padding: 20px;
              margin-bottom: 20px;
          }
          .info-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 10px;
          }
          .info-title {
              font-weight: bold;
              color: #0d47a1;
          }
          .button-container {
              text-align: center;
              margin: 30px 0;
          }
          .button {
              display: inline-block;
              background-color: #1e88e5;
              color: white;
              font-weight: bold;
              text-decoration: none;
              padding: 12px 30px;
              border-radius: 4px;
              transition: background-color 0.3s;
          }
          .button:hover {
              background-color: #0d47a1;
          }
          .footer {
              background-color: #1e88e5;
              color: white;
              text-align: center;
              padding: 15px;
              font-size: 14px;
          }
      </style>
  </head>
  <body>
      <div class="container">
          <div class="header">
              <div class="logo">Rushita</div>
              <p>منصتك الرقمية للوصفات الطبية</p>
          </div>
          
          <div class="content">
              <h2>مرحباً بك في Rushita</h2>
              <p>تم إصدار وصفة طبية جديدة لك. يمكنك الوصول إليها والاطلاع على تفاصيلها من خلال الرابط أدناه.</p>
              
              
              
              <div class="button-container">
                  <a href="""
  
  html1=f"https://wyypjyfyldeqnzvylsmt.supabase.co/storage/v1/object/public/pdfs//{s}" 
              
              
  html2="""
  class="button">عرض الوصفة الطبية</a>
  </div>
              <p>إذا كانت لديك أية استفسارات، يرجى التواصل مع طبيبك أو الاتصال بفريق دعم Rushita.</p>
              <p>نتمنى لك دوام الصحة والعافية.</p>
          </div>
          
          <div class="footer">
              <p>© 2025 Rushita - جميع الحقوق محفوظة</p>
              <p>هذه الرسالة سرية وموجهة فقط للشخص المعني</p>
          </div>
      </div>
  </body>
  </html>
  """



  # Create message container
  message = MIMEMultipart("alternative")
  message["Subject"] = subject
  message["From"] = from_email
  message["To"] = to_email

  # Attach the HTML part
  html_part = MIMEText(html+html1+html2, "html")
  message.attach(html_part)

  # SMTP settings
  smtp_server = "smtp.gmail.com"
  smtp_port = 587
  smtp_user = os.getenv("USERTP")
  smtp_password = os.getenv("PWDTP")

  # Send the email
  try:
      server = smtplib.SMTP(smtp_server, smtp_port)
      server.starttls()
      server.login(smtp_user, smtp_password)
      server.sendmail(from_email, to_email, message.as_string())
      print("Email sent successfully.")
      server.quit()
  except Exception as e:
      print("Error sending email:", e)



# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase_client = supabase.create_client(supabase_url, supabase_key)

app = FastAPI()

# CORS configuration
origins = [
    "*",  # Allow all origins (modify for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models
class Medicine(BaseModel):
    name: str
    dosage: str  # This represents Duration in the template
    frequency: str
    note: str

class PrescriptionData(BaseModel):
    sendToValue: str
    patientName: str
    patientAge: str
    patientDescription: str
    currentDate: str
    medicines: List[Medicine]

# Define HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Medical Prescription</title>
    <style>
        @page{
            size: A5;
            margin: 0;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: white;
            color: #333;
            /* A5 size in pixels (approximately) */
            width: 148mm;
            height: 210mm;
            margin: 0 auto;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .container {
            padding: 10px;
            border: 1px solid #0066cc;
        }
        
        header {
            background-color: #f8f8f8;
            padding: 10px;
            border-bottom: 2px solid #0066cc;
            display: flex;
            justify-content: space-between;
        }
        
        .clinic-info, .doctor-info {
            width: 48%;
        }
        
        h1, h2, h3 {
            color: #0066cc;
            margin: 5px 0;
        }
        
        .contact {
            background-color: #e6f2ff;
            padding: 5px 10px;
            margin: 10px 0;
            border-left: 3px solid #0066cc;
        }
        
        .patient-info {
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
        }
        
        .patient-info div {
            margin: 5px 0;
        }
        
        .patient-info label {
            font-weight: bold;
            display: inline-block;
            width: 60px;
        }
        
        .medicines {
            margin: 15px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background-color: #0066cc;
            color: white;
            padding: 8px;
            text-align: left;
        }
        
        td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        .note {
            font-style: italic;
            color: #666;
            font-size: 0.9em;
            padding-left: 10px;
        }
        
        footer {
            margin-bottom: 0px;
            padding: 10px;
            background-color: #e6f2ff;
            text-align: center;
            border-top: 1px solid #0066cc;
            font-weight: bold;
            direction: rtl;
        }
    </style>
</head>
<body class="container">
    <div>
        <header>
            <div class="clinic-info">
                <h3>Clinic of Startup dz</h3>
                <p>Example of Address</p>
                <p>Email: clinic@example.com</p>
            </div>
            <div class="doctor-info">
                <h3>Dr Startup dz</h3>
                <p>Specialization</p>
                <p>Phone: 06 XX-XX-XX-XX</p>
            </div>
        </header>
        
        <div class="patient-info">
            <h3>Patient Information</h3>
            <div><label>Name:</label> <span>{{ patient_name }}</span></div>
            <div><label>Age:</label> <span>{{ patient_age }}</span></div>
            <div><label>Date:</label> <span>{{ current_date }}</span></div>
            {% if patient_description %}
            <div><label>Notes:</label> <span>{{ patient_description }}</span></div>
            {% endif %}
        </div>
        
        <div class="medicines">
            <h3>Medications</h3>
            <table>
                {% for medicine in medicines %}
                <tr>
                    <td>{{ medicine.name }}</td>
                    <td>{{ medicine.dosage }}</td>
                    <td>{{ medicine.frequency }}</td>
                </tr>
                {% if medicine.note %}
                <tr>
                    <td colspan="3" class="note">{{ medicine.note }}</td>
                </tr>
                {% endif %}
                {% endfor %}
            </table>
        </div>
    </div>

    
</body>
</html>
"""

@app.post("/generate-prescription")
async def generate_prescription(data: PrescriptionData):
    try:
        # Create a Jinja2 environment
        template_env = jinja2.Environment()
        template = template_env.from_string(HTML_TEMPLATE)
        
        # Render HTML with the provided data
        html_content = template.render(
            patient_name=data.patientName,
            patient_age=data.patientAge,
            current_date=data.currentDate,
            patient_description=data.patientDescription,
            medicines=data.medicines
        )
        
        # Generate a unique filename based on date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prescription_{timestamp}.pdf"
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Generate PDF from HTML
            weasyprint.HTML(string=html_content).write_pdf(temp_file.name)
            send(os.getenv("USERTP"),data.sendToValue,filename)
            
            
            # Upload the PDF to Supabase storage
            with open(temp_file.name, 'rb') as pdf_file:
                # Upload to the 'pdfs' bucket
                upload_response = supabase_client.storage.from_('pdfs').upload(
                    file=pdf_file,
                    path=filename,
                    file_options={"content-type": "application/pdf"}
                )
            
            # Remove the temporary file
            os.unlink(temp_file.name)
        
        # Get the public URL of the uploaded file
        file_url = supabase_client.storage.from_('pdfs').get_public_url(filename)
        
        return {
            "status": "success",
            "message": "Prescription PDF generated and uploaded successfully",
            "filename": filename,
            "url": file_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prescription PDF: {str(e)}")

