-- Task: View students who have dropped the class
-- Endpoint: GET https://localhost:5000/instructor/dropped/?instructor_id={instructor_id}&class_code={class_code}&section_number={section_number}

-- Given instructor_id="100" class_code='CPSC449' and section_number='01'

-- Get all students who have dropped a professors class
SELECT student_id, s_first_name, s_last_name, class_code, section_number
FROM Instructor, Class, Dropped, Student
WHERE Instructor.instructor_id == "100"
AND Class.class_code =='CPSC449'
AND Class.section_number =='01'
AND Instructor.instructor_id == Class.c_instructor_id
AND  Class.class_code == Dropped.d_class_code
And Class.section_number == Dropped.d_section_number
AND Dropped.d_student_id == student_id


