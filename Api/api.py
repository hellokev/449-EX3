from collections import OrderedDict

import collections
import contextlib
import logging.config
import sqlite3
import typing
import datetime
import json

from fastapi import FastAPI, Depends, Response, Request, HTTPException, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Class(BaseModel):
    class_code: str
    section_number: str
    class_name: str
    department: str
    auto_enrollment: bool
    max_enrollment: int
    current_enrollment: int
    max_waitlist: int
    current_waitlist: int
    c_instructor_id: str

class Settings(BaseSettings, env_file=".env", extra="ignore"):
    database: str
    logging_config: str

def get_db(logger: logging.Logger = Depends(get_logger)):
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        db.set_trace_callback(logger.debug)
        yield db

def get_logger():
    return logging.getLogger(__name__)

settings = Settings()
app = FastAPI()

logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)

@app.get("/")
async def message():
    """Returns a welcome message."""
    return {"message": "Project 1"}

# ---------------------- Additional -----------------------------

# Example: GET http://localhost:5000/all_classes
@app.get("/all_classes")
def get_available_classes(db: sqlite3.Connection = Depends(get_db)):
    classes = db.execute("""
                SELECT *
                FROM Class
            """)    
    return {"classes": classes.fetchall()}

# Example: GET http://localhost:5000/student/student_details
@app.get("/student_details/{student_id}")
def get_student_details(student_id: str, db: sqlite3.Connection = Depends(get_db)):

    # Get student details
    student_details = db.execute("""
        SELECT *
        FROM Student
        WHERE student_id=?
    """, (student_id,)).fetchall()[0]

    return {"student": student_details}

# Example: GET http://localhost:5000/student/student_enrollment
@app.get("/student_enrollment/{student_id}")
def get_student_enrollment(student_id: str, db: sqlite3.Connection = Depends(get_db)):

    # Get student details
    student_enrollment = db.execute("""
        SELECT *
        FROM Enroll
        WHERE e_student_id=?
    """, (student_id,)).fetchall()

    return {"enrollment": student_enrollment}


# ---------------------- Tasks -----------------------------

# Task 1: Student can list all available classes
# Example: GET http://localhost:5000/student/available_classes
@app.get("/student/available_classes")
def student_get_available_classes(db: sqlite3.Connection = Depends(get_db)):
    classes = db.execute("""
                SELECT class_code, section_number, class_name, i_first_name, i_last_name, current_enrollment, max_enrollment
                FROM Class, Instructor
                WHERE current_enrollment < max_enrollment
                AND c_instructor_id = instructor_id
            """)    
    return {"classes": classes.fetchall()}

# Task 2: Student can attempt to enroll in a class
# Example: POST http://localhost:5000/student/enroll_in_class/student/11111111/class/CPSC449/section/01
@app.post("/student/enroll_in_class/student/{student_id}/class/{class_code}/section/{section_number}")
def student_enroll_self_in_class(student_id: str, class_code:str, section_number:str, db: sqlite3.Connection = Depends(get_db)):
    # Check to see if student already enrolled
    student_is_enrolled = db.execute("""
        SELECT *
        FROM Enroll
        WHERE e_student_id=? 
        AND e_class_code=? 
        AND e_section_number=?
    """, (student_id, class_code, section_number)).fetchall()

    if student_is_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Student already enrolled"
        )
    
    # Check to see if student already on waitlist
    student_on_waitlist = db.execute("""
        SELECT *
        FROM Waitlist
        Where w_student_id=?
        AND w_class_code=?
        AND w_section_number=?
    """, (student_id, class_code, section_number)).fetchall()

    if student_on_waitlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Student already on waitlist"
        )
    
    # Get class information
    class_details = db.execute("""
        SELECT max_enrollment, current_enrollment, max_waitlist, current_waitlist
        FROM Class
        WHERE class_code=?
        AND section_number=?
    """, (class_code, section_number)).fetchall()[0]
    
    # If the classes current enrollment is less than the max enrollment then enroll the student into the class
    if class_details['current_enrollment'] < class_details['max_enrollment']:
        # Enroll the student into the class
        db.execute("""
            INSERT INTO Enroll (e_student_id, e_class_code, e_section_number)
            VALUES (?, ?, ?)
        """, (student_id, class_code, section_number))

        # Increment the number of students that are enrolled for the class
        db.execute("""
            UPDATE Class
            SET current_enrollment=current_enrollment + 1
            Where class_code=?
            AND section_number=?
        """, (class_code, section_number))

        # Commit the changes
        db.commit()

        return {"detail": "Student successfully enrolled in class"}

    else:

        # Put the student on the waitlist
        student_details = db.execute("""
            SELECT *
            FROM Student
            WHERE student_id=?
        """, (student_id,)).fetchall()[0]

        # Student reached the max number of classes they can be waitlisted for
        if student_details['num_waitlist'] >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Class enrollment full and student has exceeded their max number of waitlisted classes"
            )   
        
        # Add student the waitlist
        currentDateTime = datetime.datetime.now()
        db.execute("""
            INSERT INTO Waitlist (w_student_id, w_class_code, w_section_number, timestamp)
            VALUES (?, ?, ?, ?);
        """, (student_id, class_code, section_number, currentDateTime))

        # Increment the number of students on the class waitlist
        db.execute("""
            UPDATE Class
            SET current_waitlist=current_waitlist + 1
            WHERE class_code=?
            AND section_number=?
        """, (class_code, section_number))

        # Increment the number of classes the student is waitlisted for
        db.execute("""
            UPDATE Student
            SET num_waitlist=num_waitlist + 1
            WHERE student_id=?
        """, (student_id,))

        # Commit the changes
        db.commit()

        return {"detail": "Class enrollment full, Student added to waitlist"}

# Task 3: Student can drop a class
# Example: DELETE http://localhost:5000/student/drop_class/student/11111111/class/CPSC449/section/01
@app.delete("/student/drop_class/student/{student_id}/class/{class_code}/section/{section_number}")
def student_drop_self_from_class(student_id: str, class_code:str, section_number:str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if student already enrolled
    student_is_enrolled = db.execute("""
        SELECT *
        FROM Enroll
        WHERE e_student_id=? 
        AND e_class_code=? 
        AND e_section_number=?
    """, (student_id, class_code, section_number)).fetchall()

    # If they are enrolled, unroll them
    if student_is_enrolled:
        db.execute("""
        DELETE 
        FROM Enroll 
        Where e_student_id=?
        AND e_class_code=?
        AND e_section_number=?
        """, (student_id, class_code, section_number))

        # Decrement number of students enrolled
        db.execute("""
        UPDATE Class
        SET current_enrollment = current_enrollment - 1
        Where class_code=?
        AND section_number=?
        AND current_enrollment > 0
        """, (class_code, section_number))

        # Add them to drop list
        db.execute("""
        INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
        VALUES(?, ?, ?);
        """, (student_id, class_code, section_number))

        # Commit the changes
        db.commit()

        return {"detail": "Class successfully dropped."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot drop class, student is not enrolled."
        )   

    
# Task 4: Instructor can view current enrollment for their classes
# Example: GET http://localhost:5000/instructor/enrollment/instructor/100
@app.get("/instructor/enrollment/instructor/{instructor_id}")
def instructor_get_enrollment_for_classes(instructor_id: str, db: sqlite3.Connection = Depends(get_db)):
    enrollment = db.execute("""
        SELECT student_id, s_first_name, s_last_name, class_code, section_number, class_name
        FROM Instructor, Class, Enroll, Student
        WHERE Instructor.instructor_id=?
        AND Instructor.instructor_id=Class.c_instructor_id
        AND  Class.class_code=Enroll.e_class_code
        AND Class.section_number=Enroll.e_section_number
        AND Enroll.e_student_id=student_id
        """, (instructor_id,)).fetchall()
    
    return {"enrollment": enrollment}

# Task 5: Instructor can view students who have dropped the class
# Example: GET http://localhost:5000/instructor/dropped/instructor/100/class/CPSC449/section/01
@app.get("/instructor/dropped/instructor/{instructor_id}/class/{class_code}/section/{section_number}")
def instructor_get_students_that_dropped_class(instructor_id: str,  class_code:str, section_number:str, db: sqlite3.Connection = Depends(get_db)):
    dropped = db.execute("""
        SELECT student_id, s_first_name, s_last_name, class_code, section_number
        FROM Instructor, Class, Dropped, Student
        WHERE Instructor.instructor_id=?
        AND Class.class_code=?
        AND Class.section_number=?
        AND Instructor.instructor_id=Class.c_instructor_id
        AND  Class.class_code=Dropped.d_class_code
        AND Class.section_number=Dropped.d_section_number
        AND Dropped.d_student_id=student_id
        """, (instructor_id, class_code, section_number)).fetchall()
    
    return {"dropped": dropped}

# Task 6: Instructor can drop students administratively (e.g. if they do not show up to class)
# Example: DELETE http://localhost:5000/instructor/drop_student/student/11111111/class/CPSC449/section/01
@app.delete("/instructor/drop_student/student/{student_id}/class/{class_code}/section/{section_number}")
def instructor_drop_student_from_class(student_id: str, class_code:str, section_number:str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if student already enrolled
    student_is_enrolled = db.execute("""
        SELECT *
        FROM Enroll
        WHERE e_student_id=? 
        AND e_class_code=? 
        AND e_section_number=?
    """, (student_id, class_code, section_number)).fetchall()

    # If they are enrolled, unroll them
    if student_is_enrolled:
        db.execute("""
        DELETE 
        FROM Enroll 
        Where e_student_id=?
        AND e_class_code=?
        AND e_section_number=?
        """, (student_id, class_code, section_number))

        # Decrement number of students enrolled
        db.execute("""
        UPDATE Class
        SET current_enrollment = current_enrollment - 1
        Where class_code=?
        AND section_number=?
        AND current_enrollment > 0
        """, (class_code, section_number))

        # Add them to drop list
        db.execute("""
        INSERT INTO Dropped (d_student_id, d_class_code, d_section_number)
        VALUES(?, ?, ?);
        """, (student_id, class_code, section_number))

        # Commit the changes
        db.commit()

        return {"detail": "Student successfully dropped."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot drop class, student is not enrolled."
        )   
    
# Task 7: Registrar can add new classes and sections
# Example: POST http://localhost:5000/registrar/new_class
# body: {
#     "class_code": "CPSC335",
#     "section_number": "01",
#     "class_name": "Algorithm Engineering",
#     "department": "Computer Science",
#     "auto_enrollment": TRUE,
#     "max_enrollment": 30,
#     "current_enrollment": 0,
#     "max_waitlist": 15,
#     "current_waitlist": 0,
#     "c_instructor_id": "100",
# }
@app.post("/registrar/new_class")
def registrar_create_new_class(new_class: Class, request: Request, db: sqlite3.Connection = Depends(get_db)):

    c = dict(new_class)
    
    class_exists = db.execute("""
                SELECT *
                FROM Class
                WHERE class_code=:class_code
                AND section_number=:section_number
            """, c).fetchall()
    
    if class_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Class already exists."
        )   

    db.execute("""
        INSERT INTO Class (class_code, section_number, class_name, department, auto_enrollment, max_enrollment, current_enrollment, max_waitlist, current_waitlist, c_instructor_id)
        VALUES (:class_code, :section_number, :class_name, :department, :auto_enrollment, :max_enrollment, :current_enrollment, :max_waitlist, :current_waitlist, :c_instructor_id)
        """, c)
    
    # Commit the changes
    db.commit()
    
    return {"detail": "New class successfully added."}


# Task 8: Registrar can remove existing sections
# Example: DELETE http://localhost:5000/registrar/remove_section/class/CPSC449/section/04
@app.delete("/registrar/class/code/{class_code}/section/{section_number}")
def registrar_remove_section(class_code: str, section_number: str, db: sqlite3.Connection = Depends(get_db)):
    # Check to see if section exists 
    section_exists = db.execute("""
                SELECT *
                FROM Class
                WHERE class_code=?
                AND section_number=?
            """, (class_code, section_number)).fetchall()
    
    if section_exists:
        # Delete section
        db.execute(""" 
        DELETE FROM Class 
        WHERE class_code=?
        AND section_number=?
        """, (class_code, section_number))

        # Unenroll every student who was in that section
        db.execute(""" 
        DELETE FROM Enroll 
        WHERE e_class_code=?
        AND e_section_number=?
        """, (class_code, section_number))

        # Remove every student who was in that section from the waitlist
        db.execute(""" 
        DELETE FROM Waitlist
        WHERE w_class_code=?
        AND w_section_number=?
        """, (class_code, section_number))

        # Remove every student who was in that section from the droplist
        db.execute(""" 
        DELETE FROM Dropped
        WHERE d_class_code=?
        AND d_section_number=?
        """, (class_code, section_number))

        db.commit()
        return {"detail": "Section successfully removed."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Section does not exist."
        )   
    
# Task 9: Registrar can change instructor for a section
# Example: PUT http://localhost:5000/registrar/change_instructor/class/CSPC449/section/02/new_instructor/101
@app.put("/registrar/change_instructor/class/{class_code}/section/{section_number}/new_instructor/{instructor_id}")
def registrar_change_instructor_for_class(class_code: str, section_number: str, instructor_id: str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if section exists 
    section_exists = db.execute("""
                SELECT *
                FROM Class
                WHERE class_code=?
                AND section_number=?
            """, (class_code, section_number)).fetchall()
    
    if not section_exists:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Section does not exist."
                )   
    
    # Check to see if instructor exists 
    instructor_exists = db.execute("""
                SELECT *
                FROM Instructor
                WHERE instructor_id=?
            """, (instructor_id,)).fetchall()
    
    if not instructor_exists:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Instructor does not exist."
                )   

    # Change instructor for section
    db.execute("""
            UPDATE Class
            SET c_instructor_id=?
            WHERE class_code=?
            AND section_number=?
        """, (instructor_id, class_code, section_number))

    db.commit()
    return {"detail": "Instructor successfully changed"}
        

# Task 10: Freeze automatic enrollment from waiting lists (e.g. during the second week of classes)
# Example: PUT http://localhost:5000/registrar/freeze_enrollment/class/CSPC449/section/02
@app.put("/registrar/freeze_enrollment/class/{class_code}/section/{section_number}")
def registrar_freeze_enrollment_for_class(class_code: str, section_number: str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if section exists 
    section_exists = db.execute("""
                SELECT *
                FROM Class
                WHERE class_code=?
                AND section_number=?
            """, (class_code, section_number)).fetchall()

    if section_exists:
        # Change class auto_enrollment to false
        db.execute("""
                UPDATE Class
                SET auto_enrollment = FALSE
                Where class_code=?
                AND section_number=?
            """, (class_code, section_number))
    
        db.commit()
        return {"detail": "auto enrollment successfully frozen."}
    
    else:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Section does not exist."
                )   
    
    
# Task 11: Student can view their current position on the waiting list
# Example: GET http://localhost:5000/student/waitlist_position/student/11111111/class/MATH101/section/02
@app.get("/student/waitlist_position/student/{student_id}/class/{class_code}/section/{section_number}")
def student_get_waitlist_position_for_class(student_id: str, class_code: str, section_number: str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if student on waitlist
    student_on_waitlist = db.execute("""
                SELECT *
                FROM Waitlist
                WHERE w_student_id=?
                AND w_class_code=?
                AND w_section_number=?
            """, (student_id, class_code, section_number)).fetchall()
    
    
    if student_on_waitlist:
        # For all students on the wait list for the specified class, get their id and the time they joined the waitlist
        class_waitlist = db.execute("""
                SELECT w_student_id, timestamp
                FROM Waitlist
                WHERE w_class_code=?
                AND w_section_number=?
            """, (class_code, section_number)).fetchall()
        
        # Transform data so we can check the students position on the waitlist
        waitlist = {}
        for wait_list_item in class_waitlist:
            waitlist_student_id = wait_list_item["w_student_id"]
            waitlist_timestamp = wait_list_item["timestamp"]
            waitlist[waitlist_student_id] = waitlist_timestamp
        
        # Return position on waitlist
        return f'You are number {get_position_on_waitlist(waitlist, student_id)} on the waitlist'
    
    else:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Student not on waitlist."
                )   

def get_position_on_waitlist(dict, student_id):
    ordered_dict = OrderedDict({k: v for k, v in sorted(dict.items(), key=lambda item: item[1])})
    return list(ordered_dict.keys()).index(student_id) + 1

# Task 12: Student can remove themselves from a waiting list
# Example: DELETE http://localhost:5000/student/remove_from_waitlist/student/11111111/class/MATH101/section/02
@app.delete("/student/remove_from_waitlist/student/{student_id}/class/{class_code}/section/{section_number}")
def student_remove_self_from_class_waitlist(student_id: str, class_code: str, section_number: str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if student on waitlist
    student_on_waitlist = db.execute("""
                SELECT *
                FROM Waitlist
                WHERE w_student_id=?
                AND w_class_code=?
                AND w_section_number=?
            """, (student_id, class_code, section_number)).fetchall()

    if student_on_waitlist:
        # Remove student from waitlist
        db.execute("""
                DELETE FROM Waitlist
                WHERE w_student_id=?
                AND w_class_code=?
                AND w_section_number=?
            """, (student_id, class_code, section_number))
        
        # Decremenet number of students on waitlist for that class 
        db.execute("""
                UPDATE Class
                SET current_waitlist = current_waitlist - 1
                WHERE class_code=?
                AND section_number=?
                AND current_waitlist > 0
            """, (class_code, section_number))
        
        # Decremenet number of classes the student is waitlisted for
        db.execute("""
                UPDATE Student
                SET num_waitlist = num_waitlist - 1
                WHERE student_id=?
                AND num_waitlist > 0
            """, (student_id,))
    
        db.commit()
        return {"detail": "Successfully removed from waitlist"}
    
    else:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Student not on waitlist."
                )   
    

# Task 13: Instructor can view the current waiting list for their course
# Example: GET http://localhost:5000/instructor/waitlist_for_class/instructor/100/class/CPSC449/section/01
@app.get("/instructor/waitlist_for_class/instructor/{instructor_id}/class/{class_code}/section/{section_number}")
def instructor_get_waitlist_for_class(instructor_id: str, class_code: str, section_number: str, db: sqlite3.Connection = Depends(get_db)):

    # Check to see if section exists 
    section_exists = db.execute("""
                SELECT *
                FROM Class
                WHERE class_code=?
                AND section_number=?
            """, (class_code, section_number)).fetchall()
    
    if not section_exists:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Section does not exist."
                )   
    
    # Check to see if section exists 
    instructor_exists = db.execute("""
                SELECT *
                FROM Instructor
                WHERE instructor_id=?
            """, (instructor_id,)).fetchall()
    
    if not instructor_exists:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Instructor does not exist."
                )   

    # Get all students on the waitlist
    waitlist = db.execute("""
                SELECT student_id, s_first_name, s_last_name, class_code, section_number
                FROM Instructor, Class, Waitlist, Student
                WHERE Instructor.instructor_id=?
                AND Class.class_code=?
                AND Class.section_number=?
                AND Instructor.instructor_id=Class.c_instructor_id
                AND  Class.class_code=Waitlist.w_class_code
                AND Class.section_number=Waitlist.w_section_number
                AND Waitlist.w_student_id=student_id
            """, (instructor_id, class_code, section_number)).fetchall()
    
    return {"waitlist": waitlist}
