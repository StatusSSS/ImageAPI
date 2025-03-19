from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    user_password = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    images = relationship("Image", back_populates="user", cascade="all, delete-orphan")
    changed_images = relationship("ChangedImages", back_populates="user", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    download_date = Column(DateTime, nullable=False)
    resolution = Column(Integer, nullable=False)
    size = Column(Integer, nullable=False)
    tags = Column(String, nullable=True)

    user = relationship("User", back_populates="images")
    changed_images = relationship("ChangedImages", back_populates="original_image", cascade="all, delete-orphan")


class ChangedImages(Base):
    __tablename__ = "changed_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    resized_file_path = Column(String, nullable=False)
    grey_file_path = Column(String, nullable=False)

    user = relationship("User", back_populates="changed_images")
    original_image = relationship("Image", back_populates="changed_images")

