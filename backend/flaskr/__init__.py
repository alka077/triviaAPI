import json
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        categories= Category.query.all()
        formatted_categories =[category.format() for category in categories] 

        if formatted_categories == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": formatted_categories,
            "total_categories": len(formatted_categories)
        }), 200


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/api/questions' , methods = ['GET'])
    def get_questions():

        #categories= Category.query.all()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        categories = Category.query.order_by(Category.id).all()
        formated_categories = [category.format() for category in categories]
        formated_formated_categories = {item['id']:item['type'] for item in formated_categories}
        return jsonify({
            'questions': current_questions,
            'total_questions':len(Question.query.order_by(Question.id).all()),
            'Current_category': formated_categories,
            'categories': formated_formated_categories
        }), 200

        # selection = Question.query.distinct(Question.category).order_by(Question.category).all()
        # current_question = paginate_questions(request, selection)
        

        # return jsonify({
        #     "success": True,
        #     "questions": current_question,
        #     "total_questions": len(Question.query.all()),
        #     "current_category": get_categories(),
        # })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/api/questions/<int:question_id>', methods = ['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question == None:
                abort(405)
            
            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)


            return jsonify({
                "success": True,
                "deleted_id": question_id,
                "questions": current_questions,
                "total_questions": len(selection)

            }), 200
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/api/questions', methods = ['POST'])
    def create_question():
        
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:
            question = Question(question = new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            Question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "created_question": question.id,
                "question": current_questions,
                "total_question": len(Question.query.all())
            }), 200
        except:
            abort(422)
    

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/api/question/search', methods =['POST'])
    def search_question():

        search_item = request.get_json().get('search_term')
        try:
            selection = Question.query.filter(Question.question.ilike('%' + search_item + '%')).first()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "question": current_questions,
                "search_item": len(selection)
            }), 200
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
    def list_category(category_id):

        category = Category.query.filter(Category.id == category_id).one()
        questions = Question.query.filter(Question.category == category_id)
        formatted_question = [question.format() for question in questions]

        return jsonify({
            "success": True,
            "current_question": formatted_question,
            "current_category": category.format()
        }), 200

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/api/quizzes', methods = ['POST'])
    def get_quizz():
        try:
            body = request.get_json()
            previous_questions = body.get_json('previous_question')
            quiz_category = body.get_json('quiz_category')

            if int(quiz_category['id']) == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == quiz_category['id']).all()
            
            formated_questions = [q.format() for q in questions]
            if len(questions) == 0:
                abort(404)
            question = random.choice(formated_questions)
            while True:
                if int(question['id']) in previous_questions:
                    question = random.choice(formated_questions)
                else:
                    break  
        
            return jsonify({
                "success": True,
                "question":questions,
                "total_questions":len(Question.query.all())
                }), 200
        except:
            return abort(422)    


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


    return app

