import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import os
from datetime import datetime
import mysql.connector
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Global variables to store Entry widgets
entry_username = None
entry_dob = None
login_entry_username = None
login_entry_dob = None
entry_file_path = None
entry_upload_date = None

# Database connection
def create_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="Hamrith@13",  # Replace with your MySQL password
        database="hospital_db"
    )

# Patient management
def insert_patient(username, dob, patient_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (patient_id, username, dob) VALUES (%s, %s, %s)",
        (patient_id, username, dob)
    )
    conn.commit()
    conn.close()

def get_patient(username, dob):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT patient_id FROM patients WHERE username = %s AND dob = %s",
        (username, dob)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Document management
def insert_document(patient_id, document_name, file_path, upload_date):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (patient_id, document_name, file_path, upload_date) VALUES (%s, %s, %s, %s)",
        (patient_id, document_name, file_path, upload_date)
    )
    conn.commit()
    conn.close()

# Google Drive upload
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    return creds

def upload_to_drive(file_path, upload_date):
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'description': f'Uploaded on {upload_date}'
    }
    media = MediaFileUpload(file_path)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Patient ID generation
def generate_patient_id(username, dob):
    combined = f"{username}_{dob}"
    patient_id = hashlib.sha256(combined.encode()).hexdigest()[:10]
    return patient_id

# User registration
def register_user():
    username = entry_username.get()
    dob = entry_dob.get()

    if not username or not dob:
        messagebox.showerror("Input Error", "Please enter both Username and Date of Birth.")
        return

    patient_id = generate_patient_id(username, dob)

    if get_patient(username, dob):
        messagebox.showerror("Registration Error", "User already registered.")
        return

    insert_patient(username, dob, patient_id)
    messagebox.showinfo("Registration Success", f"Registration successful!\nYour Patient ID: {patient_id}")
    clear_registration_form()

# User login
def login_user():
    username = login_entry_username.get()
    dob = login_entry_dob.get()

    patient_id = get_patient(username, dob)

    if patient_id:
        messagebox.showinfo("Login Success", f"Welcome back, {username}!\nYour Patient ID: {patient_id}")
        show_file_upload_form()
    else:
        messagebox.showerror("Login Error", "Invalid Username or Date of Birth.")

# File upload
def upload_file_with_details():
    file_path = entry_file_path.get()
    upload_date = entry_upload_date.get()
    username = login_entry_username.get()
    dob = login_entry_dob.get()

    patient_id = get_patient(username, dob)
    document_name = os.path.basename(file_path)

    if not file_path or not upload_date:
        messagebox.showerror("Input Error", "Please provide all details before uploading.")
        return

    try:
        file_id = upload_to_drive(file_path, upload_date)
        insert_document(patient_id, document_name, file_path, upload_date)
        messagebox.showinfo("Success", f"File uploaded successfully.\nFile ID: {file_id}\nUpload Date: {upload_date}")
    except Exception as e:
        messagebox.showerror("Upload Error", f"An error occurred while uploading the file:\n{e}")

# UI: Registration form
def show_registration_form():
    clear_widgets()

    tk.Label(root, text="Username:").pack(pady=5)
    global entry_username
    entry_username = tk.Entry(root)
    entry_username.pack(pady=5)

    tk.Label(root, text="Date of Birth (YYYY-MM-DD):").pack(pady=5)
    global entry_dob
    entry_dob = tk.Entry(root)
    entry_dob.pack(pady=5)

    tk.Button(root, text="Register", command=register_user).pack(pady=20)
    tk.Button(root, text="Go to Login", command=show_login_form).pack()

def clear_registration_form():
    entry_username.delete(0, tk.END)
    entry_dob.delete(0, tk.END)

# UI: Login form
def show_login_form():
    clear_widgets()

    tk.Label(root, text="Username:").pack(pady=5)
    global login_entry_username
    login_entry_username = tk.Entry(root)
    login_entry_username.pack(pady=5)

    tk.Label(root, text="Date of Birth (YYYY-MM-DD):").pack(pady=5)
    global login_entry_dob
    login_entry_dob = tk.Entry(root)
    login_entry_dob.pack(pady=5)

    tk.Button(root, text="Login", command=login_user).pack(pady=20)
    tk.Button(root, text="Go to Registration", command=show_registration_form).pack()

# UI: File upload form
def show_file_upload_form():
    clear_widgets()

    tk.Label(root, text="File Upload:").pack(pady=20)

    tk.Label(root, text="Select File:").pack(pady=5)
    global entry_file_path
    entry_file_path = tk.Entry(root, width=40)
    entry_file_path.pack(pady=5)
    tk.Button(root, text="Browse", command=browse_file).pack(pady=5)

    tk.Label(root, text="Upload Date:").pack(pady=5)
    global entry_upload_date
    entry_upload_date = tk.Entry(root)
    entry_upload_date.pack(pady=5)
    entry_upload_date.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    tk.Button(root, text="Upload File", command=upload_file_with_details).pack(pady=20)
    tk.Button(root, text="Logout", command=show_login_form).pack(pady=20)

def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def clear_widgets():
    for widget in root.winfo_children():
        widget.destroy()

# Initialize the main window
root = tk.Tk()
root.title("Patient Registration System")

show_registration_form()

root.mainloop()
