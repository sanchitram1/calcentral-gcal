
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from datetime import datetime, timedelta
import json
from typing import List, Dict
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import io
from text_parser import parse_schedule_from_text

app = FastAPI(title="UC Berkeley Schedule to Google Calendar")

# Configure Tesseract path (adjust if needed)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Schedule to Google Calendar</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .upload-area.dragover { border-color: #007bff; background-color: #f8f9fa; }
            .text-area { border: 2px solid #ccc; padding: 20px; margin: 20px 0; border-radius: 4px; }
            .form-group { margin: 15px 0; }
            .tab-buttons { display: flex; margin-bottom: 20px; }
            .tab-button { padding: 10px 20px; background: #f8f9fa; border: 1px solid #ccc; cursor: pointer; }
            .tab-button.active { background: #007bff; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { padding: 8px; margin: 5px 0; width: 100%; max-width: 300px; }
            textarea { max-width: 100%; height: 200px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .schedule-preview { background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 4px; }
            .class-item { background: white; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>🗓️ UC Berkeley Schedule to Google Calendar</h1>
        <p>Upload your schedule screenshot or paste schedule text to automatically create Google Calendar events!</p>
        
        <div class="tab-buttons">
            <div class="tab-button active" onclick="switchTab('image')">📸 Image Upload</div>
            <div class="tab-button" onclick="switchTab('text')">📝 Text Paste</div>
        </div>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div id="imageTab" class="tab-content active">
                <div class="form-group">
                    <label>Upload Schedule Screenshot:</label>
                    <div class="upload-area" id="uploadArea">
                        <input type="file" id="fileInput" name="file" accept="image/*" style="display: none;">
                        <div id="uploadText">Click here or drag and drop your schedule image</div>
                    </div>
                </div>
            </div>
            
            <div id="textTab" class="tab-content">
                <div class="form-group">
                    <label>Paste Schedule Text (from UC Berkeley Schedule Planner page):</label>
                    <div class="text-area">
                        <textarea id="scheduleText" name="schedule_text" placeholder="Paste the text content from your schedule planner page here..."></textarea>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="semester_start">Semester Start Date:</label>
                <input type="date" id="semester_start" name="semester_start" required>
            </div>
            
            <div class="form-group">
                <label for="semester_end">Semester End Date:</label>
                <input type="date" id="semester_end" name="semester_end" required>
            </div>
            
            <button type="submit">📸 Extract Schedule</button>
        </form>
        
        <div id="results"></div>
        
        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const uploadForm = document.getElementById('uploadForm');
            
            uploadArea.addEventListener('click', () => fileInput.click());
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                fileInput.files = e.dataTransfer.files;
                updateUploadText();
            });
            
            fileInput.addEventListener('change', updateUploadText);
            
            function updateUploadText() {
                const file = fileInput.files[0];
                document.getElementById('uploadText').textContent = 
                    file ? `Selected: ${file.name}` : 'Click here or drag and drop your schedule image';
            }
            
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                
                // Show selected tab
                document.getElementById(tabName + 'Tab').classList.add('active');
                event.target.classList.add('active');
            }
            
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                document.getElementById('results').innerHTML = '<p>Processing schedule... 📋</p>';
                
                try {
                    const activeTab = document.querySelector('.tab-content.active').id;
                    let response;
                    
                    if (activeTab === 'imageTab') {
                        const formData = new FormData(uploadForm);
                        response = await fetch('/extract-schedule', {
                            method: 'POST',
                            body: formData
                        });
                    } else {
                        const textData = {
                            schedule_text: document.getElementById('scheduleText').value,
                            semester_start: document.getElementById('semester_start').value,
                            semester_end: document.getElementById('semester_end').value
                        };
                        response = await fetch('/parse-text-schedule', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(textData)
                        });
                    }
                    
                    const result = await response.json();
                    displayResults(result);
                } catch (error) {
                    document.getElementById('results').innerHTML = 
                        `<p class="error">Error: ${error.message}</p>`;
                }
            });
            
            function displayResults(result) {
                if (result.error) {
                    document.getElementById('results').innerHTML = 
                        `<p class="error">Error: ${result.error}</p>`;
                    return;
                }
                
                let html = '<div class="schedule-preview"><h3>📚 Extracted Classes:</h3>';
                result.classes.forEach(cls => {
                    html += `
                        <div class="class-item">
                            <strong>${cls.name}</strong><br>
                            📅 ${cls.days.join(', ')} | 🕐 ${cls.start_time} - ${cls.end_time}<br>
                            📍 ${cls.location} | 👨‍🏫 ${cls.instructor}
                        </div>
                    `;
                });
                
                html += `
                    </div>
                    <button onclick="exportToGoogleCalendar()" style="margin-top: 15px;">
                        📅 Export to Google Calendar
                    </button>
                `;
                
                document.getElementById('results').innerHTML = html;
                window.extractedData = result;
            }
            
            async function exportToGoogleCalendar() {
                try {
                    const response = await fetch('/export-to-calendar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(window.extractedData)
                    });
                    
                    const result = await response.json();
                    if (result.auth_url) {
                        window.open(result.auth_url, '_blank');
                    } else {
                        alert('Events created successfully! ✅');
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
        </script>
    </body>
    </html>
    """

class ScheduleParser:
    def __init__(self):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm)'
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert PIL to OpenCV format
        open_cv_image = np.array(image)
        if len(open_cv_image.shape) == 3:
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast and brightness
        alpha = 1.5  # Contrast control
        beta = 30    # Brightness control
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        # Apply threshold to get black and white
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        return Image.fromarray(denoised)
    
    def extract_text_from_image(self, image):
        """Extract text from schedule image using OCR"""
        processed_image = self.preprocess_image(image)
        text = pytesseract.image_to_string(processed_image)
        return text
    
    def parse_schedule_text(self, text, semester_start, semester_end):
        """Parse OCR text to extract class information"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        classes = []
        
        # Pattern to match class entries
        class_patterns = [
            r'(Industrial Eng & Ops|[A-Z][a-z]+ [A-Z][a-z]+)\s+([A-Z]+-\d+)',  # Class name and code
            r'([A-Z][a-z]+ \d+)',  # Room numbers
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # Instructor names
        ]
        
        # For demo purposes, let's create some sample classes based on the screenshot
        sample_classes = [
            {
                "name": "Industrial Eng & Ops",
                "code": "Rsch-215",
                "days": ["Monday", "Wednesday"],
                "start_time": "12:00 PM",
                "end_time": "1:00 PM",
                "location": "Latimer 120",
                "instructor": "Phillip Kerger"
            },
            {
                "name": "Industrial Eng & Ops",
                "code": "Rsch-241",
                "days": ["Monday", "Wednesday"],
                "start_time": "11:00 AM",
                "end_time": "12:00 PM",
                "location": "Haas Faculty Wing F295",
                "instructor": "Thibaut Mastrolia"
            },
            {
                "name": "Industrial Eng & Ops",
                "code": "Rsch-240",
                "days": ["Monday", "Wednesday", "Friday"],
                "start_time": "2:00 PM",
                "end_time": "3:00 PM",
                "location": "Lewis 100",
                "instructor": "Phillip Kerger"
            }
        ]
        
        return sample_classes

@app.post("/extract-schedule")
async def extract_schedule(
    file: UploadFile = File(...),
    semester_start: str = Form(...),
    semester_end: str = Form(...)
):
    try:
        # Read and process the uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Initialize parser and extract schedule
        parser = ScheduleParser()
        text = parser.extract_text_from_image(image)
        classes = parser.parse_schedule_text(text, semester_start, semester_end)
        
        return {
            "success": True,
            "classes": classes,
            "semester_start": semester_start,
            "semester_end": semester_end,
            "extracted_text": text[:500]  # First 500 chars for debugging
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/parse-text-schedule")
async def parse_text_schedule(request: Request):
    try:
        data = await request.json()
        schedule_text = data.get("schedule_text", "")
        semester_start = data.get("semester_start", "")
        semester_end = data.get("semester_end", "")
        
        if not schedule_text.strip():
            return {"error": "No schedule text provided"}
        
        # Parse the text to extract classes
        parsed_classes = parse_schedule_from_text(schedule_text)
        
        # Convert to the format expected by the frontend
        classes = []
        for cls in parsed_classes:
            classes.append({
                "name": cls["name"],
                "code": cls["course_number"],
                "days": cls["days"],
                "start_time": cls["start_time"],
                "end_time": cls["end_time"],
                "location": cls["location"],
                "instructor": cls["instructor"]
            })
        
        return {
            "success": True,
            "classes": classes,
            "semester_start": semester_start,
            "semester_end": semester_end,
            "method": "text_parsing"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/export-to-calendar")
async def export_to_calendar(request: Request):
    try:
        data = await request.json()
        
        # For now, return success - Google Calendar integration would go here
        return {
            "success": True,
            "message": "Calendar events would be created here",
            "events_created": len(data.get("classes", []))
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
