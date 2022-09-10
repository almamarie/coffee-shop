from crypt import methods
import os
from types import new_class
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
 uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@ implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    return jsonify({"success": True, "drinks": drinks})


'''
@ implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def get_all_drinks_details(payload):
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({"success": True, "drinks": drinks})


'''
@ implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def add_new_drink(payload):
    try:
        body = request.get_json()
        # print("\nbody: ", body)

        title = body.get('title')
        recipe = body.get('recipe')
        # print("\n\nrecipe: ", recipe, "\n\n")
        new_Drink = Drink(
            title=body.get('title'),
            recipe=json.dumps(recipe)
        )
        print(new_Drink.title)
        print(new_Drink.recipe)

        new_Drink.insert()
    except:
        print(sys.exc_info())
        abort(422)

    drink = Drink.query.filter(Drink.title == title).one()
    # print("\n Drink: ", drink)
    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_a_drink(payload, id):
    body = request.get_json()
    drink_to_patch = Drink.query.filter(Drink.id == id).one_or_none()

    if drink_to_patch is None:
        abort(404)

    if 'title' in body:
        drink_to_patch.title = body.get('title')
        print("title: ", body.get('title'))

    if 'recipe' in body:
        drink_to_patch.recipe = json.dumps(body.get('recipe'))
        print("recipe: ", body.get('recipe'))

    try:
        drink_to_patch.update()
    except:
        print(sys.exc_info())
        abort(400)

    print(drink_to_patch)
    return jsonify({
        "success": None,
        "drinks": [drink_to_patch.long()]
    })


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_a_drink(payload, id):
    drink_to_delete = Drink.query.filter(Drink.id == id).one_or_none()

    if drink_to_delete is None:
        abort(404)
    try:
        drink_to_delete.delete()
    except:
        abort(400)

    return jsonify({
        "success": True,
        "delete": id
    })

# Error Handling


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404,
                "message": "resource not found"}),
        404,
    )


@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422,
                "message": "unprocessable"}),
        422,
    )


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


@app.errorhandler(405)
def not_found(error):
    return (
        jsonify({"success": False, "error": 405,
                "message": "method not allowed"}),
        405,
    )


@app.errorhandler(500)
def server_error(error):
    return (
        jsonify({"success": False, "error": 500,
                "message": "server error"}),
        500,
    )


@app.errorhandler(401)
def authentication_error(error):
    return (
        jsonify({"success": False, "error": 401,
                "message": "could not verify"}),
        401,
    )
