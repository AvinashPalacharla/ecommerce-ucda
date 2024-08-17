from ecom.utils import UserAlreadyExists, UserDoesNotExist
from ecom.extensions import admin, db, guard, mm
from flask import current_app as app
from flask_admin.contrib.sqla import ModelView
from enum import unique
import logging
from datetime import datetime
from logging import INFO, info
from operator import mod
from os import getenv
import uuid

from sqlalchemy import (
    CHAR,
    DECIMAL,
    INTEGER,
    JSON,
    NVARCHAR,
    TEXT,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
    text,
)

# Third party imports
from sqlalchemy.dialects.mssql import BIT, DATETIME2
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import UniqueConstraint
from wtforms import PasswordField
from wtforms.fields.simple import TextAreaField


class Role(db.Model):
    __tablename__ = "role"

    ROLE_ADMIN = "Admin"
    ROLE_BUSINESS_USER = "Business User"

    role_id = Column(INTEGER, primary_key=True)
    role_name = Column(NVARCHAR(100), nullable=False, unique=True)
    description = Column(NVARCHAR(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

    @staticmethod
    def create_role(role_name, description=None):
        role = Role.query.filter_by(role_name=role_name).first()
        if role:
            return
        role = Role()
        role.role_name = role_name
        if description is not None:
            role.description = description
        db.session.add(role)
        db.session.commit()
        return role

    @classmethod
    def lookup(cls, role_name):
        return cls.query.filter_by(role_name=role_name).first()


class User(db.Model):
    __tablename__ = "users"

    user_id = Column(INTEGER, primary_key=True)
    first_name = Column(NVARCHAR(100))
    last_name = Column(NVARCHAR(100))
    email = Column(NVARCHAR(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)
    is_active = Column(INTEGER, nullable=False, server_default=text("1"))
    passwords = Column(Text, nullable=False)
    role_id = Column(
        INTEGER,
        ForeignKey(Role.role_id, name="users_ibfk_1", ondelete="SET NULL"),
        nullable=True,
    )
    password_changed_at = Column(DateTime, server_default=text("NULL"))
    role = relationship("Role", backref="users", lazy=True)

    def __repr__(self):
        return "<User %r>" % str(self.username)

    @property
    def role_name(self):
        """Returns role_name.
        Returns:
            str: role_name
        """
        return self.role.role_name

    # properties and methods required by Praetorian
    @property
    def identity(self):
        return self.user_id

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def rolenames(self):
        try:
            return [self.role.role_name]
        except Exception:
            return []

    @classmethod
    def lookup_active(cls, email):
        return cls.query.filter_by(email=email, is_active=1).first()

    # def is_valid(self):
    # to be used while soft delete of user
    #    return self.approved_at is not None

    # CUSTOM properties and methods for convinience
    @property
    def password(self):
        return self.passwords

    @password.setter
    def password(self, plain_password):
        self.passwords = guard.hash_password(plain_password)

    @property
    def username(self):
        return "_".join(["id" + str(self.user_id), self.email.split("@")[0]])

    @staticmethod
    def create_user(
        first_name,
        last_name,
        email,
        password,
        role: str = None,
    ):
        user = User.lookup(email)
        if user is not None:
            raise UserAlreadyExists
        elif user is not None and user.is_active is False:
            User.update_user(
                user_id=user.user_id,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role,
            )
        else:
            user = User()
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.password = password

            role_id = None
            if role is not None:
                role_record = Role.lookup(role_name=role)
                if role_record:
                    role_id = role_record.role_id

            user.role_id = role_id

            db.session.add(user)
            db.session.commit()
        return user

    @staticmethod
    def update_user(
        user_id: int,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        password: str = None,
        role: str = None,
    ):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            raise UserDoesNotExist

        if first_name is not None:
            user.first_name = first_name

        if last_name is not None:
            user.last_name = last_name

        if email is not None:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.user_id != user_id:
                raise UserAlreadyExists
            user.email = email

        if password is not None:
            user.password = password
            user.password_changed_at = datetime.utcnow()

        if role is not None:
            role_id = None
            role_record = Role.lookup(role_name=role)
            if role_record:
                role_id = role_record.role_id
            user.role_id = role_id

        db.session.add(user)
        db.session.commit()
        return user

