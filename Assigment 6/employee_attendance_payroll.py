import json
import os
from datetime import datetime


EMPLOYEES_FILE = "employees.json"
ATTENDANCE_FILE = "attendance.json"
PAYROLL_FILE = "payroll.json"
SALARY_SLIP_FOLDER = "salary_slips"

COMPANY_NAME = "ABC Company"
STANDARD_WORKDAY_HOURS = 8
WORKING_DAYS_PER_MONTH = 26

ATTENDANCE_STATUSES = {
    "1": "Present",
    "2": "Absent",
    "3": "Leave",
    "4": "Half Day",
}


def load_records(file_name):
    if not os.path.exists(file_name):
        save_records(file_name, [])
        return []

    try:
        with open(file_name, "r") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            print(file_name, "did not contain a list. Starting with empty data.")
            return []
    except json.JSONDecodeError:
        print(file_name, "is empty or invalid. Starting with empty data.")
        return []


def save_records(file_name, records):
    with open(file_name, "w") as file:
        json.dump(records, file, indent=4)


def initialize_files():
    for file_name in [EMPLOYEES_FILE, ATTENDANCE_FILE, PAYROLL_FILE]:
        if not os.path.exists(file_name):
            save_records(file_name, [])

    if not os.path.exists(SALARY_SLIP_FOLDER):
        os.makedirs(SALARY_SLIP_FOLDER)


def input_required(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def input_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value > 0:
                return value
            print("Value must be positive.")
        except ValueError:
            print("Please enter a valid number.")


def input_date(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Please enter date in YYYY-MM-DD format.")


def input_month(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            print("Please enter month in YYYY-MM format.")


def input_time(prompt, allow_blank=False):
    while True:
        value = input(prompt).strip()
        if allow_blank and value == "":
            return ""
        try:
            datetime.strptime(value, "%H:%M")
            return value
        except ValueError:
            print("Please enter time in 24-hour HH:MM format, for example 09:00.")


def pause():
    input("\nPress Enter to continue...")


def find_employee(employees, employee_id):
    for employee in employees:
        if employee["employee_id"].lower() == employee_id.lower():
            return employee
    return None


def find_attendance(attendance, employee_id, attendance_date):
    for record in attendance:
        if (
            record["employee_id"].lower() == employee_id.lower()
            and record["date"] == attendance_date
        ):
            return record
    return None


def calculate_hours(check_in, check_out):
    start = datetime.strptime(check_in, "%H:%M")
    end = datetime.strptime(check_out, "%H:%M")

    if end <= start:
        return None, None

    hours = (end - start).total_seconds() / 3600
    overtime = max(0, hours - STANDARD_WORKDAY_HOURS)
    return round(hours, 2), round(overtime, 2)


def display_employee(employee):
    print("\nEmployee ID:", employee["employee_id"])
    print("Name:", employee["name"])
    print("Department:", employee["department"])
    print("Designation:", employee["designation"])
    print("Monthly Basic Salary:", format_money(employee["monthly_basic_salary"]))
    print("Joining Date:", employee["joining_date"])


def list_employees(employees):
    if not employees:
        print("\nNo employees found.")
        return

    print("\nRegistered Employees")
    print("-" * 95)
    print(
        "{:<12} {:<22} {:<18} {:<18} {:>12}".format(
            "ID", "Name", "Department", "Designation", "Salary"
        )
    )
    print("-" * 95)
    for employee in employees:
        print(
            "{:<12} {:<22} {:<18} {:<18} {:>12.2f}".format(
                employee["employee_id"],
                employee["name"],
                employee["department"],
                employee["designation"],
                employee["monthly_basic_salary"],
            )
        )


def add_employee(employees):
    print("\nAdd New Employee")
    employee_id = input_required("Employee ID: ")

    if find_employee(employees, employee_id):
        print("Employee ID already exists.")
        return

    employee = {
        "employee_id": employee_id,
        "name": input_required("Name: "),
        "department": input_required("Department: "),
        "designation": input_required("Designation: "),
        "monthly_basic_salary": input_positive_float("Monthly basic salary: "),
        "joining_date": input_date("Joining date (YYYY-MM-DD): "),
    }
    employees.append(employee)
    save_records(EMPLOYEES_FILE, employees)
    print("Employee added successfully.")


def search_employee(employees):
    employee_id = input_required("\nEnter Employee ID: ")
    employee = find_employee(employees, employee_id)
    if employee:
        display_employee(employee)
    else:
        print("Employee not found.")


def update_employee(employees):
    employee_id = input_required("\nEnter Employee ID to update: ")
    employee = find_employee(employees, employee_id)

    if not employee:
        print("Employee not found.")
        return

    print("Leave a field blank to keep the current value.")
    name = input("Name (" + employee["name"] + "): ").strip()
    department = input("Department (" + employee["department"] + "): ").strip()
    designation = input("Designation (" + employee["designation"] + "): ").strip()
    salary = input("Monthly basic salary (" + str(employee["monthly_basic_salary"]) + "): ").strip()
    joining_date = input("Joining date (" + employee["joining_date"] + "): ").strip()

    if name:
        employee["name"] = name
    if department:
        employee["department"] = department
    if designation:
        employee["designation"] = designation
    if salary:
        try:
            salary_value = float(salary)
            if salary_value <= 0:
                print("Salary must be positive. Salary was not updated.")
            else:
                employee["monthly_basic_salary"] = salary_value
        except ValueError:
            print("Invalid salary. Salary was not updated.")
    if joining_date:
        try:
            datetime.strptime(joining_date, "%Y-%m-%d")
            employee["joining_date"] = joining_date
        except ValueError:
            print("Invalid joining date. Date was not updated.")

    save_records(EMPLOYEES_FILE, employees)
    print("Employee updated successfully.")


def employee_menu(employees):
    while True:
        print("\nEmployee Management")
        print("1. Add employee")
        print("2. Search employee")
        print("3. Update employee")
        print("4. Display all employees")
        print("5. Back to main menu")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_employee(employees)
        elif choice == "2":
            search_employee(employees)
        elif choice == "3":
            update_employee(employees)
        elif choice == "4":
            list_employees(employees)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


def choose_status():
    print("Attendance Status")
    for key, status in ATTENDANCE_STATUSES.items():
        print(key + ".", status)

    while True:
        choice = input("Choose status: ").strip()
        if choice in ATTENDANCE_STATUSES:
            return ATTENDANCE_STATUSES[choice]
        print("Invalid status choice.")


def record_attendance(employees, attendance):
    print("\nRecord Daily Attendance")
    employee_id = input_required("Employee ID: ")

    if not find_employee(employees, employee_id):
        print("Employee not found.")
        return

    attendance_date = input_date("Attendance date (YYYY-MM-DD): ")
    if find_attendance(attendance, employee_id, attendance_date):
        print("Attendance already recorded for this employee on this date.")
        return

    status = choose_status()
    check_in = ""
    check_out = ""
    working_hours = 0
    overtime_hours = 0

    if status in ["Present", "Half Day"]:
        check_in = input_time("Check-in time (HH:MM, blank to skip): ", True)
        if check_in:
            check_out = input_time("Check-out time (HH:MM): ")
            working_hours, overtime_hours = calculate_hours(check_in, check_out)
            if working_hours is None:
                print("Check-out must be later than check-in. Time was not saved.")
                check_in = ""
                check_out = ""
                working_hours = 0
                overtime_hours = 0

    record = {
        "employee_id": employee_id,
        "date": attendance_date,
        "status": status,
        "check_in": check_in,
        "check_out": check_out,
        "working_hours": working_hours,
        "overtime_hours": overtime_hours,
    }
    attendance.append(record)
    save_records(ATTENDANCE_FILE, attendance)
    print("Attendance recorded successfully.")


def record_check_in_out(employees, attendance):
    print("\nRecord Check-In / Check-Out")
    employee_id = input_required("Employee ID: ")

    if not find_employee(employees, employee_id):
        print("Employee not found.")
        return

    attendance_date = input_date("Attendance date (YYYY-MM-DD): ")
    record = find_attendance(attendance, employee_id, attendance_date)

    if not record:
        print("Attendance was not found for this date.")
        create = input("Create Present attendance for this date? (y/n): ").strip().lower()
        if create != "y":
            return
        record = {
            "employee_id": employee_id,
            "date": attendance_date,
            "status": "Present",
            "check_in": "",
            "check_out": "",
            "working_hours": 0,
            "overtime_hours": 0,
        }
        attendance.append(record)

    if record["status"] in ["Absent", "Leave"]:
        print("Time records are only allowed for Present or Half Day status.")
        return

    check_in = input_time("Check-in time (HH:MM): ")
    check_out = input_time("Check-out time (HH:MM): ")
    working_hours, overtime_hours = calculate_hours(check_in, check_out)

    if working_hours is None:
        print("Check-out must be later than check-in.")
        return

    record["check_in"] = check_in
    record["check_out"] = check_out
    record["working_hours"] = working_hours
    record["overtime_hours"] = overtime_hours

    save_records(ATTENDANCE_FILE, attendance)
    print("Time record saved successfully.")


def month_records(attendance, employee_id, month):
    selected = []
    for record in attendance:
        if record["employee_id"].lower() == employee_id.lower() and record["date"].startswith(month):
            selected.append(record)
    return selected


def attendance_summary(records):
    summary = {
        "present": 0,
        "absent": 0,
        "leave": 0,
        "half_day": 0,
        "unpaid_days": 0,
        "overtime_hours": 0,
        "working_hours": 0,
    }

    for record in records:
        status = record["status"]
        if status == "Present":
            summary["present"] += 1
        elif status == "Absent":
            summary["absent"] += 1
            summary["unpaid_days"] += 1
        elif status == "Leave":
            summary["leave"] += 1
        elif status == "Half Day":
            summary["half_day"] += 1
            summary["unpaid_days"] += 0.5

        summary["overtime_hours"] += float(record.get("overtime_hours", 0))
        summary["working_hours"] += float(record.get("working_hours", 0))

    summary["overtime_hours"] = round(summary["overtime_hours"], 2)
    summary["working_hours"] = round(summary["working_hours"], 2)
    return summary


def display_attendance_records(records):
    if not records:
        print("No attendance records found.")
        return

    print("-" * 90)
    print(
        "{:<12} {:<10} {:<10} {:<10} {:>8} {:>8}".format(
            "Date", "Status", "Check In", "Check Out", "Hours", "OT"
        )
    )
    print("-" * 90)
    for record in records:
        print(
            "{:<12} {:<10} {:<10} {:<10} {:>8.2f} {:>8.2f}".format(
                record["date"],
                record["status"],
                record.get("check_in", ""),
                record.get("check_out", ""),
                float(record.get("working_hours", 0)),
                float(record.get("overtime_hours", 0)),
            )
        )


def view_attendance(attendance):
    employee_id = input_required("\nEmployee ID: ")
    month = input_month("Month (YYYY-MM): ")
    records = month_records(attendance, employee_id, month)
    display_attendance_records(records)


def calculate_attendance_summary(attendance):
    employee_id = input_required("\nEmployee ID: ")
    month = input_month("Month (YYYY-MM): ")
    records = month_records(attendance, employee_id, month)
    summary = attendance_summary(records)
    print_summary(summary)


def print_summary(summary):
    print("\nAttendance Summary")
    print("Present Days:", summary["present"])
    print("Absent Days:", summary["absent"])
    print("Leave Days:", summary["leave"])
    print("Half Days:", summary["half_day"])
    print("Unpaid Days:", summary["unpaid_days"])
    print("Working Hours:", summary["working_hours"])
    print("Overtime Hours:", summary["overtime_hours"])


def attendance_menu(employees, attendance):
    while True:
        print("\nAttendance Management")
        print("1. Record attendance")
        print("2. Record check-in / check-out")
        print("3. View attendance by month")
        print("4. Calculate attendance summary")
        print("5. Back to main menu")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            record_attendance(employees, attendance)
        elif choice == "2":
            record_check_in_out(employees, attendance)
        elif choice == "3":
            view_attendance(attendance)
        elif choice == "4":
            calculate_attendance_summary(attendance)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


def calculate_payroll(employee, summary):
    monthly_salary = employee["monthly_basic_salary"]
    daily_salary = monthly_salary / WORKING_DAYS_PER_MONTH
    overtime_rate = daily_salary / STANDARD_WORKDAY_HOURS
    absence_deduction = daily_salary * summary["unpaid_days"]
    overtime_compensation = overtime_rate * summary["overtime_hours"]
    gross_salary = monthly_salary + overtime_compensation
    net_salary = gross_salary - absence_deduction

    return {
        "monthly_basic_salary": round(monthly_salary, 2),
        "daily_salary": round(daily_salary, 2),
        "overtime_rate": round(overtime_rate, 2),
        "unpaid_days": summary["unpaid_days"],
        "absence_deduction": round(absence_deduction, 2),
        "overtime_hours": summary["overtime_hours"],
        "overtime_compensation": round(overtime_compensation, 2),
        "gross_salary": round(gross_salary, 2),
        "net_salary": round(net_salary, 2),
    }


def find_payroll(payroll, employee_id, month):
    for record in payroll:
        if record["employee_id"].lower() == employee_id.lower() and record["month"] == month:
            return record
    return None


def format_money(value):
    return "{:.2f}".format(float(value))


def salary_slip_text(employee, month, summary, salary):
    lines = [
        "=" * 58,
        COMPANY_NAME,
        "Salary Slip",
        "=" * 58,
        "Employee ID: " + employee["employee_id"],
        "Employee Name: " + employee["name"],
        "Department: " + employee["department"],
        "Designation: " + employee["designation"],
        "Payroll Month: " + month,
        "-" * 58,
        "Monthly Basic Salary: " + format_money(salary["monthly_basic_salary"]),
        "Present Days: " + str(summary["present"]),
        "Absent Days: " + str(summary["absent"]),
        "Leave Days: " + str(summary["leave"]),
        "Half Days: " + str(summary["half_day"]),
        "Unpaid Days: " + str(summary["unpaid_days"]),
        "Total Working Hours: " + str(summary["working_hours"]),
        "Total Overtime Hours: " + str(salary["overtime_hours"]),
        "-" * 58,
        "Daily Salary: " + format_money(salary["daily_salary"]),
        "Overtime Rate: " + format_money(salary["overtime_rate"]),
        "Overtime Compensation: " + format_money(salary["overtime_compensation"]),
        "Unpaid Absence Deduction: " + format_money(salary["absence_deduction"]),
        "Gross Salary: " + format_money(salary["gross_salary"]),
        "Net Salary: " + format_money(salary["net_salary"]),
        "=" * 58,
    ]
    return "\n".join(lines)


def save_salary_slip(employee, month, text):
    safe_month = month.replace("-", "_")
    file_name = employee["employee_id"] + "_" + safe_month + "_salary_slip.txt"
    file_path = os.path.join(SALARY_SLIP_FOLDER, file_name)
    with open(file_path, "w") as file:
        file.write(text)
    return file_path


def process_payroll(employees, attendance, payroll):
    print("\nPayroll Processing")
    employee_id = input_required("Employee ID: ")
    employee = find_employee(employees, employee_id)

    if not employee:
        print("Employee not found.")
        return

    month = input_month("Payroll month (YYYY-MM): ")
    existing = find_payroll(payroll, employee_id, month)
    if existing:
        choice = input("Payroll already exists. Revise it? (y/n): ").strip().lower()
        if choice != "y":
            return
        payroll.remove(existing)

    records = month_records(attendance, employee_id, month)
    summary = attendance_summary(records)
    salary = calculate_payroll(employee, summary)
    slip_text = salary_slip_text(employee, month, summary, salary)
    slip_path = save_salary_slip(employee, month, slip_text)

    payroll_record = {
        "employee_id": employee["employee_id"],
        "employee_name": employee["name"],
        "department": employee["department"],
        "designation": employee["designation"],
        "month": month,
        "summary": summary,
        "salary": salary,
        "salary_slip": slip_path,
        "processed_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    payroll.append(payroll_record)
    save_records(PAYROLL_FILE, payroll)

    print("\nPayroll processed successfully.")
    print("Salary slip saved at:", slip_path)
    print("\n" + slip_text)


def payroll_menu(employees, attendance, payroll):
    while True:
        print("\nPayroll Processing")
        print("1. Process salary")
        print("2. Back to main menu")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            process_payroll(employees, attendance, payroll)
        elif choice == "2":
            break
        else:
            print("Invalid choice.")


def attendance_report(employees, attendance):
    employee_id = input_required("\nEmployee ID: ")
    employee = find_employee(employees, employee_id)
    if not employee:
        print("Employee not found.")
        return

    month = input_month("Month (YYYY-MM): ")
    records = month_records(attendance, employee_id, month)
    print("\nAttendance Report for", employee["name"], "-", month)
    display_attendance_records(records)
    print_summary(attendance_summary(records))


def monthly_payroll_report(payroll):
    month = input_month("\nPayroll month (YYYY-MM): ")
    records = [record for record in payroll if record["month"] == month]

    if not records:
        print("No payroll records found for this month.")
        return

    total_expense = 0
    print("\nMonthly Payroll Report -", month)
    print("-" * 80)
    print("{:<12} {:<22} {:<18} {:>12}".format("ID", "Name", "Department", "Net Salary"))
    print("-" * 80)
    for record in records:
        net_salary = record["salary"]["net_salary"]
        total_expense += net_salary
        print(
            "{:<12} {:<22} {:<18} {:>12.2f}".format(
                record["employee_id"],
                record["employee_name"],
                record["department"],
                net_salary,
            )
        )
    print("-" * 80)
    print("Total Monthly Salary Expense:", format_money(total_expense))


def salary_history(payroll):
    employee_id = input_required("\nEmployee ID: ")
    records = [
        record
        for record in payroll
        if record["employee_id"].lower() == employee_id.lower()
    ]

    if not records:
        print("No salary history found.")
        return

    print("\nEmployee Salary History")
    print("-" * 70)
    print("{:<10} {:>12} {:>12} {:>12}".format("Month", "Gross", "Deduction", "Net"))
    print("-" * 70)
    for record in sorted(records, key=lambda item: item["month"]):
        salary = record["salary"]
        print(
            "{:<10} {:>12.2f} {:>12.2f} {:>12.2f}".format(
                record["month"],
                salary["gross_salary"],
                salary["absence_deduction"],
                salary["net_salary"],
            )
        )


def department_summary(payroll):
    month = input_month("\nPayroll month (YYYY-MM): ")
    summary = {}

    for record in payroll:
        if record["month"] != month:
            continue
        department = record["department"]
        if department not in summary:
            summary[department] = {"employees": 0, "expense": 0}
        summary[department]["employees"] += 1
        summary[department]["expense"] += record["salary"]["net_salary"]

    if not summary:
        print("No payroll records found for this month.")
        return

    print("\nDepartment-Wise Payroll Summary -", month)
    print("-" * 65)
    print("{:<25} {:>12} {:>15}".format("Department", "Employees", "Expense"))
    print("-" * 65)
    for department, values in summary.items():
        print(
            "{:<25} {:>12} {:>15.2f}".format(
                department,
                values["employees"],
                values["expense"],
            )
        )


def total_monthly_expense(payroll):
    month = input_month("\nPayroll month (YYYY-MM): ")
    total = 0
    for record in payroll:
        if record["month"] == month:
            total += record["salary"]["net_salary"]
    print("Total Monthly Salary Expense for", month + ":", format_money(total))


def employee_attendance_summary(employees, attendance):
    month = input_month("\nMonth (YYYY-MM): ")

    if not employees:
        print("No employees found.")
        return

    print("\nEmployee Attendance Summary -", month)
    print("-" * 95)
    print(
        "{:<12} {:<22} {:>8} {:>8} {:>8} {:>8} {:>10}".format(
            "ID", "Name", "Present", "Absent", "Leave", "Half", "Overtime"
        )
    )
    print("-" * 95)
    for employee in employees:
        records = month_records(attendance, employee["employee_id"], month)
        summary = attendance_summary(records)
        print(
            "{:<12} {:<22} {:>8} {:>8} {:>8} {:>8} {:>10.2f}".format(
                employee["employee_id"],
                employee["name"],
                summary["present"],
                summary["absent"],
                summary["leave"],
                summary["half_day"],
                summary["overtime_hours"],
            )
        )


def reports_menu(employees, attendance, payroll):
    while True:
        print("\nReports")
        print("1. Employee attendance report")
        print("2. Monthly payroll report")
        print("3. Employee salary history")
        print("4. Department-wise payroll summary")
        print("5. Total monthly salary expense")
        print("6. Employee attendance summary")
        print("7. Back to main menu")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            attendance_report(employees, attendance)
        elif choice == "2":
            monthly_payroll_report(payroll)
        elif choice == "3":
            salary_history(payroll)
        elif choice == "4":
            department_summary(payroll)
        elif choice == "5":
            total_monthly_expense(payroll)
        elif choice == "6":
            employee_attendance_summary(employees, attendance)
        elif choice == "7":
            break
        else:
            print("Invalid choice.")


def main_menu():
    initialize_files()
    employees = load_records(EMPLOYEES_FILE)
    attendance = load_records(ATTENDANCE_FILE)
    payroll = load_records(PAYROLL_FILE)

    while True:
        print("\n" + "=" * 60)
        print("Employee Attendance & Payroll Management System")
        print("=" * 60)
        print("1. Employee Management")
        print("2. Attendance Management")
        print("3. Payroll Processing")
        print("4. Reports")
        print("5. Save and Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            employee_menu(employees)
        elif choice == "2":
            attendance_menu(employees, attendance)
        elif choice == "3":
            payroll_menu(employees, attendance, payroll)
        elif choice == "4":
            reports_menu(employees, attendance, payroll)
        elif choice == "5":
            save_records(EMPLOYEES_FILE, employees)
            save_records(ATTENDANCE_FILE, attendance)
            save_records(PAYROLL_FILE, payroll)
            print("Data saved. Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()
