from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from database import Base, engine, SessionLocal
from models import User, Student, Course, student_course
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()


def create_users(session: Session, num_users: int) -> List[User]:
    """
    Create fake user records.

    Args:
        session (Session): SQLAlchemy session
        num_users (int): Number of users to create

    Returns:
        List[User]: List of created user objects
    """
    users = []
    roles = ["admin", "user"]
    try:
        for _ in range(num_users):
            user = User(
                name=fake.name(),
                login=fake.user_name(),
                password=fake.password(),
                phone=fake.phone_number(),
                role=random.choice(roles),
            )
            session.add(user)
            users.append(user)
        session.commit()
        logger.info(f"Created {num_users} fake users")
        return users
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating users: {str(e)}")
        raise


def create_courses(session: Session, num_courses: int) -> List[Course]:
    """
    Create fake course records.

    Args:
        session (Session): SQLAlchemy session
        num_courses (int): Number of courses to create

    Returns:
        List[Course]: List of created course objects
    """
    courses = []
    try:
        for _ in range(num_courses):
            course = Course(title=fake.bs().title())
            session.add(course)
            courses.append(course)
        session.commit()
        logger.info(f"Created {num_courses} fake courses")
        return courses
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating courses: {str(e)}")
        raise


def create_students(
    session: Session, num_students: int, users: List[User], courses: List[Course]
) -> List[Student]:
    """
    Create fake student records and link them to users and courses.

    Args:
        session (Session): SQLAlchemy session
        num_students (int): Number of students to create
        users (List[User]): List of available users
        courses (List[Course]): List of available courses

    Returns:
        List[Student]: List of created student objects
    """
    students = []
    try:
        for _ in range(num_students):
            student = Student(
                name=fake.name(),
                lab=fake.word(),
                user_id=fake.random_element([user.id for user in users]),
            )
            # Randomly assign 1-3 courses to the student
            student.courses = fake.random_elements(
                elements=courses, length=fake.random_int(min=1, max=3), unique=True
            )
            session.add(student)
            students.append(student)
        session.commit()
        logger.info(f"Created {num_students} fake students with course assignments")
        return students
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating students: {str(e)}")
        raise


def create_fake_data(
    session: Session, num_users: int = 10, num_courses: int = 5, num_students: int = 20
) -> None:
    """
    Create all fake data for the database.

    Args:
        session (Session): SQLAlchemy session
        num_users (int): Number of users to create (default: 10)
        num_courses (int): Number of courses to create (default: 5)
        num_students (int): Number of students to create (default: 20)
    """
    try:
        # Ensure the database tables exist
        Base.metadata.create_all(bind=engine)

        # Create the fake data in order
        users = create_users(session, num_users)
        courses = create_courses(session, num_courses)
        students = create_students(session, num_students, users, courses)

        logger.info("All fake data created successfully!")

    except Exception as e:
        logger.error(f"Error during fake data creation: {str(e)}")
        raise


def main():
    """Main function to run the fake data generator."""
    try:
        with Session(engine) as session:
            create_fake_data(session)
    except Exception as e:
        logger.error(f"Failed to generate fake data: {str(e)}")
        raise


if __name__ == "__main__":
    main()
