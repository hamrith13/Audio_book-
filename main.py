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


class PatientApp: 
    def __init__(self,root):
        self.root = root
        self.root.title("Patient Registration System")

       
        self.entry_username = None
        self.entry_dob = None
        self.login_entry_username = None
        self.login_entry_dob = None
        self.entry_file_path = None
        self.entry_upload_date = None

        
        self.logged_in_username = None
        self.logged_in_dob = None

        self.show_registration_form()


    def show_registration_form(self):
        self.clear_widgets()

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.entry_username = tk.Entry(self.root)
        self.entry_username.pack(pady=5)

        tk.Label(self.root, text="Date of Birth (YYYY-MM-DD):").pack(pady=5)
        self.entry_dob = tk.Entry(self.root)
        self.entry_dob.pack(pady=5)

        tk.Button(self.root, text="Register", command=self.register_user).pack(pady=20)
        tk.Button(self.root, text="Go to Login", command=self.show_login_form).pack()

    def register_user(self):
        username = self.entry_username.get()
        dob = self.entry_dob.get()

        if not username or not dob:
            messagebox.showerror("Input Error", "Please enter both Username and Date of Birth.")
            return

        patient_id = self.generate_patient_id(username, dob)

        if self.get_patient(username, dob):
            messagebox.showerror("Registration Error", "User already registered.")
            return

        self.insert_patient(username, dob, patient_id)
        messagebox.showinfo("Registration Success", f"Registration successful!\nYour Patient ID: {patient_id}")
        self.clear_registration_form()

    # UI: Login form
    def show_login_form(self):
        self.clear_widgets()

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.login_entry_username = tk.Entry(self.root)
        self.login_entry_username.pack(pady=5)

        tk.Label(self.root, text="Date of Birth (YYYY-MM-DD):").pack(pady=5)
        self.login_entry_dob = tk.Entry(self.root)
        self.login_entry_dob.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login_user).pack(pady=20)
        tk.Button(self.root, text="Go to Registration", command=self.show_registration_form).pack()

    def login_user(self):
        username = self.login_entry_username.get()
        dob = self.login_entry_dob.get()

        patient_id = self.get_patient(username, dob)

        if patient_id:
            self.logged_in_username = username  # Store the logged-in user's data
            self.logged_in_dob = dob
            messagebox.showinfo("Login Success", f"Welcome back, {username}!\nYour Patient ID: {patient_id}")
            self.show_file_upload_form()
        else:
            messagebox.showerror("Login Error", "Invalid Username or Date of Birth.")

    # UI: File upload form
    def show_file_upload_form(self):
        self.clear_widgets()

        tk.Label(self.root, text="File Upload:").pack(pady=20)

        tk.Label(self.root, text="Select File:").pack(pady=5)
        self.entry_file_path = tk.Entry(self.root, width=40)
        self.entry_file_path.pack(pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_file).pack(pady=5)

        tk.Label(self.root, text="Upload Date:").pack(pady=5)
        self.entry_upload_date = tk.Entry(self.root)
        self.entry_upload_date.pack(pady=5)
        self.entry_upload_date.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        tk.Button(self.root, text="Upload File", command=self.upload_file_with_details).pack(pady=20)
        tk.Button(self.root, text="Logout", command=self.show_login_form).pack(pady=20)

    def upload_file_with_details(self):
        file_path = self.entry_file_path.get()
        upload_date = self.entry_upload_date.get()

        if not file_path or not upload_date:
            messagebox.showerror("Input Error", "Please provide all details before uploading.")
            return

        patient_id = self.get_patient(self.logged_in_username, self.logged_in_dob)
        document_name = os.path.basename(file_path)

        try:
            file_id = self.upload_to_drive(file_path, upload_date)
            self.insert_document(patient_id, document_name, file_path, upload_date)
            messagebox.showinfo("Success", f"File uploaded successfully.\nFile ID: {file_id}\nUpload Date: {upload_date}")
        except Exception as e:
            messagebox.showerror("Upload Error", f"An error occurred while uploading the file:\n{e}")

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.entry_file_path.delete(0, tk.END)
            self.entry_file_path.insert(0, file_path)

    
    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    
    def clear_registration_form(self):
        self.entry_username.delete(0, tk.END)
        self.entry_dob.delete(0, tk.END)

    def generate_patient_id(self, username, dob):
        combined = f"{username}_{dob}"
        return hashlib.sha256(combined.encode()).hexdigest()[:10]

    def create_db_connection(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Hamrith@13",
            database="hospital_db"
        )

    def insert_patient(self, username, dob, patient_id):
        conn = self.create_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients (patient_id, username, dob) VALUES (%s, %s, %s)",
            (patient_id, username, dob)
        )
        conn.commit()
        conn.close()

    def get_patient(self, username, dob):
        conn = self.create_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT patient_id FROM patients WHERE username = %s AND dob = %s",
            (username, dob)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def insert_document(self, patient_id, document_name, file_path, upload_date):
        conn = self.create_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (patient_id, document_name, file_path, upload_date) VALUES (%s, %s, %s, %s)",
            (patient_id, document_name, file_path, upload_date)
        )
        conn.commit()
        conn.close()

    def get_credentials(self):
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

    def upload_to_drive(self, file_path, upload_date):
        creds = self.get_credentials()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': os.path.basename(file_path),
            'description': f'Uploaded on {upload_date}'
        }
        media = MediaFileUpload(file_path)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')


root = tk.Tk()
app = PatientApp(root)
root.mainloop()
