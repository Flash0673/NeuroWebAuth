from passlib.context import CryptContext
from sqlalchemy.orm import Session
from tests.auth import models
from tests.auth.db_manager import SessionLocal
from auth.manager import UserManager


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return db.delete(user)


def create_user(db: Session, user: dict):
    context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    fake_hashed_password = context.hash(user["password"])
    db_user = models.User(email=user["email"], username=user["username"], hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def prepare_db_to_test(email: str, db: Session):
    user = get_user_by_email(db, email)
    if not user:
        print("Такого пользователя не существует")
        return
    else:
        print(user.id)
        db.delete(user)
        db.commit()
        print("Пользователь успешно удален")
    return


def create_test_user(db: Session, test_email: str, data: dict):
    user = get_user_by_email(db, test_email)
    if not user:
        create_user(db, data)
