

USE hospital_db;

CREATE TABLE patients (
    patient_id VARCHAR(10) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    dob DATE NOT NULL
);


CREATE TABLE documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(10),
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    upload_date DATETIME NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
