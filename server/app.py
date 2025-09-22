#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


api = Api(app)

# GET /restaurants
class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict(rules=("-restaurant_pizzas",)) for r in restaurants], 200

# GET /restaurants/<int:id>, DELETE /restaurants/<int:id>
class RestaurantByIdResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(rules=("restaurant_pizzas",)), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204

# GET /pizzas
class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        # Exclude 'restaurant_pizzas' from output
        return [p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas], 200

# POST /restaurant_pizzas
class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(rp)
            db.session.commit()
        except Exception:
            return {"errors": ["validation errors"]}, 400
        return rp.to_dict(rules=("pizza", "restaurant")), 201

# Add resources to API
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantByIdResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
