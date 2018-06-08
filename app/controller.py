import os
import base64
import logging

from flask import Blueprint, request, jsonify, abort, render_template, redirect
from flask_login import login_required, login_user, logout_user, current_user
from flask_api import status
from werkzeug import secure_filename

from app import db, ma, login_manager
from app.models import Offering, Course, User, Staff, Adviser, Student, Courseform, Session, Department, Faculty, Level
from flask_cors import CORS, cross_origin


api = Blueprint('api', __name__, url_prefix='/api')
# CORS(api, origins='http://127.0.0.1:8080', supports_credentials=True)

login_manager.login_message = "Unauthorized access"
login_manager.login_view = "api.unauth"# Set up user_loader


@api.route('/notfound')
def unauth():
  data = {
        'message': 'Unauthorized'
      }
  return data, status.HTTP_404_NOT_FOUND


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
    
@login_manager.request_loader
def load_user(request):
  api_key = request.args.get('api_key')
  if api_key:
    user = User.verify_token(token)
    if user:
        return user

  # next, try to login using Basic Auth
  token = request.headers.get('Authorization')
  if token:
    user = User.verify_token(token)
    if user:
      return user
  
  return None

@api.route('/levels', methods=['GET'])
def level():
  levels = Level.get_all()

  data = levels_schema.dump(levels).data
  
  return jsonify(data)

@api.route('/departments', methods=['GET'])
def dept():
  departments = Department.get_all()

  data = departments_schema.dump(departments).data
  
  return jsonify(data)

@api.route('/faculties', methods=['GET'])
def fac():
  faculties = Faculty.get_all()

  data = faculties_schema.dump(faculties).data
  
  return jsonify(data)


@api.route('/user/role', methods=['GET'])
@login_required
def user_role():
  # current_user = User.get(178646)
  staff = Staff.query.filter_by(staff_id=current_user.id).scalar()
  if staff:
    dept = Department.query.filter_by(staff_id=current_user.id).scalar()
    fac = Faculty.query.filter_by(staff_id=current_user.id).scalar()
    user = staff_schema.dump(current_user.staff).data
    role = "staff"

    if (staff.adviser):
      role = "adviser"
      user["department"] = staff.adviser.department_code
      user["level"] = staff.adviser.level
    elif(dept):
      role = "hod"
      dept = Department.query.filter_by(staff_id=current_user.id).first()
      user["department"] = dept.code
    elif(fac):
      role = "dean"
      fac = Faculty.query.filter_by(staff_id=current_user.id).first()
      user["faculty"] = fac.name

    data = {
      "role": role,
      "user": user
    }
  else:
    # courseform = current_user.student.courseforms[0]
    user = student_schema.dump(current_user.student).data
    session = Session.get_current()
    session = session_schema.dump(session).data
    # user.courseforms = courseform
    data = {
      "role": "student",
      "user": user,
      "session": session
      # "session": session
    }
  return jsonify(data)

@api.route('/user/dashboard', methods=['GET'])
@login_required
def user_dashboard():
  staff = Staff.query.filter_by(staff_id=current_user.id).first()
  dept = Department.query.filter_by(staff_id=current_user.id).scalar()
  fac = Faculty.query.filter_by(staff_id=current_user.id).scalar()
  if (staff.adviser):
    adviser = staff.adviser
    courses = Course.query.filter_by(level=adviser.level, department_code=adviser.department_code).all()
    course = len(courses)
    signs = Offering.query.filter_by(signed=adviser.staff_id).all()
    signed = len(signs)
    students = Student.query.filter_by(level=adviser.level, department_code=adviser.department_code).all()
    submissions = 0
    session_id = Session.get_current()
    
    for student in students:
      courseform = Courseform.query.filter_by(student_id=student.student_id, session_id=session_id).first()
      offerings = Offering.query.filter_by(courseform_id=courseform.id, submitted=True).all()
      offering = len(offerings)
      submissions = submissions + offering
    data = {
      "a": course,
      "b": signed,
      "c": submissions
    }      
  elif(dept):
    dept = Department.query.filter_by(staff_id=current_user.id).first()
    advisers = Adviser.query.filter_by(department_code=dept.code).all()
    adviser = len(advisers)
    courses = Course.query.filter_by(department_code=dept.code).all()
    course = len(courses)
    students = Student.query.filter_by(department_code=dept.code).all()
    student = len(students)
    data = {
      "a": course,
      "b": adviser,
      "c": student
    } 
    
  elif(fac):
    fac = Faculty.query.query.filter_by(staff_id=current_user.id).first()
    dept = Department.query.query.filter_by(fac_name=fac.name).all()
    adviser = 0
    course = 0
    student = 0
    for dept in depts:
      advisers = Adviser.query.filter_by(department_code=dept.code).all()
      a = len(advisers)
      adviser = a +adviser
      courses = Course.query.filter_by(department_code=dept.code).all()
      c = len(courses)
      course = c + course
      students = Student.query.filter_by(department_code=dept.code).all()
      s = len(students)
      student = s +student
    data = {
      "a": course,
      "b": adviser,
      "c": student
    } 
  else:
    data = {
      "message": "Invalid User"
    }

  return data


@api.route('/student/<int:id>', methods=['GET'])
def student_info(id):
  student = Student.query.get(id)
  # student = user.student
  data = student_schema.dump(student).data
  return jsonify(data)  

@api.route('/auth/token')
@login_required
def get_auth_token():
    token = current_user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@api.route('/auth/login', methods=['POST'])
def login():
  id = request.json['id']
  password = request.json['password']
  user = User.query.get(id)
  data = {
    'message': 'Invalid login'
  }
  if user is not None and user.verify_password(password):    
    token = user.generate_auth_token()
    
    if not login_user(user):
      return data

    dept = Department.query.filter_by(staff_id=user.id).scalar()
    fac = Faculty.query.filter_by(staff_id=user.id).scalar()
    if (user.student):
      role = "student"

    elif (user.staff.adviser):
      role = "adviser"
      
    elif(dept):
      role = "hod"

    elif(fac):
      role = "dean"
    
    else:
      return data
    
    data = { 'token': token.decode('ascii'), 'role': role }
    return jsonify(data)
    
  else:
    return "help"
    
  
@api.route('/auth/register', methods=['POST'])
def register():
  id = request.json['id']
  email = request.json['email']
  password = request.json['password']
  
  user = User(id=id, email=email, password=password)
  user.save()
  if not login_user(user):
    data = {
    'message': 'Invalid Credentials'
    }
  else: 
    token = user.generate_auth_token() 
    data = { 'token': token.decode('ascii') }
  
  return jsonify(data)
  
@api.route("/auth/logout")
@login_required
def logout():
  # current_user = User.get(178646)
  logout_user()

  data = {
    'message': 'success'
  }
  return jsonify(data)

@api.route('/signature', methods=['POST'])
@login_required
def addsignature():
  # current_user = User.get(178646)

  signature = request.json['signature']
  imageName = str(current_user.id)+".png"

  if current_user.staff:
    current_user.staff.signature = imageName
  else:
    current_user.student.signature = imageName
    
  db.session.commit()

  signature = signature.encode()
  signature = base64.decodestring(signature)
  image = open('../frontend/static/uploads/'+imageName, 'wb')
  image2 = open('dist/static/uploads/'+imageName, 'wb')
  if (image.write(signature) and image2.write(signature)):
    data = {
      'message': 'success'
    }
    
  else:
    data = {
      'message': 'An error occured'
    }

  return jsonify(data)

  
@api.route('/student/profile', methods=['POST'])
@login_required
def student_profile():
  # current_user = User.get(178646)
  # student = current_user.student
  firstname = request.json['firstname']
  lastname = request.json['lastname']
  sex = request.json['sex']
  phone = request.json['phone']
  department = request.json['department']
  level = request.json['level']

  # if (request.json['role']):
  #   role = request.json['role']
  #   if

  student = Student(student_id=current_user.id, firstname=firstname, lastname=lastname, department_code=department, sex=sex, phone_no=phone)
  student.save()
  
  data = {
      'message': 'success'
  }
  
  return jsonify(data)


  
@api.route('/student/courses/', methods=['GET'])
@login_required
def student_mycourses():
  # current_user = User.get(178646)
  
  session_id = Session.get_current()
  courseform = Courseform.query.filter_by(student_id=current_user.id, session_id=session_id).first()
  offerings = courseform.offerings
  session = Session.get_current_name()
  
  courseform = courseform_schema.dump(courseform).data
  courseform['session'] = session
  
  data = {
    "courses": [],
    "session": session,
    "courseform": courseform
  }
  for i in range(len(offerings)):
    course = offerings[i].course
    course =  course_schema.dump(course).data
    course['signature'] = offerings[i].signed    
    data['courses'].append(course) 

  return jsonify(data)

  # return jsonify(data)
  
@api.route('/student/courses/add', methods=['POST'])
@login_required
def student_addcourse():
  dept = Department.query.filter_by(staff_id=current_user.id).scalar()
  if(dept):
    department_code = Department.query.filter_by(staff_id=current_user.id).first()
  
  course_id = request.json['course_id']
  session_id = Session.get_current()
  courseform = Courseform.query.filter_by(student_id=current_user.id, session_id=session_id).first()
  
  course = Course.query.get(course_id)
  unit = course.unit
  old_unit = courseform.total_units
  courseform.total_units = unit + old_unit
  db.session.commit()

  offering = Offering(courseform_id=courseform.id, course_id=course_id)
  exists = Offering.query.filter_by(courseform_id=courseform.id, course_id=course_id).scalar()
  if not exists:
    offering.save()

    data = {
      "message": "success"
    }
  else: 
    data = {
      "message": "Course already exists"
    }

  return jsonify(data)
   

@api.route('/student/courses/delete/<int:id>', methods=['DELETE'])
@login_required
def student_deletecourse(id):
  # current_user = User.get(178646)
  session_id = Session.get_current()
  courseform = Courseform.query.filter_by(student_id=current_user.id, session_id=session_id).first()
  
  

  exists = Offering.query.filter_by(courseform_id=courseform.id, course_id=id).scalar()
  if not exists:
    data = {
      "message": "Course not found"
    }
  else:
    offering = Offering.query.filter_by(courseform_id=courseform.id, course_id=id).first()
    offering.delete()
    course = Course.query.get(id)
    unit = course.unit
    old_unit = courseform.total_units
    courseform.total_units = old_unit - unit 
    db.session.commit()    
    data = {
      "message": "success"
    }

  # response['status_code'] = 200
  return jsonify(data)

@api.route('/dept/<dept>/staff', methods=['GET'])
@login_required
def dept_staff(dept):
  advisers = Adviser.get_staff(dept)
  if (advisers):
    staffs = []
    for i in range(len(advisers)):
      staff_id = advisers[i].staff_id
      staff = Staff.query.get(staff_id)
      staffs.append(staff)

    staffs = staffs_schema.dump(staffs).data
    for i in range(len(advisers)):
      staffs[i]["level"] = advisers[i].level

    data = {
      "staff" : staffs
    }

  else: 
    data = {
      "message": "No Adviser's Found"
    }
  print(data)
  return data
  
@api.route('/staff/courses/', methods=['GET'])
@login_required
def staff_courses():
  staff = Staff.query.filter_by(staff_id=current_user.id).first()
  # staff = Adviser.get_all()
  level = staff.adviser.level
  department = staff.adviser.department_code
  courses = Course.query.filter_by(level=level, department_code=department).all()
  # courses = adviser.get_courses
  
  data = courses_schema.dump(courses).data
  return jsonify(data)
  

@api.route('/staff/courses/sign', methods=['POST'])
def sign_course():
  # logging(request)
  # student = 1
  student_id = request.json['student_id']
  course_id = request.json['course_id']

  session_id = Session.get_current()
  courseform = Courseform.query.filter_by(student_id=student_id, session_id=session_id).first()
  offering = Offering.query.filter_by(courseform_id=courseform.id, course_id=course_id).first()

  offering.signed = 255001
  db.session.commit()

  # response['status_code'] = 200
  data = {
      "message": "success"
    }

  # response['status_code'] = 200
  return jsonify(data)
  

@api.route('/staff/courses/delete/<int:id>', methods=['DELETE'])
@login_required
def staff_deletecourse():
  # current_user = User.get(178646)
  offering = offering.query.filter_by(id=id).first()
  if not course:
    abort(404)

  offering.delete()
  return redirect('courses')


@api.route('/staff/profile', methods=['POST'])
@login_required
def staff_profile():
  firstname = request.json['firstname']
  lastname = request.json['lastname']
  sex = request.json['sex']
  phone = request.json['phone']
  role = request.json['staff']
  
  staff = Staff(staff_id=current_user.id, firstname=firstname, lastname=lastname, sex=sex, phone_no=phone)
  staff.save()
  if (role== "HOD"):
    department_code = request.json['department_code']
    department = Department.query.filter_by(code=department_code).first()
    department.staff_id = current_user.id
    db.session.commit()

  elif(role == "Adviser"):
    department_code = request.json['department_code']
    adviser = Adviser(staff_id=current_user.id, department_code=department_code, level=4)
    adviser.save()

  elif(role == "Dean"):
    faculty = request.json['faculty']
    faculty = Faculty.query.filter_by(name=faculty).first()
    faculty.staff_id = current_user.id
    db.session.commit()

  data = {
      'message': 'success'
  }
  
  return jsonify(data)

@api.route('/dept/<dept>/course/add', methods=['POST'])
@login_required
def addCourse(dept):
  code = request.json['code'] 
  title = request.json['title'] 
  unit = request.json['unit'] 
  level = request.json['level'] 

  course = Course(code=code, title=title, unit=unit, level=level, department_code=dept)
  course.save()
  data = {
    "message": "success"
  }
  if request.json['adviser']:
    adviser = request.json['adviser']
    getadviser = Adviser.query.filter_by(staff_id=adviser).first()
    getadviser.level = level
    db.session.commit()

  return jsonify(data)

@api.route('/dept/<code>/courses', methods=['GET'])
def dept_courses(code): 
 
  courses = Course.get_dept(code.upper())
  data = courses_schema.dump(courses).data

  return jsonify(data)

@api.route('/course/', methods=['GET'])
def all_courses():
  # print (request.headers)
  courses = Course.get_all()
  # course = Course.query.get_or_404(1)('01')
  data =  courses_schema.dump(courses).data
  # res.headers.add('Access-Control-Allow-Origin', '*')
  return data
  
@api.route('/course/<int:id>', methods=['GET'])
def get_course(id):
  # print (request.headers)
  course = Course.query.get(id)
  level = course.level
  # course = Course.query.get_or_404(1)('01')
  data =  course_schema.dump(course).data
  # res.headers.add('Access-Control-Allow-Origin', '*')
  data["level"] = level
  adviser = Level.query.get(level).adviser.staff_id
  data["adviser"] = adviser
  return data
  

@api.route('/courses/student', methods=['GET'])
@login_required
def courses_student(): 
  current_user = current_user.student
  courses = Course.query.filter_by(department_code=current_user.department_code, level=current_user.level).all()
  data = courses_schema.dump(courses).data

  return jsonify(data)

@api.route('/course/<int:id>/students', methods=['GET'])
def courseStudents(id): 
  # current_user = User.get(178646).student
  courses = Course.query.get(id)
  offerings = courses.offerings
  olddata = offerings_schema.dump(offerings).data
  data = []
  for i in range(len(offerings)):
    student = offerings[i].courseform.student
    olddata[i] =  student_schema.dump(student).data
    if offerings[i].signed is None:
      data.append(olddata[i])

  return jsonify(data)

@api.route('/course/edit/<int:id>', methods=['PUT'])
def editCourse(id):
  # course = Course.query.get_or_404(101)
  exists = Course.query.filter_by(id=id).scalar()
  if exists:
    course = Course.query.get(id)
    
    code = request.json['code'] 
    title = request.json['title'] 
    unit = request.json['unit'] 
    level = request.json['level'] 

    course.code = code
    course.level = level
    course.title = title
    course.unit = unit

    if request.json['adviser']:
      adviser = request.json['adviser']
      getadviser = Adviser.query.filter_by(staff_id=adviser).first()
      getadviser.level = level
    
    db.session.commit()

    data = {
      "message": "success"
    }
  else:
    data = {
      "message": "An error occured"
    }

  return jsonify(data)
  
@api.route('/course/delete/<int:id>', methods=['GET'])
def deleteCourse(id):
  # course = Course.query.get_or_404(101)
  exists = Course.query.filter_by(id=id).scalar()
  if exists:
    course = Course.query.get(id=id).first()
    course.delete()
    data = {
      "message": "success"
    }
  else:
    data = {
      "message": "An error occured"
    }

  return jsonify(data)


class StudentSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Student
    # fields = ('id', 'firstname', 'lastname', 'user_id', 'department_code', 'level', 'phone_no', 'sex')

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

class OfferingSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Offering
    # fields = ('id', 'courseform_id', 'course_id', 'signed', 'submitted', 'courses')

offering_schema = OfferingSchema()
offerings_schema = OfferingSchema(many=True)

class AdviserSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Adviser
    # fields = ('id', 'courseform_id', 'department_code', 'signed', 'submitted')

adviser_schema = AdviserSchema()
advisers_schema = AdviserSchema(many=True)

class StaffSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Staff
      # fields = ('id', 'firstname', 'lastname', 'user_id', 'phone_no', 'sex', 'signature')

   # fields = ('id', 'code', 'title', 'user_id', 'phone_no', 'sex', 'signature')    
staff_schema = StaffSchema()
staffs_schema = StaffSchema(many=True)

class CourseformSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Courseform
      # fields = ('id', 'firstname', 'lastname', 'user_id', 'phone_no', 'sex', 'signature')

   # fields = ('id', 'code', 'title', 'user_id', 'phone_no', 'sex', 'signature')    
courseform_schema = CourseformSchema()
courseforms_schema = CourseformSchema(many=True)

class CourseSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Course
    # fields = ('id', 'code', 'title', 'unit', 'department_code')

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

class DepartmentSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Department
    # fields = ('id', 'code', 'title', 'unit', 'department_code')

department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)

class FacultySchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Faculty
    # fields = ('id', 'code', 'title', 'unit', 'faculty_code')

faculty_schema = FacultySchema()
faculties_schema = FacultySchema(many=True)

class LevelSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Level
    # fields = ('id', 'code', 'title', 'unit', 'department_code')

level_schema = LevelSchema()
levels_schema = LevelSchema(many=True)

class SessionSchema(ma.ModelSchema):
  class Meta:
    # Fields to expose
    model = Session
    # fields = ('id', 'code', 'title', 'unit', 'department_code')

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

