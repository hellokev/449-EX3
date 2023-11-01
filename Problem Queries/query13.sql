-- Task: View the current waiting list for the course
-- Endpoint: GET https://localhost:5000/instructor/waitlist_for_class/?instructor_id={instructor_id}&class_code={class_code}&section_number={section_number}

-- Given instructor_id="102" class_code='MATH101' and section_number='02'

-- Get all students on the waitlist student_id, s_first_name, s_last_name, class_code and section_number 
-- for a specific class
SELECT student_id, s_first_name, s_last_name, class_code, section_number
FROM Instructor, Class, Waitlist, Student
WHERE Instructor.instructor_id == "102"
AND Class.class_code =='MATH101'
AND Class.section_number =='02'
AND Instructor.instructor_id == Class.c_instructor_id
AND  Class.class_code == Waitlist.w_class_code
And Class.section_number == Waitlist.w_section_number
AND Waitlist.w_student_id == student_id