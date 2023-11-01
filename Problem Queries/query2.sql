-- Task: Attempt to enroll in a class
-- Endpoint: POST https://localhost:5000/student/enroll_in_class/?student_id={student_id}&class_code={class_code}&section_number={section_number}


-- Given student_id="11111111" class_code='ENGL205' and section_number='01'

-- Check to make sure the student is not already enrolled
-- If this returns a value then they are already enrolled in the class
SELECT *
FROM Enroll
Where e_student_id="11111111"
AND e_class_code == "ENGL205"
AND e_section_number == "01"

-- If the student is not enrolled
-- Check to make sure the student is not already on the waitlist
-- If this returns a value then they are already on the waitlist
SELECT *
FROM Waitlist
Where w_student_id="11111111"
AND w_class_code == "ENGL205"
AND w_section_number == "01"

-- If the student is neither enrolled nor on the waitlist then
-- Get max_enrollment and current_enrollment and check (current_enrollment < max_enrollment)
-- Also get max_waitlist and current_waitlist incase class is full so we can check if waitlist is full
SELECT max_enrollment, current_enrollment, max_waitlist, current_waitlist
FROM Class
Where class_code == "ENGL205"
and section_number == "01"

-- If class is not full then enroll (current_enrollment < max_enrollment)
INSERT INTO Enroll (e_student_id, e_class_code, e_section_number)
VALUES ('11111111', 'ENGL205', '01')

-- Increment number of students enrolled
UPDATE Class
SET current_enrollment = current_enrollment + 1
Where class_code='ENGL205'
AND section_number='01'
AND current_enrollment < max_enrollment

-- If the class is full then we want to add them to the waitlist but first we need to make sure
-- the student is not going to exceeded there 3 waitlist maximum (num_waitlist  <  3)
SELECT num_waitlist
FROM Student
WHERE student_id == "11111111"

-- Now we can add the student to the waitlist
-- check if waitlist is full using max_waitlist and current_waitlist from the previous query
-- If waitlist is not full then add student to waitlist (current_waitlist < max_waitlist)
INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
VALUES ('11111111', 'ENGL205', '01', CURRENT_TIMESTAMP);

-- Increment number of students on waitlist
UPDATE Class
SET current_waitlist = current_waitlist + 1
Where class_code='ENGL205'
AND section_number='01'
AND current_waitlist < max_waitlist

-- Increment number of classes the student is waitlisted for
UPDATE Student
SET num_waitlist = num_waitlist + 1
WHERE student_id == "11111111"
AND num_waitlist < 3