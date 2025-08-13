import streamlit as st
import pandas as pd
import os
import datetime
from Sample import load_employees, save_employees, create_employee, update_employee, delete_employee

# --- Messaging Service Notification Placeholder ---
def send_message_notification(message):
    # Integrate with Slack, Teams, or SMS here
    # For Slack: Use requests.post() to send to a webhook URL
    # For SMS: Use Twilio's Python client
    pass

# Audit log file
AUDIT_LOG = os.path.join(os.path.dirname(__file__), 'audit.log')

# Helper to append audit log
def append_audit_log(entry):
    with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')

def read_audit_log():
    if os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

# Notification log file
NOTIF_LOG = os.path.join(os.path.dirname(__file__), 'notifications.log')

# Initialize notification history in session state
if 'notification_history' not in st.session_state:
    st.session_state['notification_history'] = []

def append_notification_log(msg):
    with open(NOTIF_LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def read_notification_log():
    if os.path.exists(NOTIF_LOG):
        with open(NOTIF_LOG, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

# FILE_PATH = r"C:\Users\532985\OneDrive - Cognizant\Desktop\WindSurfCode\employees.xlsx"
FILE_PATH = r"C:\Users\532985\Downloads\WindSurf\employees.xlsx"
st.title("Employee Records CRUD App")

# Role-based access control
role = st.selectbox("Select your role", ["Administrator", "HR"], key="role_select")

# Define allowed operations per role
if role == "Administrator":
    allowed_ops = ["Create", "Read", "Update", "Delete"]
else:  # HR
    allowed_ops = ["Create", "Read"]

operation = st.sidebar.selectbox("Choose Operation", allowed_ops)

# Load current employee data
def get_employees():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH)
    else:
        return pd.DataFrame(columns=['ID', 'Name', 'Department', 'Salary'])

# --- Notification History Panel ---
st.markdown("---")
st.subheader("Notification History (this session)")
for note in st.session_state['notification_history']:
    st.markdown(f"- {note}")

# --- Full Notification Log ---
st.markdown("---")
st.subheader("Full Notification Log (all sessions)")
full_log = read_notification_log()
if full_log:
    for note in full_log:
        st.markdown(f"- {note}")
else:
    st.info("No notifications logged yet.")

# --- Audit Trail ---
st.markdown("---")
st.subheader("Audit Trail (all changes to employee records)")
audit_log = read_audit_log()
if audit_log:
    for entry in audit_log[::-1]:  # Show most recent first
        st.code(entry)
else:
    st.info("No audit trail entries yet.")

if operation == "Create":
    st.header("Add New Employee")
    emp_id = st.number_input("Employee ID", min_value=1, step=1)
    name = st.text_input("Name")
    department = st.text_input("Department")
    salary = st.number_input("Salary", min_value=0, step=1000)
    if st.button("Create"):
        # Audit: log new values
        new_vals = {'ID': emp_id, 'Name': name, 'Department': department, 'Salary': salary}
        timestamp = datetime.datetime.now().isoformat()
        audit_entry = f"[{timestamp}] CREATE by {role} | New: {new_vals}"
        append_audit_log(audit_entry)
        create_employee(emp_id, name, department, salary)
        msg = f"Onboarding: Employee {name} (ID: {emp_id}) has been successfully added."
        st.success(msg)
        st.session_state['notification_history'].append(msg)
        append_notification_log(msg)
        # --- Email and Messaging Notification ---
        subject = "Employee Onboarding Notification"
        body = f"Onboarding: Employee {name} (ID: {emp_id}) has been added by {role}."
        
        send_message_notification(body)

elif operation == "Read":
    st.header("All Employees")
    df = get_employees()
    if not df.empty:
        # Search by name or department
        search_text = st.text_input("Search by Name or Department")
        if search_text:
            df = df[df['Name'].str.contains(search_text, case=False, na=False) |
                    df['Department'].str.contains(search_text, case=False, na=False)]
        # Filter by department
        departments = df['Department'].dropna().unique().tolist()
        selected_dept = st.multiselect("Filter by Department", departments, default=departments)
        if selected_dept:
            df = df[df['Department'].isin(selected_dept)]
        # Filter by salary range
        if not df['Salary'].dropna().empty:
            min_salary = int(df['Salary'].min())
            max_salary = int(df['Salary'].max())
            salary_range = st.slider("Filter by Salary", min_salary, max_salary, (min_salary, max_salary), step=1000)
            df = df[(df['Salary'] >= salary_range[0]) & (df['Salary'] <= salary_range[1])]
        # --- Paging ---
        page_size = st.selectbox("Records per page", [5, 10, 20, 50, 100], index=1)
        total_records = len(df)
        total_pages = (total_records - 1) // page_size + 1
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        start_idx = (page_num - 1) * page_size
        end_idx = start_idx + page_size
        st.dataframe(df.iloc[start_idx:end_idx].reset_index(drop=True))
        st.caption(f"Showing page {page_num} of {total_pages}, records {start_idx+1}-{min(end_idx, total_records)} of {total_records}")
    else:
        st.info("No employee records found.")

elif operation == "Update":
    st.header("Update Employee")
    df = get_employees()
    if df.empty:
        st.info("No employees to update.")
    else:
        emp_id = st.selectbox("Select Employee ID", df['ID'].tolist())
        name = st.text_input("New Name", value=str(df[df['ID']==emp_id]['Name'].values[0]))
        department = st.text_input("New Department", value=str(df[df['ID']==emp_id]['Department'].values[0]))
        salary = st.number_input("New Salary", min_value=0, step=1000, value=int(df[df['ID']==emp_id]['Salary'].values[0]))
        if st.button("Update"):
            # Audit: log old and new values
            old_vals = df[df['ID']==emp_id].iloc[0].to_dict()
            new_vals = {'ID': emp_id, 'Name': name, 'Department': department, 'Salary': salary}
            timestamp = datetime.datetime.now().isoformat()
            audit_entry = f"[{timestamp}] UPDATE by {role} | Old: {old_vals} | New: {new_vals}"
            append_audit_log(audit_entry)
            update_employee(emp_id, name, department, salary)
            msg = f"Update: Employee ID {emp_id} has been updated."
            st.info(msg)
            st.session_state['notification_history'].append(msg)
            append_notification_log(msg)
            # --- Email and Messaging Notification ---
            subject = "Employee Update Notification"
            body = f"Update: Employee ID {emp_id} has been updated by {role}.\nOld: {old_vals}\nNew: {new_vals}"
            
            send_message_notification(body)

elif operation == "Delete":
    st.header("Delete Employee")
    df = get_employees()
    if df.empty:
        st.info("No employees to delete.")
    else:
        emp_id = st.selectbox("Select Employee ID", df['ID'].tolist())
        if st.button("Delete"):
            # Audit: log old values
            old_vals = df[df['ID']==emp_id].iloc[0].to_dict()
            timestamp = datetime.datetime.now().isoformat()
            audit_entry = f"[{timestamp}] DELETE by {role} | Old: {old_vals}"
            append_audit_log(audit_entry)
            delete_employee(emp_id)
            msg = f"Exit: Employee ID {emp_id} has been removed from the system."
            st.warning(msg)
            st.session_state['notification_history'].append(msg)
            append_notification_log(msg)
            # --- Email and Messaging Notification ---
            subject = "Employee Exit Notification"
            body = f"Exit: Employee ID {emp_id} has been removed from the system by {role}.\nOld: {old_vals}"
            
            send_message_notification(body)
