-- Task: Remove existing sections
-- Endpoint: DELETE https://localhost:5000/registrar/section/?class_code={class_code}&section_number={section_number}

-- Given class_code='CPSC335' and section_number='01'

-- Remove section
DELETE FROM Class 
Where class_code='CPSC335'
AND section_number='01'

-- Unenroll every student who was in that section
DELETE FROM Enroll 
WHERE e_class_code == "CPSC335"
AND e_section_number == "01"

-- Remove every student who was in that section from the waitlist
DELETE FROM Waitlist
WHERE w_class_code == "CPSC335"
AND w_section_number == "01"

-- Remove every student who was in that section from the droplist
DELETE FROM Dropped
WHERE d_class_code == "CPSC335"
AND d_section_number == "01"