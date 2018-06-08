import time
from app import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import asc

from flask import current_app as app

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    staff = db.relationship('Staff', backref='user', lazy=True, uselist=False)
    student = db.relationship('Student', backref='user', lazy=True, uselist=False)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)


    def save(self):
        db.session.add(self)
        db.session.commit()

    def get(id):
        return  User.query.filter_by(id=id).first()

    def get_id(self):
        return self.id

    @staticmethod
    def get_all():
        return User.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.id

class Student(UserMixin, db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    department_code = db.Column(db.String(3), db.ForeignKey('departments.code'), nullable=False)
    level = db.Column(db.Integer, db.ForeignKey('levels.id'))
    phone_no = db.Column(db.String(20))
    sex = db.Column(db.String(1)) 
    signature = db.Column(db.String(120)) #blob 
    courseforms = db.relationship('Courseform', backref='student', lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_id(self):
        return self.student_id

    @staticmethod
    def get_all():
        return Student.query.all()
    

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Student %r>' % self.student_id


class Staff(UserMixin, db.Model):
    __tablename__ = "staff"
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False , unique=True)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    phone_no = db.Column(db.String(20))
    sex = db.Column(db.String(1))
    signature = db.Column(db.String(120)) #blob
    adviser = relationship('Adviser', backref='staff', lazy=True, uselist=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Staff.query.all()

    @staticmethod
    def get_dept(code):
        return Course.query.filter_by(department_code=code).order_by(asc(Course.code)).all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Staff %r>' % self.staff_id


class Course(db.Model):
    __tablename__ = "courses"
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    department_code = db.Column(db.String(3), db.ForeignKey('departments.code'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    unit = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    # courseform = relationship("Courseform", secondary="offerings")
    # offerings = db.relationship('Offering', backref='course', lazy=True)

    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_dept(code):
        return Course.query.filter_by(department_code=code).all()
    
    @staticmethod
    def get_all():
        return Course.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return 'Course: %r%r' % (Department.code, self.code)

class Faculty(db.Model):
    __tablename__ = "faculties"
    name = db.Column(db.String(120), primary_key=True, unique=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    departments = db.relationship('Department', backref='departments', lazy=True)
   

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Faculty.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Faculty %r>' % self.name


class Department(db.Model):
    __tablename__ = "departments"
    code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(120), unique=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    fac_name = db.Column(db.String(120), db.ForeignKey('faculties.name'), nullable=False)
    courses = db.relationship('Course', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)


    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Department.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Department %r>' % self.code

class Courseform(db.Model):
    __tablename__ = "courseforms"
    id = db.Column(db.Integer,  primary_key=True)
    student_id = db.Column(db.Integer,  db.ForeignKey('students.student_id'), nullable=False)
    level = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    total_units = db.Column(db.Integer)
    last_modified = db.Column(db.Date)
    submitted = db.Column(db.Boolean)
    # course = relationship("Course", secondary="offerings")
    offerings = db.relationship('Offering', backref='courseform', lazy=True)
    

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Courseform.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Course Form %r>' % self.student_id

class Offering(db.Model):
    __tablename__ = "offerings"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    courseform_id = db.Column(db.Integer, db.ForeignKey('courseforms.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    submitted = db.Column(db.Boolean)
    signed = db.Column(db.Integer)
    date_signed = db.column(db.DateTime)
    date_created = db.column(db.DateTime)
    course = db.relationship('Course', backref="offerings", lazy=True, uselist=False)
    
   
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Offering.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

      

    def __repr__(self):
        return '<Offering %r>' % self.signed

class Adviser(db.Model):
    __tablename__ = "advisers"
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    department_code = db.Column(db.String(3), db.ForeignKey('departments.code'), nullable=False)
    level = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    # staff = relationship('Staff', backref=backref("adviser", cascade="all, delete-orphan"))
    
   
    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_courses(self):
        courses = Courses.query.filter_by(level=self.level, depatment_code=self.department_code).all()
        return courses
    
    @staticmethod
    def get_staff(code):
        return Adviser.query.filter_by(department_code=code).all()
    
    @staticmethod
    def get_all():
        return Adviser.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Adviser %r>' % self.staff_id

# class GSPAdviser(db.Model):
    # __tablename__ = "gspadvisers"
    # staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    # course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, unique=True, primary_key=True)
   

    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()
    
    # @staticmethod
    # def get_all():
    #     return Adviser.query.all()

    # def delete(self):
    #     db.session.delete(self)
    #     db.session.commit()

    # def __repr__(self):
    #     return '<Adviser %r>' % self.staff_id

class Level(db.Model):
    __tablename__ = "levels"
    id = db.Column(db.Integer,  primary_key=True)
    student = db.relationship('Student', backref='levels', lazy=True, uselist=False)
    adviser = db.relationship('Adviser', backref='levels', lazy=True , uselist=False)
    courseforms = db.relationship('Courseform', backref='levels', lazy=True)
    

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Level.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Level %r>' % self.id

class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer,  primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    courseforms = db.relationship('Courseform', backref='sessions', lazy=True)
    current = db.Column(db.Boolean, nullable=False)
    

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    
    @staticmethod
    def get_all():
        return Courseform.query.all()

    @staticmethod
    def get_current():
        return Session.query.filter_by(current=True).first().id

    def get_current_name():
        return Session.query.filter_by(current=True).first().name

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Session %r>' % self.name

