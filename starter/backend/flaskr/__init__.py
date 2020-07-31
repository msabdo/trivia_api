import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.debug = True
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response


    '''
    @TODO: 
    Create an endpoint to handle GET requests     ##### done ####
    for all available categories.
    '''
    @app.route('/categories')
    def getAll_categories():
        category_list = []
        categories = Category.query.all()
        for cat in categories:
            category_list.append({
                'type': cat.type
                })
               
        return jsonify( category_list ) 

    '''
    @TODO:                                                 ######## done #
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    ''' 
    @app.route('/questions/<int:page>')
    def getPage_questions(page):
        
        questions = Question.query.paginate(page=page, per_page=10).items
        category = Category.query.all()
        category_list = []
        for cat in category:
            category_list.append({'type': cat.type})

        total_questions = len(questions)
        questions_list = []
        categories = []
        for ques in questions:
            questions_list.append(ques.format())

        return jsonify(
            questions_list, 
            category_list,
            {'totalQuestions': total_questions}
            )

    '''
    @TODO:                                              #####  done ###
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            Question.query.get(question_id).delete()
            db.session.commit()
            return jsonify({"description": "success"})

        except:
            abort(417,description="Expectation field not deleted")
    '''
    @TODO:                                  #### done ###
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            data = request.get_json()
            question = Question(
                question = data['question'], 
                answer = data['answer'],
                category = data['category'] , 
                difficulty = data['difficulty'])
            db.session.add(question)
            db.session.commit()
            return jsonify({"description": "success"})
        except:
            abort(417, description="faild")        
        

    '''
    @TODO:                                          #####  done  ###
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions_search', methods=['POST'])
    def question_search():

        questions = []
        search_data = request.get_json()['query']
        questions_list = Question.query.all()
        for ques in questions_list:
            if ques.question.lower().find(search_data) >= 0:
                questions.append(ques.format()) 

        return jsonify(questions)    


    '''
    @TODO:                                          #### done #####
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:cat_id>/questions') 
    def category_questions(cat_id):
        questions_list  = []
        questions= Question.query.all()
        category = Category.query.get(cat_id)
        for ques in questions:
            if ques.category == category.type:
                questions_list.append(ques.format())

        return jsonify(questions_list)


    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=["POST"])
    def quizzes():
        
        ids = []
        data = request.get_json()
        previous_questions = data["previous_questions"]
        for ques in previous_questions:
            ids.append(ques['id'])

        quiz_category = data['quiz_category']
        questions = Question.query.all()
        
        for ques in questions:
            if (ques.id not in ids) and (ques.category == quiz_category):
            
                return jsonify(ques.format())
        
        abort(417, description="faild")  
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(422)
    def not_processable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Not processable entity"
            }), 422

            
    return app

