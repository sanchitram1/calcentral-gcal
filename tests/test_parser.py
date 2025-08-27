from parser import Course, Schedule, parse_class_schedule


def test_parse_class_schedule():
    schedule_test = """Skip to Main Content
    Schedule Planner
    Help Help
    Potential Schedule for 2025 Fall
    Status\tClass #\tSubject\tCourse\tSection\tSeats Open\tInstruction Mode\tInstructor\tDay(s) & Location(s)\tUnits
    Enrolled\t29901\tIndustrial Eng & Ops Rsch\t215\t001\t20\tIn-Person Instruction\t\n    Phillip Kerger
    MW 12:00pm - 12:59pm - Latimer 120
    3
    Has Reserved SeatsHas Reserved Seats
    Reserved Seats:
    130 of 150 At least some seats in this class are reserved for students who meet specific criteria. See the Berkeley Academic Guide Class Schedule for details.
    Enrolled\t33001\tIndustrial Eng & Ops Rsch\t215\t102\t18\tIn-Person Instruction\t\n    F 10:00am - 10:59am - Barker 101
    0"""

    result = parse_class_schedule(schedule_test)
    expected = [
        Course(
            id="29901",
            name="Industrial Eng & Ops Rsch",
            number="215",
            location="Latimer 120",
            schedule=Schedule(start_time="12:00pm", end_time="12:59pm", days="MW"),
            instructor=["Phillip Kerger"],
        ),
        Course(
            id="33001",
            name="Industrial Eng & Ops Rsch",
            number="215",
            location="Barker 101",
            schedule=Schedule(start_time="10:00am", end_time="10:59am", days="F"),
            instructor=[],
        ),
    ]
    assert result == expected


def test_parse_class_schedule_tuesday_thursday():
    schedule_test = """
    Skip to Main Content
    Schedule Planner
    Help Help
    Enrolled\t29900\tIndustrial Eng & Ops Rsch\t241\t002\t31\tIn-Person Instruction\t
    Thibaut Mastrolia
    TTh 11:00am - 12:29pm - Haas Faculty Wing F295
    3
    Has Reserved SeatsHas Reserved Seats
    Reserved Seats:
    97 of 125 At least some seats in this class are reserved for students who meet specific criteria. See the Berkeley Academic Guide Class Schedule for details.
    32 of 35 At least some seats in this class are reserved for students who meet specific criteria. See the Berkeley Academic Guide Class Schedule for details.
    """
    result = parse_class_schedule(schedule_test)
    expected = [
        Course(
            id="29900",
            name="Industrial Eng & Ops Rsch",
            number="241",
            location="Haas Faculty Wing F295",
            schedule=Schedule(start_time="11:00am", end_time="12:29pm", days="TTh"),
            instructor=["Thibaut Mastrolia"],
        ),
    ]
    assert result == expected
