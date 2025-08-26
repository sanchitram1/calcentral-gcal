
import re
from typing import List, Dict

def parse_schedule_from_text(text_content: str) -> List[Dict]:
    """
    Parse schedule from UC Berkeley text format and extract class information.
    """
    classes = []
    lines = text_content.strip().split('\n')
    
    current_class = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines and headers
        if not line or line.startswith('Skip to Main Content') or line.startswith('Schedule Planner'):
            continue
            
        # Match enrolled class entries
        # Pattern: Status Class# Subject Course Section Seats Open Instruction Mode Instructor Day(s) & Location(s) Units
        enrolled_match = re.match(r'Enrolled\s+(\d+)\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+?)\s+(.+)', line)
        
        if enrolled_match:
            class_num = enrolled_match.group(1)
            subject = enrolled_match.group(2).strip()
            course_num = enrolled_match.group(3)
            
            current_class = {
                'class_number': class_num,
                'subject': subject,
                'course_number': course_num,
                'name': '',
                'instructor': '',
                'days': [],
                'start_time': '',
                'end_time': '',
                'location': ''
            }
            continue
        
        # Look for instructor name (usually on the next line)
        if current_class and not current_class.get('instructor'):
            # Match instructor name pattern
            instructor_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$', line)
            if instructor_match:
                current_class['instructor'] = instructor_match.group(1)
                continue
        
        # Look for schedule pattern: MW 12:00pm - 12:59pm - Location
        schedule_match = re.search(r'([MTWRF]+)\s+(\d{1,2}:\d{2}[ap]m)\s*-\s*(\d{1,2}:\d{2}[ap]m)\s*-\s*(.+)', line)
        if schedule_match and current_class:
            days_str = schedule_match.group(1)
            start_time = schedule_match.group(2)
            end_time = schedule_match.group(3)
            location = schedule_match.group(4).strip()
            
            # Convert day abbreviations to full names
            day_mapping = {'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday', 'R': 'Thursday', 'F': 'Friday'}
            days = [day_mapping[d] for d in days_str if d in day_mapping]
            
            current_class.update({
                'days': days,
                'start_time': start_time,
                'end_time': end_time,
                'location': location
            })
            
            # Try to extract course name from subject
            if 'Industrial Eng & Ops Rsch' in current_class['subject']:
                # Map course numbers to names based on the calendar description
                course_names = {
                    '215': 'DATABASE SYSTEMS',
                    '221': 'INTRO FINANCE ENG', 
                    '240': 'OPTIMIZATION ANALYT',
                    '241': 'RISK MODELING SIMUL',
                    '242A': 'MACH LRNING & DATA',
                    '298': 'GRP STUD, SEM, RES'
                }
                current_class['name'] = course_names.get(current_class['course_number'], f"Course {current_class['course_number']}")
            
            classes.append(current_class.copy())
            current_class = {}
    
    # Also parse the calendar description section for additional details
    calendar_section = text_content[text_content.find('MondayThis day has'):]
    if calendar_section:
        # Extract course names from calendar descriptions
        name_matches = re.findall(r'Industrial Eng & Ops Rsch - (\d+[A-Z]*) ([A-Z\s]+) from', calendar_section)
        course_name_map = {match[0]: match[1].strip() for match in name_matches}
        
        # Update class names
        for cls in classes:
            if cls['course_number'] in course_name_map:
                cls['name'] = course_name_map[cls['course_number']]
    
    return classes

def test_parser():
    """Test the parser with the example file"""
    with open('class.example.txt', 'r') as f:
        content = f.read()
    
    classes = parse_schedule_from_text(content)
    
    print("Parsed Classes:")
    for cls in classes:
        print(f"Name: {cls['name']}")
        print(f"Number: {cls['course_number']}")
        print(f"Days/Time: {' '.join(cls['days'])} {cls['start_time']} - {cls['end_time']}")
        print(f"Place: {cls['location']}")
        print(f"Instructor: {cls['instructor']}")
        print("-" * 40)
    
    return classes

if __name__ == "__main__":
    test_parser()
