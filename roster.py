class Employee:
    def __init__(self, name, start_time, end_time):
        # Instantiate the Employee
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

        # Set the hours worked
        self.hours_worked = self.end_time - self.start_time

        # If the employee works past midnight their hours worked will be negative, 
        # which can be added to 24 to get their actual hours worked.
        if (self.hours_worked < 0):
            self.hours_worked = 24 + self.hours_worked

        # Set break length to 0, if the employee works 4.5 or 6 hours assign them the relevant break.
        self.break_length = 0
        if (self.hours_worked >= 4.5):
            self.break_length = .25
        if (self.hours_worked >= 6):
            self.break_length = .5

# Example Roster
e0001 = Employee("Tommy", 13, 1)
e0002 = Employee("Carl", 13, 1 )
e0003 = Employee("John", 13, 1)
e0004 = Employee("Conor", 13, 1)
roster = [e0001, e0002, e0003, e0004]
roster.sort(key=lambda x: x.start_time)


def calculateEmployeeBreaks(roster):
    breakList = []
    current_time = 0
    for employee in roster:
        if (employee.break_length > 0):
            
            # Set the employee to begin their break 1/4 of their shift in
            break_start = employee.start_time + ((employee.hours_worked / 4))
            if (break_start < current_time):
                break_start += prev_employee.break_length
            break_end = break_start + employee.break_length

            # Add when the employee is due to go on break and when they return to the list
            breakList.append([employee.name, break_start, break_end])
            prev_employee = employee
            current_time = break_end
            
    print(breakList)


calculateEmployeeBreaks(roster)