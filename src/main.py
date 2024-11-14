from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List, Union, Dict


from database import Base, engine, SessionLocal
import models
import schema
from utils import hash_password, verify_password

app = FastAPI()

Base.metadata.create_all(bind=engine)


# define the dependence


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users", response_model=List[schema.User])
async def get_user(
    skip: int = 0, limit: int = 15, db: Session = Depends(get_db)
) -> List[schema.User]:

    db_user = db.query(models.User).offset(skip).limit(limit).all()
    if db_user is None:
        # relever une exception
        raise HTTPException(status_code=404, details="No_items")
    return db_user


@app.post("/create_users", response_model=schema.User)
async def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):

    try:
        hashed_password = hash_password(user.password)
        db_user = models.User(
            name=user.name,
            login=user.login,
            password=hashed_password,
            phone=user.phone,
            role=user.role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()

        print(f"Error {e}")

        raise HTTPException(status_code=500, detail="connexion failed ")


@app.put("/user_update/{user_id}")
async def update_user(
    user_id: int,
    user: schema.UserUpdate,
    db: Session = Depends(get_db),
    password: str = None,
):

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="can not found the user ")
    if db_user.role != "admin":
        if not password:
            raise HTTPException(
                status_code=403,
                detail="user is not admin and password is empty",
            )
        if not verify_password(password, db_user.password):
            raise HTTPException(
                status_code=403, detail="the password did not match"
            )

    db_user.name = user.name
    db_user.login = user.login
    if user.password is not None:
        db_user.password = hash_password(user.password)
    db_user.phone = user.phone
    db_user.role = user.role
    db.commit()
    db.refresh(db_user)

    return db_user


@app.delete("/delete_user/{user_id}", response_model=Dict[str, str])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = (
            db.query(models.User).filter(models.User.id == user_id).first()
        )
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(db_user)
        db.commit()

        return {"detail": "User deleted successfuly"}
    except Exception as e:
        db.rollback()
        raise HTTPException(detail=f"An error occured {str(e)}")


@app.get("/students")
async def get_student(
    skip: int = 0, limit: int = 15, db: Session = Depends(get_db)
) -> List[schema.StudentWithCourse]:

    db_student = (
        db.query(models.Student)
        .options(joinedload(models.Student.courses))
        .offset(skip)
        .limit(limit)
        .all()
    )
    if db_student is None:
        # relver une exception
        raise HTTPException(status_code=404, details="No student  found")
    return db_student
    # students = db.query(models.Student).offset(skip).limit(limit).all()
    # if not students:
    #     raise HTTPException(status_code=404, detail=" Stdudent not find ")
    # # student_with_courses=[]
    # for student in students:
    #     courses=student.courses

    # return students


@app.post("/create_students", response_model=List[schema.Student])
async def create_student(
    user_id,
    students: List[schema.StudentCreate] | schema.StudentCreate,
    db: Session = Depends(get_db),
):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=" user not found ")

    if user.role != "admin":
        raise HTTPException(
            status_code=404, detail="Only admin can create an user "
        )

    def create_single_student(student: schema.StudentCreate):

        user = (
            db.query(models.User)
            .filter(models.User.id == student.user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db_student = models.Student(
            name=student.name,
            lab=student.lab,
            user_id=student.user_id,
            # course_id=student.course_id
        )
        if student.course_id:
            courses = (
                db.query(models.Course)
                .filter(models.Course.id.in_(student.course_id))
                .all()
            )

        if len(courses) != len(student.course_id):
            raise HTTPException(
                status_code=404, detail="Some courses not found"
            )
        db_student.courses = courses
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student

    try:
        if isinstance(students, list):
            list_student = []
            for student in students:
                list_student.append(create_single_student(student))
            return list_student
        else:
            return [create_single_student]

    except Exception as e:
        print(f"Error {e}")
        raise HTTPException(status_code=500, detail="connexion failed ")


# @app.put(
#     "/student_update/{student_id}",
#     response_model=Union[List[schema.Student], schema.Student],
# )
@app.put(
    "/student_update/",
    response_model=Union[List[schema.Student], schema.Student],
)
async def update_student(
    user_id: int,
    # student_id: int,
    student_updates: Union[List[schema.StudentUpdate], schema.StudentUpdate],
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=" user not found ")

    # if user.role != "admin":
    #     raise HTTPException(status_code=404, detail="Only admin can create an user ")

    def update_one_student(student_update: schema.StudentUpdate):
        db_student = (
            db.query(models.Student)
            .filter(models.Student.id == student_update.id)
            .first()
        )
        if db_student is None:
            raise HTTPException(
                status_code=404, detail="can not found the student"
            )

        if student_update.name is not None:

            db_student.name = student_update.name

        if student_update.lab is not None:

            db_student.lab = student_update.lab

        # if student_update.user_id is not None:
        #     user = (
        #         db.query(models.User)
        #         .filter(models.User.id == student_update.user_id)
        #         .first()
        #     )
        #     if not user:
        #         raise HTTPException(status_code=404, detail="user not found ")

        #     db_student.user_id = student_update.user_id
        if student_update.course_id is not None:
            course = (
                db.query(models.Course)
                .filter(models.Course.id.in_(student_update.course_id))
                .all()
            )
            if len(course) != len(student_update.course_id):
                raise HTTPException(
                    status_code=404,
                    detail="the lenght of course is different than the length of user_id",
                )

            db_student.course_id = student_update.course_id

        db.commit()

        db.refresh(db_student)

        return db_student

    # update_student = []
    try:
        if isinstance(student_updates, list):
            list_student_update = []
            for student_update in student_updates:
                list_student_update.append(update_one_student(student_update))
            return list_student_update
        else:
            return update_one_student(student_updates)

    except Exception as e:
        print(f"Error {e}")
        raise HTTPException(status_code=500, detail="connexion failed ")


# @app.delete("/delete_student/", response_model=Dict[str, str])
@app.delete(
    "/delete_student/",
    response_model=Dict[str, Union[str, List[Dict[str, str]]]],
)
async def delete_student(
    user_id: int,
    student_deletes: Union[List[schema.StudentDelete] | schema.StudentDelete],
    db: Session = Depends(get_db),
):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=" user not found ")

    if user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin can delete an user "
        )

    def delete_on_student(student_delete: schema.StudentDelete):

        db_student = (
            db.query(models.Student)
            .filter(models.Student.id == student_delete.id)
            .first()
        )
        if db_student is None:
            raise HTTPException(status_code=404, detail="student not found")
        db.delete(db_student)
        db.commit()
        return {
            "detail": f"student with ID {student_delete.id} deleted successfuly"
        }

    try:
        if isinstance(student_deletes, list):
            list_deletes_student = []
            for student_delete in student_deletes:
                list_deletes_student.append(delete_on_student(student_delete))

            return {
                "detail": "Students deleted successfully",
                "students": list_deletes_student,
            }
        else:

            return {
                "detail": "Students deleted successfully",
                "students": delete_on_student(student_deletes),
            }

    except Exception as e:
        print(f"str{e}")
        raise HTTPException(
            status_code=500, detail=" can not delete any student"
        )


@app.get("/courses", response_model=List[schema.Course])
async def get_course(
    skip: int = 0, limit: int = 15, db: Session = Depends(get_db)
) -> List[schema.Course]:

    db_course = db.query(models.Course).offset(skip).limit(limit).all()
    if db_course is None:
        # relver une exception
        raise HTTPException(status_code=404, detail="No course found")
    return db_course


@app.post("/create_courses", response_model=List[schema.Course])
async def create_course(
    courses: Union[List[schema.CourseCreate], schema.CourseCreate],
    db: Session = Depends(get_db),
):

    try:

        def create_a_course(course: schema.CourseCreate):

            db_course = models.Course(title=course.title)
            db.add(db_course)
            db.commit()
            db.refresh(db_course)
            return db_course

        if isinstance(courses, list):
            return [create_a_course(course) for course in courses]
        else:
            return create_a_course(courses)
    except Exception as e:

        raise HTTPException(
            status_code=500, detail=f"connexion failed:{str(e)}"
        )


@app.put("/course_update/{course_id}", response_model=List[schema.Course])
async def update_course(
    course_id: int,
    course_updates: Union[List[schema.CourseUpdate], schema.CourseUpdate],
    db: Session = Depends(get_db),
):

    try:

        def update_a_course(course_update: schema.CourseUpdate):

            db_course = (
                db.query(models.Course)
                .filter(models.Course.id == course_id)
                .first()
            )
            if db_course is None:
                raise HTTPException(
                    status_code=404, detail="can not found the course "
                )

            if course_update.title is not None:

                db_course.title = course_update.title
            db.commit()
            db.refresh(db_course)

            return db_course

        if isinstance(course_updates, list):
            return [
                update_a_course(course_update)
                for course_update in course_updates
            ]
        else:
            return update_a_course(course_updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occur {str(e)}")


@app.delete("/delete_course/{course_id}", response_model=Dict[str, str])
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    try:

        db_course = (
            db.query(models.Course)
            .filter(models.Course.id == course_id)
            .first()
        )
        if db_course is None:
            raise HTTPException(status_code=404, detail="course not found")

        db.delete(db_course)
        db.commit()
        return {"detail": "Course deleted successfuly"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occured {str(e)}"
        )
