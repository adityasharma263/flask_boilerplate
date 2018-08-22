# -*- coding: utf-8 -*-
__author__ = 'aditya'
"""base class for every model class"""
from app_name import db
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only


class Base(db.Model):
    __abstract__ = True

    id = db.Column('id', db.Integer, primary_key=True, index=True)
    created_at = db.Column('created_at', db.DateTime(timezone=True), default=db.func.current_timestamp())
    updated_at = db.Column('updated_at', db.DateTime(timezone=True), default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.flush()

    @staticmethod
    def join_query(class_name, join, filter, order):
        return db.session.query(class_name).join(join).order_by(order).filter(filter).all()

    @staticmethod
    def insert(obj):
        db.session.add(obj)
        db.session.commit()
        db.session.flush()

    @staticmethod
    def update_db():
        db.session.commit()
        db.session.flush()

    @classmethod
    def merge(cls, obj):
        db.session.merge(obj)
        db.session.commit()

    @staticmethod
    def delete_db(obj):
        db.session.delete(obj)
        db.session.commit()