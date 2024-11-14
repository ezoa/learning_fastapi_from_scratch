from sqlalchemy import Table, ForeignKey, String, Integer, Column
from sqlalchemy.orm import relationship
from database import Base

# Association table
student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("course_id", Integer, ForeignKey("courses.id")),
)


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    login = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=False)
    role = Column(String(100), default="user")
    # Establish a one to many relationship with student
    students = relationship("Student", back_populates="user")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    lab = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    # link back to user

    user = relationship("User", back_populates="students")
    courses = relationship(
        "Course", secondary=student_course, back_populates="students"
    )


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    students = relationship(
        "Student", secondary=student_course, back_populates="courses"
    )
