from parser import parse_class_schedule


def main():
    schedule_test = """Skip to Main Content
    Schedule Planner
    Help Help
    Potential Schedule for 2025 Fall
    Status	Class #	Subject	Course	Section	Seats Open	Instruction Mode	Instructor	Day(s) & Location(s)	Units
    Enrolled	29901	Industrial Eng & Ops Rsch	215	001	20	In-Person Instruction	
    Phillip Kerger
    MW 12:00pm - 12:59pm - Latimer 120
    3
    Has Reserved SeatsHas Reserved Seats
    Reserved Seats:
    130 of 150 At least some seats in this class are reserved for students who meet specific criteria. See the Berkeley Academic Guide Class Schedule for details.
    Enrolled	33001	Industrial Eng & Ops Rsch	215	102	18	In-Person Instruction	
    F 10:00am - 10:59am - Barker 101
    0"""

    print(parse_class_schedule(schedule_test))


if __name__ == "__main__":
    main()
