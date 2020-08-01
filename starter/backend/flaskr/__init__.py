import os
from flask import Flask, request, abort, jsonify, make_response
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
    @TODO: Set up CORS. Allow '*' for origins.
    '''
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
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
        if categories is not None:
            for cat in categories:
                category_list.append({
                    'id': cat.id,
                    'type': cat.type
                })
            return make_response(jsonify(category_list), 200)
        else:
            return make_response(jsonify(success=False), 404)


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
    @app.route('/questions')
    def getPage_questions():
        page = request.args.get('page')
        questions = Question.query.paginate(page=page, per_page=10).items
        category = Category.query.all()
        category_list = []
        for cat in category:
            category_list.append({'type': cat.type})

        total_questions = len(questions)
        questions_list = []
        for ques in questions:
            questions_list.append(ques.format())

        return make_response(
            jsonify(
                questions_list,
                category_list,
                {'totalQuestions': total_questions}
            ), 200)

    '''
    @TODO:                   #####  done ###
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            ques = Question.query.get(question_id)
            if ques is not None:
                ques.delete()
                return make_response(jsonify({"id": question_id}), 200)
            else:
                return make_response(
                    jsonify(description='already deleted'), 200
                )

        except:
            abort(500, description=" not deleted")
    '''
    @TODO:                      #### done ###
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
                question=data['question'],
                answer=data['answer'],
                category=data['category'],
                difficulty=data['difficulty'])
            db.session.add(question)
            db.session.commit()
            return make_response(jsonify(success=True), 200)
        except:
            abort(400, success=False)

    '''
    @TODO:                                        #####  done  ###
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
        search_data = request.get_json()['searchTerm']
        questions_list = Question.query.all()
        first_step = True 
        for ques in questions_list:
            if search_data.lower() in ques.question.lower():
                first_step = False
                questions.append(ques.format())
        if first_step:
            return make_response(jsonify(success=False), 404)

        return make_response(jsonify(questions), 200)

    '''
    @TODO:                                          #### done #####
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:cat_id>/questions')
    def category_questions(cat_id):
        questions_list = []
        categ = Category.query.get(cat_id)
        if categ is not None:
            questions = Question.query.filter_by(category=categ.type).all()
            for ques in questions:
                questions_list.append(ques.format())

            return make_response(jsonify(questions_list), 200)

        if (categ is None) or (questions is None):
            return make_response(jsonify(success=False), 404)

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

        pre_ids = []
        current_ids = []
        rand_num = 0
        data = request.get_json()
        previous_questions = data["previous_questions"]
        for ques in previous_questions:
            pre_ids.append(ques['id'])

        quiz_category = data['quiz_category']
        category_questions = Question.query.filter_by(
            category=quiz_category).all()
        if len(category_questions) == 0:
            return make_response(jsonify(
                success=False
            ), 404)
        else:
            for ques in category_questions:
                current_ids.append(ques.id)

        rand_num = random.choice(current_ids)

        while True:
            if rand_num not in pre_ids:
                rand_question = Question.query.get(rand_num)
                if(rand_question is not None):
                    return make_response(jsonify(rand_question.format()), 200)
                else:
                    return
            else:
                return make_response(jsonify(success=False), 404)

        abort(500, description="faild")
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

    @app.errorhandler(500)
    def not_processable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(400)
    def not_processable(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400   
        
    return app
