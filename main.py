import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response

from ics import generate_ics_file
from parser import (  # Import deserialize_courses
    deserialize_courses,
    parse_class_schedule,
)

app = FastAPI(title="UC Berkeley Schedule to Google Calendar")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UC Berkeley Schedule Parser</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .text-area { border: 2px solid #ccc; padding: 20px; margin: 20px 0; border-radius: 4px; }
            .form-group { margin: 15px 0; }
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
        <h1>🗓️ UC Berkeley Schedule Parser</h1>
        <p>Paste your schedule text from UC Berkeley Schedule Planner to parse your class schedule!</p>

        <form id="uploadForm">
            <div class="form-group">
                <label>Paste Schedule Text (from UC Berkeley Schedule Planner page):</label>
                <div class="text-area">
                    <textarea id="scheduleText" name="schedule_text" placeholder="Paste the text content from your schedule planner page here..."></textarea>
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
            const uploadForm = document.getElementById('uploadForm');

            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                document.getElementById('results').innerHTML = '<p>Processing schedule... 📋</p>';

                try {
                    const textData = {
                        schedule_text: document.getElementById('scheduleText').value,
                        semester_start: document.getElementById('semester_start').value,
                        semester_end: document.getElementById('semester_end').value
                    };
                    const response = await fetch('/parse-text-schedule', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(textData)
                    });

                    const result = await response.json();
                    displayResults(result);
                } catch (error) {
                    document.getElementById('results').innerHTML = 
                        `<p class="error">Error: ${error.message}</p>`;
                }
            });

            function displayResults(result) {
                console.log('***** Result inside displayResult:', result.classes);
                if (result.error) {
                    console.error('***** Error:', result.error);
                    document.getElementById('results').innerHTML = 
                        `<p class="error">Error: ${result.error}</p>`;
                    return;
                }

                let html = '<div class="schedule-preview"><h3>📚 Extracted Classes:</h3>';
                result.classes.forEach(cls => {
                    const instructorList = Array.isArray(cls.instructor) ? cls.instructor.join(', ') : cls.instructor || 'TBA';
                    html += `
                        <div class="class-item">
                            <strong>${cls.name} ${cls.number}</strong><br>
                            📅 ${cls.schedule.days} | 🕐 ${cls.schedule.start_time} - ${cls.schedule.end_time}<br>
                            📍 ${cls.location} | 👨‍🏫 ${instructorList}
                        </div>
                    `;
                });

                html += `
                    </div>
                    <button onclick="downloadICSFile()" style="margin-top: 15px;">
                        📄 Download ICS File
                    </button>
                `;

                document.getElementById('results').innerHTML = html;
                window.extractedData = result;
            }

            async function downloadICSFile() {
                try {
                    console.log('Starting download...', window.extractedData);

                    const response = await fetch('/generate-ics', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(window.extractedData)
                    });

                    console.log('Response status:', response.status);
                    console.log('Response headers:', response.headers);

                    if (response.ok) {
                        const blob = await response.blob();
                        console.log('Blob created:', blob.size, 'bytes');

                        // Check if we're on mobile
                        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

                        if (isMobile) {
                            // Mobile fallback: show content in new window/tab
                            const icsText = await blob.text();
                            const newWindow = window.open('', '_blank');
                            if (newWindow) {
                                newWindow.document.write(`
                                    <html>
                                    <head>
                                        <title>UC Berkeley Schedule - Calendar File</title>
                                        <style>
                                            body { font-family: monospace; margin: 20px; }
                                            .instructions { background: #e8f5e8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                                            .content { background: #f5f5f5; padding: 10px; border-radius: 5px; white-space: pre-wrap; font-size: 12px; }
                                        </style>
                                    </head>
                                    <body>
                                        <div class="instructions">
                                            <h3>📱 Mobile Download Instructions:</h3>
                                            <p>1. Select all the text below (tap and hold, then "Select All")</p>
                                            <p>2. Copy it</p>
                                            <p>3. Create a new file called "schedule.ics" on your device</p>
                                            <p>4. Paste the content and save</p>
                                            <p>5. Open the file with your calendar app to import</p>
                                        </div>
                                        <div class="content">${icsText}</div>
                                    </body>
                                    </html>
                                `);
                                newWindow.document.close();
                            }
                            alert('📱 Calendar file opened in new tab! Follow the instructions to save and import it.');
                        } else {
                            // Desktop: try normal download
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = url;
                            a.download = 'uc_berkeley_schedule.ics';

                            // Add to DOM, click, and remove
                            document.body.appendChild(a);
                            a.click();

                            // Cleanup
                            setTimeout(() => {
                                document.body.removeChild(a);
                                window.URL.revokeObjectURL(url);
                            }, 100);

                            alert('✅ ICS file downloaded! Check your downloads folder and import it into your calendar app.');
                        }
                    } else {
                        console.error('Response not ok:', response.status);
                        try {
                            const errorText = await response.text();
                            console.error('Error response:', errorText);
                            alert(`Error downloading file: ${response.status} - ${errorText}`);
                        } catch (e) {
                            alert(`Error downloading file: ${response.status}`);
                        }
                    }
                } catch (error) {
                    console.error('Download error:', error);
                    alert(`Error: ${error.message}`);
                }
            }
        </script>
    </body>
    </html>
    """


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
        parsed_courses = parse_class_schedule(schedule_text)

        # Convert to the format expected by the frontend using Course.serialize()
        courses_for_frontend = []
        for cls in parsed_courses:
            courses_for_frontend.append(cls.serialize())

        return {
            "success": True,
            "classes": courses_for_frontend,
            "semester_start": semester_start,
            "semester_end": semester_end,
            "method": "text_parsing",
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/generate-ics")
async def generate_ics(request: Request):
    try:
        data = await request.json()
        classes_data = data.get("classes", [])
        semester_start = data.get("semester_start", "")
        semester_end = data.get("semester_end", "")

        if not classes_data:
            return Response(
                content='{"error": "No classes to export"}',
                status_code=400,
                media_type="application/json",
            )

        # Convert dictionary data back to Course objects using deserialize_courses
        course_objects = deserialize_courses(classes_data)

        # Generate ICS content
        ics_content = generate_ics_file(course_objects, semester_start, semester_end)

        response = Response(
            content=ics_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": "attachment; filename=uc_berkeley_schedule.ics",
                "Content-Type": "text/calendar; charset=utf-8",
            },
        )

        return response

    except Exception as e:
        print(f"Error generating ICS: {str(e)}")
        return Response(
            content=f'{{"error": "{str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
