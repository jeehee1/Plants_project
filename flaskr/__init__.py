from flask import Flask, jsonify, request, abort
from flask_cors.decorator import cross_origin
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.sqltypes import BOOLEAN, Boolean, String
from sqlalchemy.sql.type_api import BOOLEANTYPE
from models import setup_db, Plant
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    #CORS(app, resources={r"*/api/*" : {'origins' : '*'}})
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'Get, POST, PATCH, DELETE, OPTION')
        return response

    #@cross_origin
    @app.route('/plants', methods=['GET'])
    def get_plants():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        plants = Plant.query.all()
        formatted_plants = [plant.format() for plant in plants]
        return jsonify({
            'success' : True,
            'plants' : formatted_plants[start:end],
            'total_plants' : len(formatted_plants)
        })

    @app.route('/plants', methods=['POST'])
    def create_plant():
        body=request.get_json()
        new_name = body.get('name', None)
        new_scientific_name = body.get('scientific_name', None)
        new_is_poisonous = body.get('is_poisonous', None)
        new_primary_color = body.get('primary_color', None)

        if new_is_poisonous:
            new_poisonous = bool(new_is_poisonous)

        try:
            plant = Plant(
                name=new_name, 
                scientific_name=new_scientific_name, 
                is_poisonous=new_poisonous, 
                primary_color=new_primary_color
            )
            plant.insert()

            return jsonify({
                'success' : True,
                'created_id' : plant.id
            })
        except:
            abort(422)

    @app.route('/plants/<int:plant_id>', methods=['GET'])
    def get_specific_plant(plant_id):

        plant = Plant.query.filter(Plant.id == plant_id).one_or_none()

        if plant is None:
            abort(404)
        
        else:
            return jsonify({
                'success' : True,
                'plant' : plant.format()
            })

    @app.route('/plants/<int:plant_id>', methods=['PATCH'])
    def update_plant(plant_id):
        body=request.get_json()
        try:
            plant = Plant.query.filter(Plant.id==plant_id).one_or_none()
            if plant is None:
                abort(404)
            if 'scientific_name' in body:
                plant.scientific_name = body.get('scientific_name')
            # if 'is_poisonous' in body:
            #     plant.is_poisonous = body.get('is_poisonous')
            if 'primary_color' in body:
                plant.primary_color = body.get('primary_color')
            plant.update()

            return jsonify({
                'success' : True,
                'plant' : plant.format()
            })
        except:
            abort(400)

        

    @app.route('/plants/<int:plant_id>', methods=['DELETE'])
    def delete_plant(plant_id):
        plant = Plant.query.filter(Plant.id==plant_id).one_or_none()
        if plant is None:
            abort(404)
        try:
            plant.delete()
            return jsonify({
                'success' : True,
                'delete_plant' : plant_id,           
            })
        except:
            abort(422)



    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success' : False,
            'error' : 404,
            'message' : "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success' : False,
            'error' : 422,
            'message' : "unprocessable"
        }), 422

    return app
