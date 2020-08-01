import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "Trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'root', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_getAll_categories(self):
        res = self.client().get('/categories')
        # data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_getPage_questions(self):
        page = 2
        res = self.client().get('/questions', json={'page': page}) 
        data = json.loads(res.data)   
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data[0]))

    def test_delete_question(self):
        
        res = self.client().delete('/questions/3')
        data = json.loads(res.data)   
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["id"],3)

    def test_create_question(self):
        question = {
            "question": "question math 7 ?",
	        "answer":"answer 7",
	        "category":"math",
	        "difficulty": 8
	    }
        res = self.client().post('/questions', json=question)   
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True) 

    def test_question_search(self):
        subString = 'math'
        res = self.client().post('/questions_search', json={'searchTerm':subString}) 
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data[0]))           

    def test_category_questions(self):

        res = self.client().get('/categories/2/questions') 
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data[0])) 

    def test_quizzes(self):
        request_data={
            "quiz_category": "history",
            "previous_questions": 
            [
                {
                    "answer": "answer 1",
                    "category": "music",
                    "difficulty": 9,
                    "id": 9,
                    "question": "question music 1 ?"
                },
                {
                    "answer": "answer 2",
                    "category": "music",
                    "difficulty": 5,
                    "id": 10,
                    "question": "question music 2 ?"
                },
                {
                    "answer": "answer 3",
                    "category": "music",
                    "difficulty": 5,
                    "id": 11,
                    "question": "question music 3 ?"
                }
            ]
        }
        res = self.client().post('/quizzes',json=request_data) 
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))         

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()