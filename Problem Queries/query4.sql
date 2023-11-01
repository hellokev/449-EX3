-- Task: View current enrollment for their classes
-- Endpoint: GET https://localhost:5000/instructor/enrollment/?instructor_id={instructor_id}

-- Given instructor_id="100"

-- Get all students that are enrolled for any of the professors classes
SELECT student_id, s_first_name, s_last_name, class_code, section_number, class_name
FROM Instructor, Class, Enroll, Student
WHERE Instructor.instructor_id == "100"
AND Instructor.instructor_id == Class.c_instructor_id
AND  Class.class_code == Enroll.e_class_code
And Class.section_number == Enroll.e_section_number
AND Enroll.e_student_id == student_id


