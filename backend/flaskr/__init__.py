import json
from logging import exception
import os
from tkinter.messagebox import NO
from token import EXACT_TOKEN_TYPES
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
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
    Use the after_request decorator to set Access-Control-Allow
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
    Create an endpoint to handle GET requests
    for all available categories.
    """

    # working fine
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        categories_formatted = {
            item['id']: item['type'] for item in formatted_categories
            }

        if formatted_categories == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": categories_formatted
        }), 200

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]
        categories_formatted = {
            item['id']: item['type'] for item in formatted_categories
            }

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(Question.query.order_by(Question.id).all()),
            "categories": categories_formatted,
            "current_category": 'All',
        }), 200

    """
    Create an endpoint to DELETE question using a question ID.
    """

    # working fine
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "deleted_id": question_id,
                "Total_questions": len(current_questions),
            }), 200
        except Exception as e:
            print(e)
            abort(422)

    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        searchTerm = body.get('searchTerm', None)

        try:
            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                )
                current_question = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "question": current_question,
                        "total_questions": len(selection.all()),
                    }
                )
            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category
                    )
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_question = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_question,
                        "total_questions": len(Question.query.all()),
                    }
                )
        except Exception as e:
            print(e)
            abort(422)
    """
    Create a GET endpoint to get questions based on category.
    """

    # working fine
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def list_category(category_id):
        try:
            category = Category.query.filter(Category.id == category_id).one()
            questions = Question.query.filter(Question.category == category_id)
            formatted_question = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": formatted_question,
                "total_questions": len(Question.query.all()),
                "current_category": category.format().get('type')
            }), 200
        except Exception as e:
            print(e)
            abort(404)

    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():

        try:
            body = request.get_json()
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')
            print(quiz_category, previous_questions)

            if quiz_category != 0:
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))
                    ).all()
                print(available_questions)
            else:
                available_questions = Question.query.filter_by(
                    category=quiz_category['id']).filter(
                        Question.id.notin_((previous_questions))
                    ).all()
                print(available_questions)

            new_question = available_questions[
                random.randrange(0, len(available_questions))
                ].format() if len(available_questions) > 0 else None
            return jsonify({
                "success": True,
                "question": new_question
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404,

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
            }), 422,

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
            }), 400

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
            }), 500

    return app
