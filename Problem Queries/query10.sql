-- Task: Freeze automatic enrollment from waiting lists (e.g. during the second week of classes)
-- Endpoint: PUT https://localhost:5000/registrar/freeze_auto_enrollment/?class_code={class_code}&section_number={section_number}

-- Given class_code='CPSC449', section_number='02' and instructor_id="102"

-- Change class auto_enrollment to false
UPDATE Class
SET auto_enrollment = FALSE
Where class_code='CPSC449'
AND section_number='02'