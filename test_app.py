import unittest
import os
import json
from app import create_app, db

class Student(unittest.TestCase):
    """This class represents the student test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.student = {
          "dept": "Computer Science", 
          "email": "mofopet@gmail.com", 
          "fname": "Mofope", 
          "level": 400, 
          "lname": "Ojosh", 
          "matric_no": 178646, 
          "password": "password"
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_student_creation(self):
        """Test API can create a student (POST request)"""
        # res = self.client().post('/students/', data=self.student)
        # self.assertEqual(res.status_code, 201)
        # self.assertIn('Mofope', str(res.data))

    def test_api_can_get_all_students(self):
        """Test API can get a student (GET request)."""
        res = self.client().post('/students/', data=self.student)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/students/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Mofope', str(res.data))

    def test_api_can_get_student_by_id(self):
        """Test API can get a single student by using it's id."""
        # rv = self.client().post('/students/', data=self.student)
        # self.assertEqual(rv.status_code, 201)
        # result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        # result = self.client().get(
        #     '/students/{}'.format(result_in_json['id']))
        # self.assertEqual(result.status_code, 200)
        # self.assertIn('Go to Borabora', str(result.data))

    def test_student_can_be_edited(self):
        """Test API can edit an existing student. (PUT request)"""
        # rv = self.client().post(
        #     '/students/',
        #     data={'name': 'Eat, pray and love'})
        # self.assertEqual(rv.status_code, 201)
        # rv = self.client().put(
        #     '/students/1',
        #     data={
        #         "name": "Dont just eat, but also pray and love :-)"
        #     })
        # self.assertEqual(rv.status_code, 200)
        # results = self.client().get('/students/1')
        # self.assertIn('Dont just eat', str(results.data))

    # def test_student_deletion(self):
    #     """Test API can delete an existing student. (DELETE request)."""
    #     rv = self.client().post(
    #         '/students/',
    #         data={'name': 'Eat, pray and love'})
    #     self.assertEqual(rv.status_code, 201)
    #     res = self.client().delete('/students/1')
    #     self.assertEqual(res.status_code, 200)
    #     # Test to see if it exists, should return a 404
    #     result = self.client().get('/students/1')
    #     self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
