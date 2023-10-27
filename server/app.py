#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask import Flask, jsonify, request
import os
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
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    camper_dict = camper.to_dict()
    camper_dict['signups'] = [signup.to_dict() for signup in camper.signups]
    return jsonify(camper_dict)

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    data = request.json
    try:
        if 'name' in data:
            camper.name = data['name']
        if 'age' in data:
            camper.age = data['age']
        db.session.commit()
        return jsonify(camper.to_dict()), 202
    except AssertionError as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.json
    try:
        camper = Camper(name=data['name'], age=data['age'])
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict()), 201
    except (AssertionError, IntegrityError) as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict() for activity in activities])

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    db.session.delete(activity)
    db.session.commit()
    return '', 204

@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.json
    try:
        signup = Signup(time=data['time'], camper_id=data['camper_id'], activity_id=data['activity_id'])
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict()), 201
    except (AssertionError, IntegrityError) as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)