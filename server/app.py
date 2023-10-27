#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask import Flask, jsonify, request
import os
import logging
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)

@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    return jsonify([camper.to_dict() for camper in campers])

@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    camper_dict = camper.to_dict()
    camper_dict['signups'] = [signup.to_dict() for signup in camper.signups]
    return jsonify(camper_dict)

@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.json
    if not data:
        return jsonify({"errors": ["No data provided"]}), 400
    if 'name' not in data or not data['name'].strip():
        return jsonify({"errors": ["Invalid or missing name"]}), 400
    if 'age' not in data or not isinstance(data['age'], int) or not (0 <= data['age'] <= 120):
        return jsonify({"errors": ["Invalid or missing age"]}), 400
    try:
        camper = Camper(name=data['name'].strip(), age=data['age'])
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict()), 201
    except (AssertionError, IntegrityError) as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
    except ValueError as e:  # Catch the ValueError
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400  # Return the error message from the exception
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    data = request.json
    if not data:
        return jsonify({"errors": ["No data provided"]}), 400
    try:
        if 'name' in data:
            if not data['name'].strip():
                raise ValueError("Invalid name")
            camper.name = data['name'].strip()
        if 'age' in data:
            if not isinstance(data['age'], int) or not (0 <= data['age'] <= 120):
                raise ValueError("Invalid age")
            camper.age = data['age']
        db.session.commit()
        return jsonify(camper.to_dict()), 202
    except (ValueError, AssertionError, IntegrityError):
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500

@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict() for activity in activities])

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    db.session.delete(activity)
    db.session.commit()
    return '', 204

@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.json
    if not data or 'time' not in data or not isinstance(data['time'], int) or not (0 <= data['time'] <= 23) or 'camper_id' not in data or 'activity_id' not in data:
        return jsonify({"errors": ["validation errors"]}), 400
    try:
        signup = Signup(time=data['time'], camper_id=data['camper_id'], activity_id=data['activity_id'])
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict()), 201
    except (AssertionError, IntegrityError):
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)