-- Task: View their current position on the waiting list
-- Endpoint: GET https://localhost:5000/student/waitlist_position/?student_id={student_id}&class_code={class_code}&section_number={section_number}

-- Given student_id="11111111" class_code='ENGL205' and section_number='01'

-- Get all students on waitlist for that class and section
SELECT w_student_id, timestamp
FROM Waitlist
WHERE w_class_code == "MATH101"
AND w_section_number == "02"

-- Then in python create a dictionary with the student_id as the key and timestamp as the value
-- then use the funciton found in file "./get_position_on_waitlist.py" to return the position