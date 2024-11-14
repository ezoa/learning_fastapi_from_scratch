from pydantic import BaseModel

from typing import Optional, List


class User(BaseModel):
    id: int
    login: str
    password: str
    name: str
    phone: str
    role: str

    class Config:
        # orm_mode=True
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    login: str
    password: str
    phone: str
    role: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class Student(BaseModel):
    id: int
    name: str
    lab: str
    user_id: int  # include user id to associate user
    # course_id: Optional[List[int]]=[]

    class Config:
        # orm_mode=True
        from_attributes = True


class StudentCreate(BaseModel):
    
    name: str
    lab: str
    user_id: int
    course_id: Optional[List[int]]=None


class StudentUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    lab: Optional[str] = None
    # user_id: Optional[int] = None
    course_id: Optional[List[int]] = None


class StudentDelete(BaseModel):
    id: int


class Course(BaseModel):
    id: int
    title: str
    # student_id: Optional[List[int]]=[]

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    title: str
    # student_id: Optional[List[int]] = None


class CourseUpdate(BaseModel):
    title: Optional[str]
    # student_id: Optional[List[int]] = None


class StudentWithCourse(Student):
    courses: List[Course] = []


class CourseWithStudent(Course):
    students: List[Student] = []
