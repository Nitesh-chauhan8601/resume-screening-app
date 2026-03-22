CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'recruiter') NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_descriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description_text TEXT NOT NULL,
    required_skills TEXT,
    keywords TEXT,
    min_experience INT NOT NULL DEFAULT 0,
    qualifications TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_recruiter
        FOREIGN KEY (recruiter_id) REFERENCES users(id)
);

CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    candidate_name VARCHAR(150),
    email VARCHAR(120),
    phone VARCHAR(20),
    skills TEXT,
    education TEXT,
    experience_text TEXT,
    experience_years DECIMAL(4,1) NOT NULL DEFAULT 0.0,
    certifications TEXT,
    raw_text LONGTEXT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    parse_status ENUM('pending', 'success', 'failed') NOT NULL DEFAULT 'pending',
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_resume_recruiter
        FOREIGN KEY (recruiter_id) REFERENCES users(id)
);

CREATE TABLE screening_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    jd_id INT NOT NULL,
    skill_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    experience_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    education_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    similarity_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    suitability_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    ranking INT DEFAULT NULL,
    recommendation VARCHAR(30),
    matched_skills TEXT,
    missing_skills TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_result_resume
        FOREIGN KEY (resume_id) REFERENCES resumes(id),
    CONSTRAINT fk_result_job
        FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
);

CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    jd_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    date_range VARCHAR(50),
    file_path VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_user
        FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_report_job
        FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
);

CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    module VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    error_trace TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE issue_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    severity ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    status ENUM('open', 'in_progress', 'resolved') NOT NULL DEFAULT 'open',
    created_by INT NOT NULL,
    assigned_to INT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME DEFAULT NULL,
    CONSTRAINT fk_ticket_creator
        FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_ticket_assigned
        FOREIGN KEY (assigned_to) REFERENCES users(id)
);

CREATE INDEX idx_jobs_recruiter ON job_descriptions(recruiter_id);
CREATE INDEX idx_resumes_recruiter ON resumes(recruiter_id);
CREATE INDEX idx_resumes_status ON resumes(parse_status);
CREATE INDEX idx_results_jd_score ON screening_results(jd_id, suitability_score);
CREATE INDEX idx_reports_job ON reports(jd_id);
CREATE INDEX idx_logs_level_created ON system_logs(level, created_at);
CREATE INDEX idx_tickets_status ON issue_tickets(status);
