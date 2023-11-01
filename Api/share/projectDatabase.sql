CREATE TABLE Student (
    s_first_name VARCHAR(255), 
    s_last_name VARCHAR(255), 
    student_id VARCHAR(255) PRIMARY KEY,
    num_waitlist TINYINT
);

CREATE TABLE Instructor (
    instructor_id VARCHAR(255) PRIMARY KEY,
    i_first_name VARCHAR(255),
    i_last_name VARCHAR(255)
);

CREATE TABLE Class (
    class_code CHAR(7),
    section_number CHAR(2),
    class_name VARCHAR(255),
    department VARCHAR(255),
    auto_enrollment BOOLEAN,
    max_enrollment TINYINT,
    current_enrollment TINYINT,
    max_waitlist TINYINT,
    current_waitlist TINYINT,
    c_instructor_id VARCHAR(255),
    PRIMARY KEY (class_code, section_number),
    FOREIGN KEY (c_instructor_id) REFERENCES Instructor(instructor_id)
);

CREATE TABLE Enroll (
    e_student_id VARCHAR(255),
    e_class_code CHAR(7),
    e_section_number CHAR(2),
    PRIMARY KEY (e_student_id, e_class_code, e_section_number),
    FOREIGN KEY (e_student_id) REFERENCES Student(student_id),
    FOREIGN KEY (e_class_code, e_section_number) REFERENCES Class(class_code, section_number)
);

CREATE TABLE Waitlist (
    w_student_id VARCHAR(255),
    w_class_code CHAR(7),
    w_section_number CHAR(2),
    timestamp DATETIME,
    PRIMARY KEY (w_student_id, w_class_code, w_section_number),
    FOREIGN KEY (w_student_id) REFERENCES Student(student_id),
    FOREIGN KEY (w_class_code, w_section_number) REFERENCES Class(class_code, section_number)
);

CREATE TABLE Dropped (
    d_student_id VARCHAR(255),
    d_class_code CHAR(7),
    d_section_number CHAR(2),
    PRIMARY KEY (d_student_id, d_class_code, d_section_number),
    FOREIGN KEY (d_student_id) REFERENCES Student(student_id),
    FOREIGN KEY (d_class_code, d_section_number) REFERENCES Class(class_code, section_number)
);




-- Insert six students with names starting with 'S'
INSERT INTO Student (s_first_name, s_last_name, student_id, num_waitlist)
VALUES
    ('Sam', 'Doe', '11111111', 0),
    ('Samantha', 'Smith', '22222222', 1),
    ('Sandra', 'Johnson', '33333333', 2),
    ('Steve', 'Brown', '444444444', 0),
    ('Sylvia', 'Wilson', '555555555', 1),
    ('Scott', 'Davis', '666666666', 2);

-- Insert three professors with names starting with 'I'
INSERT INTO Instructor (instructor_id, i_first_name, i_last_name)
VALUES
    ('100', 'Irene', 'Doe'),
    ('101', 'Isaac', 'Smith'),
    ('102', 'Isabella', 'Johnson');

-- Insert six courses
INSERT INTO Class (class_code, section_number, class_name, department, auto_enrollment, max_enrollment, current_enrollment, max_waitlist, current_waitlist, c_instructor_id)
VALUES
    ('CPSC449', '01', 'Database Systems', 'Computer Science', TRUE, 30, 2, 15, 0, '100'),
    ('CPSC449', '02', 'Database Systems', 'Computer Science', TRUE, 30, 1, 15, 0, '101'),
    ('MATH101', '01', 'Introduction to Calculus', 'Mathematics', TRUE, 25, 2, 15, 0, '102'),
    ('MATH101', '02', 'Introduction to Calculus', 'Mathematics', TRUE, 25, 25, 15, 3, '102'),
    ('ENGL205', '01', 'American Literature', 'English', TRUE, 35, 3, 15, 0, '100'),
    ('PHYS202', '01', 'Physics II', 'Physics', TRUE, 40, 2, 15, 0, '101'),
    ('PHYS202', '02', 'Physics II', 'Physics', TRUE, 40, 40, 15, 3, '101'),
    ('CHEM101', '01', 'Introduction to Chemistry', 'Chemistry', TRUE, 20, 2, 15, 0, '102');

-- Enroll every student in two classes
INSERT INTO Enroll (e_student_id, e_class_code, e_section_number)
VALUES
    ('11111111', 'CPSC449', '01'),
    ('11111111', 'MATH101', '01'),
    
    ('22222222', 'CPSC449', '02'),
    ('22222222', 'ENGL205', '01'),
    
    ('33333333', 'MATH101', '01'),
    ('33333333', 'PHYS202', '01'),
    
    ('444444444', 'ENGL205', '01'),
    ('444444444', 'CHEM101', '01'),
    
    ('555555555', 'PHYS202', '01'),
    ('555555555', 'CPSC449', '01'),
    
    ('666666666', 'CHEM101', '01'),
    ('666666666', 'ENGL205', '01');

-- Add students to the waitlist of classes they are not enrolled in
-- Each student is added to the waitlist of a class they are not enrolled in
-- The timestamp is set to the current date and time for simplicity

-- Sam is added to the waitlist of 'ENGL205' section '01' on a specific date
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES
    ('11111111', 'MATH101', '02', '2023-09-15 10:00:00');

-- Samantha is added to the waitlist of 'PHYS202' section '01' on a specific date
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES
    ('22222222', 'MATH101', '02', '2023-09-15 11:00:00');

-- Sandra is added to the waitlist of 'CHEM101' section '01' on a specific date
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES
    ('33333333', 'MATH101', '02', '2023-09-15 12:00:00');

-- Steve is added to the waitlist of 'CPSC449' section '01' on a specific date
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES
    ('444444444', 'PHYS202', '02', '2023-09-15 13:00:00');

-- Sylvia is added to the waitlist of 'MATH101' section '01' on a specific date
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES
    ('555555555', 'PHYS202', '02', '2023-09-15 14:00:00');

-- Scott is added to the waitlist of 'CPSC449' section '02' on a specific date
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES
    ('666666666', 'PHYS202', '02', '2023-09-15 15:00:00');


-- Have every student drop one class they are not enrolled in

-- Sam drops the class 'CHEM101' section '01'
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES
    ('11111111', 'CHEM101', '01');

-- Samantha drops the class 'CPSC449' section '02'
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES
    ('22222222', 'CPSC449', '01');

-- Sandra drops the class 'ENGL205' section '01'
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES
    ('33333333', 'ENGL205', '01');

-- Steve drops the class 'MATH101' section '01'
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES
    ('444444444', 'MATH101', '01');

-- Sylvia drops the class 'PHYS202' section '01'
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES
    ('555555555', 'CHEM101', '01');

-- Scott drops the class 'CHEM101' section '01'
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES
    ('666666666', 'MATH101', '01');
