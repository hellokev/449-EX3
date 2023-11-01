-- Task: Drop a class
-- Endpoint: DELETE https://localhost:5000/student/drop_class/?student_id={student_id}&class_code={class_code}&section_number={section_number}

-- Given student_id="11111111" class_code='CPSC449' and section_number='01'

-- Check to make sure the student is actually enrolled in the class
-- If this returns a value then they are in fact enrolled
SELECT *
FROM Enroll
Where e_student_id="11111111"
AND e_class_code == "CPSC449"
AND e_section_number == "01"

-- If they are not enrolled then dont do the steps below

-- If they are enrolled then
-- Unenroll them
DELETE FROM Enroll 
Where e_student_id="11111111"
AND e_class_code == "CPSC449"
AND e_section_number == "01"

-- Decrement number of students enrolled
UPDATE Class
SET current_enrollment = current_enrollment - 1
Where class_code='CPSC449'
AND section_number='01'
AND current_enrollment > 0

-- And add them to drop list
INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
VALUES('11111111', 'CPSC449', '01');