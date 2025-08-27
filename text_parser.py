
import re
from typing import List, Dict

def parse_schedule_from_text(text_content: str) -> List[Dict]:
    """
    Parse schedule from UC Berkeley text format and extract class information.
    """
    classes = []
    lines = text_content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and headers
        if not line or line.startswith('Skip to Main Content') or line.startswith('Schedule Planner'):
            i += 1
            continue
        
        # Look for "Enrolled" status lines
        if line.startswith('Enrolled'):
            # Parse the enrolled line: Enrolled	ClassNum	Subject	Course	Section	Seats	Mode	[Instructor]	[Schedule]	Units
            parts = line.split('\t')
            if len(parts) < 4:
                # Try splitting by spaces if tabs don't work
                parts = re.split(r'\s+', line)
            
            if len(parts) >= 4:
                class_num = parts[1]
                subject = parts[2]
                course_num = parts[3]
                section = parts[4] if len(parts) > 4 else ""
                
                current_class = {
                    'class_number': class_num,
                    'subject': subject,
                    'course_number': course_num,
                    'section': section,
                    'name': f"{subject} {course_num}",
                    'instructor': '',
                    'days': [],
                    'start_time': '',
                    'end_time': '',
                    'location': '',
                    'units': ''
                }
                
                # Look ahead for instructor and schedule info in the next few lines
                j = i + 1
                found_schedule = False
                
                while j < len(lines) and j < i + 10:  # Look at next 10 lines max
                    next_line = lines[j].strip()
                    
                    # Stop if we hit another "Enrolled" line
                    if next_line.startswith('Enrolled'):
                        break
                    
                    # Skip reserved seats and other metadata
                    if ('Reserved Seats' in next_line or 
                        'At least some seats' in next_line or
                        next_line.isdigit() or
                        not next_line):
                        j += 1
                        continue
                    
                    # Look for instructor name (usually a line with just first and last name)
                    instructor_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$', next_line)
                    if instructor_match and not current_class['instructor']:
                        current_class['instructor'] = instructor_match.group(1)
                        j += 1
                        continue
                    
                    # Look for schedule pattern: Days Time - Time - Location
                    # Handle both "MW" and "TTh" patterns
                    schedule_match = re.search(r'((?:M|T|W|R|F|TTh|Th)+)\s+(\d{1,2}:\d{2}[ap]m)\s*-\s*(\d{1,2}:\d{2}[ap]m)\s*-\s*(.+)', next_line)
                    if schedule_match:
                        days_str = schedule_match.group(1)
                        start_time = schedule_match.group(2)
                        end_time = schedule_match.group(3)
                        location = schedule_match.group(4).strip()
                        
                        # Parse days - handle TTh specially
                        days = parse_days(days_str)
                        
                        current_class.update({
                            'days': days,
                            'start_time': start_time,
                            'end_time': end_time,
                            'location': location
                        })
                        found_schedule = True
                        break
                    
                    j += 1
                
                # Only add classes that have schedule information
                if found_schedule:
                    classes.append(current_class)
                
                # Move to the line after where we stopped looking
                i = j
            else:
                i += 1
        else:
            i += 1
    
    # Extract course names from the calendar section if available
    extract_course_names_from_calendar(text_content, classes)
    
    return classes

def parse_days(days_str: str) -> List[str]:
    """Parse day abbreviations into full day names, handling TTh specially"""
    days = []
    
    # Handle TTh (Tuesday/Thursday) first
    if 'TTh' in days_str:
        days.extend(['Tuesday', 'Thursday'])
        days_str = days_str.replace('TTh', '')
    elif 'Th' in days_str:
        days.append('Thursday')
        days_str = days_str.replace('Th', '')
    
    # Handle remaining single letter days
    day_mapping = {
        'M': 'Monday', 
        'T': 'Tuesday', 
        'W': 'Wednesday', 
        'R': 'Thursday',  # Note: R is also Thursday in some systems
        'F': 'Friday'
    }
    
    for char in days_str:
        if char in day_mapping:
            day_name = day_mapping[char]
            if day_name not in days:  # Avoid duplicates
                days.append(day_name)
    
    return days

def extract_course_names_from_calendar(text_content: str, classes: List[Dict]):
    """Extract course names from the calendar section of the text"""
    # Look for the calendar section with course descriptions
    calendar_match = re.search(r'This day has (.+?) from', text_content)
    if calendar_match:
        # Find all course name patterns in the calendar description
        name_patterns = re.findall(r'Industrial Eng & Ops Rsch - (\d+[A-Z]*) ([A-Z\s]+)', text_content)
        course_name_map = {}
        
        for course_num, course_name in name_patterns:
            course_name_map[course_num] = course_name.strip()
        
        # Update class names with extracted course names
        for cls in classes:
            if cls['course_number'] in course_name_map:
                cls['name'] = course_name_map[cls['course_number']]

def test_parser():
    """Test the parser with the example file"""
    with open('class.example.txt', 'r') as f:
        content = f.read()
    
    classes = parse_schedule_from_text(content)
    
    print(f"Found {len(classes)} enrolled classes:")
    print("=" * 50)
    
    for i, cls in enumerate(classes, 1):
        print(f"{i}. {cls['name']} ({cls['course_number']})")
        print(f"   Class #: {cls['class_number']}")
        print(f"   Days: {', '.join(cls['days'])}")
        print(f"   Time: {cls['start_time']} - {cls['end_time']}")
        print(f"   Location: {cls['location']}")
        print(f"   Instructor: {cls['instructor']}")
        print("-" * 40)
    
    return classes

if __name__ == "__main__":
    test_parser()
