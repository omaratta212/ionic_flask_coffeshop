import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink

from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def drinks():
	success = False
	drinks_formatted = {}
	try:
		drinks = Drink.query.all()
		drinks_formatted = [drink.short() for drink in drinks]
		success = True
	except Exception as e:
		print(e)

	return {
		"success": success,
		"drinks": drinks_formatted
	}


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details():
	success = False
	drinks_formatted = {}
	try:
		drinks = Drink.query.all()
		drinks_formatted = [drink.long() for drink in drinks]
		success = True
	except Exception as e:
		print(e)

	return {
		"success": success,
		"drinks": drinks_formatted
	}


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
	success = False
	drink = Drink(title=request.json.get('title'), recipe=json.dumps(request.json.get('recipe')))

	try:
		drink.insert()
		success = True
	except Exception as e:
		print(e)

	return jsonify({
		"success": success,
		"drink": drink.long() if success else None
	})


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
	success = False
	drink = Drink.query.get_or_404(drink_id)
	try:
		drink.title = request.json.get('title')
		drink.recipe = json.dumps(request.json.get('recipe'))
		drink.update()
		success = True
	except Exception as e:
		print(e)

	return jsonify({
		"success": success,
		"drink": drink.long() if success else None
	})


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
	success = False
	drink = Drink.query.get_or_404(drink_id)

	try:
		drink.delete()
		success = True
	except Exception as e:
		print(e)

	return jsonify({
		"success": success,
		"delete": drink_id
	})


## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
	return jsonify({
		"success": False,
		"error": 422,
		"message": "unprocessable"
	}), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def not_found_error(error):
	return jsonify({
		"success": False,
		"error": 404,
		"message": str(error),
	}), 404


@app.errorhandler(500)
def server_error(error):
	return jsonify({
		"success": False,
		"error": 500,
		"message": str(error),
	}), 500


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def unauthorized_error(error):
	return jsonify({
		"success": False,
		"error": error.status_code,
		"message": str(error)
	}), error.status_code
