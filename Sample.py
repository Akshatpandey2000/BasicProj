import pandas as pd
import os

# FILE_PATH =r"C:\Users\532985\OneDrive - Cognizant\Desktop\WindSurfCode\employees.xlsx"
FILE_PATH = r"C:\Users\532985\Downloads\WindSurf\employees.xlsx"

def load_employees():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH)
    else:
        # Create a new DataFrame if file doesn't exist
        return pd.DataFrame(columns=['ID', 'Name', 'Department', 'Salary'])

def save_employees(df):
    df.to_excel(FILE_PATH, index=False)

def create_employee(emp_id, name, department, salary):
    df = load_employees()
    if emp_id in df['ID'].values:
        print(f"Employee with ID {emp_id} already exists.")
        return
    new_record = {'ID': emp_id, 'Name': name, 'Department': department, 'Salary': salary}
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    save_employees(df)
    print("Employee created.")

def read_employees():
    df = load_employees()
    print(df)

def update_employee(emp_id, name=None, department=None, salary=None):
    df = load_employees()
    if emp_id not in df['ID'].values:
        print(f"Employee with ID {emp_id} does not exist.")
        return
    idx = df.index[df['ID'] == emp_id][0]
    if name: df.at[idx, 'Name'] = name
    if department: df.at[idx, 'Department'] = department
    if salary: df.at[idx, 'Salary'] = salary
    save_employees(df)
    print("Employee updated.")

def delete_employee(emp_id):
    df = load_employees()
    if emp_id not in df['ID'].values:
        print(f"Employee with ID {emp_id} does not exist.")
        return
    df = df[df['ID'] != emp_id]
    save_employees(df)
    print("Employee deleted.")

# Example usage:
if __name__ == "__main__":
    # Create
    create_employee(1, "Alka", "HR", 50000)
    create_employee(2, "Akshat", "IT", 60000)
    create_employee(3, "Ankit", "IT", 40000)
    create_employee(4, "Anupam", "IT", 50000)
    create_employee(5, "Lekshmi", "IT", 60000)
    create_employee(6, "Pavani", "IT", 70000)
    create_employee(7, "Naresh", "IT", 80000)
    create_employee(8, "Rahul", "IT", 90000)
    create_employee(9, "Bala", "IT", 80000)
    create_employee(10, "Prashant", "IT", 90000)
    create_employee(11, "Radhika", "IT", 70000)
    create_employee(12, "Mounika", "HR", 60000)
    # Read
    read_employees()
    # Update
    update_employee(1, salary=55000)
    # Delete
    delete_employee(2)
    # Read again
    read_employees()
