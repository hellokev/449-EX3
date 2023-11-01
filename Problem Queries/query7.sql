-- Task: Add new classes and sections
-- Endpoint: POST https://localhost:5000/registrar/new_class
-- body: {
    -- "class_code": "CPSC335",
    -- "section_number": "01",
    -- "class_name": "Algorithm Engineering",
    -- "department": "Computer Science",
    -- "auto_enrollment": TRUE,
    -- "max_enrollment": 30,
    -- "current_enrollment": 0,
    -- "max_waitlist": 15,
    -- "current_waitlist": 0,
    -- "c_instructor_id": "100",
-- }

-- Given the information above in the request body
-- Create new class and section
INSERT INTO Class (class_code, section_number, class_name, department, auto_enrollment, max_enrollment, current_enrollment, max_waitlist, current_waitlist, c_instructor_id)
VALUES ('CPSC335', '01', 'Algorithm Engineering', 'Computer Science', TRUE, 30, 0, 15, 0, '100')