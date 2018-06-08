import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app import models

app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def seed():
    # db.drop_all()
    level1 = models.Level(id=1)
    level1.save()

    level2 = models.Level(id=2)
    level2.save()

    level3 = models.Level(id=3)
    level3.save()

    level4 = models.Level(id=4)
    level4.save()

    sessiona = models.Session(id=1, name="2011/2012", current=False)
    sessiona.save()

    sessionb = models.Session(id=2, name="2012/2013", current=False)
    sessionb.save()

    sessionc = models.Session(id=3, name="2013/2014", current=False)
    sessionc.save()

    sessiond = models.Session(id=4, name="2014/2015", current=False)
    sessiond.save()
    
    sessione = models.Session(id=5, name="2015/2016", current=False)
    sessione.save()
    
    sessiona = models.Session(id=6, name="2016/2017", current=True)
    sessiona.save()

    usera = models.User(id=178646, email="mofopet@gmail.com", password="mofope")
    usera.save()

    userb = models.User(id=186674, email="lola@gmail.com", password="186674")
    userb.save()

    userc = models.User(id=255001, email="francis@mail.com", password="francis")
    userc.save()

    userd = models.User(id=255002, email="tolu@mail.com", password="toluosa")
    userd.save()
    
    facultya = models.Faculty(name="Social Science")
    facultya.save()

    facultyb = models.Faculty(name="Science")
    facultyb.save()

    departmenta = models.Department(code="CSC", name="Customer Science", fac_name="Science")
    departmenta.save()

    departmentb = models.Department(code="GEO", name="Geophraphy", fac_name="Social Science")
    departmentb.save()

    studenta = models.Student(firstname="Mofope", lastname="Ojosh", department_code="CSC", student_id=178646, level=4, phone_no="08116631381", sex="F")
    studenta.save()
    
    studentb = models.Student(firstname="Omolola", lastname="Okunubi", department_code="GEO", student_id=186674, level=4, phone_no="08124456789", sex="F")
    studentb.save()

    staffa = models.Staff(firstname="Francis", lastname="Akomolafe", staff_id=255001, phone_no="0812345679", sex="M")
    staffa.save()

    staffb = models.Staff(firstname="Tolu", lastname="Osa", staff_id=255002, phone_no="0812345678", sex="M")
    staffb.save()

    coursea = models.Course(code=101, title="Introduction", unit=4, level=1, department_code="CSC")
    coursea.save()

    coursef = models.Course(code=401, title="Nigeria", unit=4, level=4, department_code="GEO")
    coursef.save()

    courseb = models.Course(code=401, title="Systems Programming", unit=4, level=4, department_code="CSC")
    courseb.save()

    coursec = models.Course(code=433, title="Database Systems", unit=3, level=4, department_code="CSC")
    courseb.save()

    coursed = models.Course(code=402, title="Operating Systems", unit=3, level=4, department_code="CSC")
    coursed.save()

    coursee = models.Course(code=422, title="Computer Organizations", unit=3, level=4, department_code="CSC")
    coursee.save()


    courseforma = models.Courseform(student_id=178646, level=4, session_id=6, total_units=4)
    courseforma.save()
    
    courseformb = models.Courseform(student_id=186674, level=4, session_id=6, total_units=4)
    courseformb.save()
    
    offeringa = models.Offering(courseform_id=1, course_id=3)
    offeringa.save()
    
    offeringb = models.Offering(courseform_id=2, course_id=2)
    offeringb.save()
    
    advisera = models.Adviser(staff_id=255001, department_code="CSC", level=4)
    advisera.save()
    
    adviserb = models.Adviser(staff_id=255002, department_code="GEO", level=1)
    adviserb.save()

    # gspa = models.GSPAdviser(staff_id=255001, course_id="")
    # gspa.save()
    
    # gspb = models.GSPAdviser(staff_id=255002, course_id="")
    # gspb.save()

  

    


if __name__ == '__main__':
    manager.run()

