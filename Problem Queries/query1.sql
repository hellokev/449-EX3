-- Task: List available classes
-- Endpoint: GET https://localhost:5000/student/available_classes

-- Get all classes that are not full
SELECT class_code, section_number, class_name, i_first_name, i_last_name, current_enrollment, max_enrollment
from Class, Instructor
WHERE current_enrollment < max_enrollment
AND c_instructor_id == instructor_id
