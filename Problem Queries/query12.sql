-- Task: Remove themselves from a waiting list
-- Endpoint: DELETE https://localhost:5000/student/remove_from_waitlist/?student_id={student_id}&class_code={class_code}&section_number={section_number}

-- Given student_id='666666666' class_code='PHYS202' and section_number='02'

-- Check if student actually on waitlist, if this returns a value then we can proceed
SELECT *
FROM Waitlist
WHERE w_student_id="666666666"
AND w_class_code == "PHYS202"
AND w_section_number == "02"

-- If student not on waitlist dont do the below steps

-- Remove self from waitlist
DELETE FROM Waitlist
WHERE w_student_id="666666666"
AND w_class_code == "PHYS202"
AND w_section_number == "02"

-- Decremenet number of students on waitlist for that class 
UPDATE Class
SET current_waitlist = current_waitlist - 1
Where class_code='PHYS202'
AND section_number='02'
AND current_waitlist > 0

-- Decremenet number of classes the student is waitlisted for
UPDATE Student
SET num_waitlist = num_waitlist - 1
WHERE student_id == "666666666"
AND num_waitlist > 0