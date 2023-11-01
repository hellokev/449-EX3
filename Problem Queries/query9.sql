-- Task: Change the instructor for a section
-- Endpoint: PUT https://localhost:5000/registrar/change_instructor/?class_code={class_code}&section_number={section_number}&intructor_id={intructor_id}

-- Given class_code='CPSC449', section_number='02' and instructor_id="102"

-- Update class c_instructor_id with new instructor_id
UPDATE Class
SET c_instructor_id = "102"
Where class_code='CPSC449'
AND section_number='02'