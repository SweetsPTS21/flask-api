import json

from flask import Flask
from flask_restful import Resource, Api
from services.CF import get_data, show_data, rec_with_ratings
import os


class Recommendation(Resource):
    def get(self, user_id: str):
        file_path = "data/cf0.json"

        # Load data from the JSON file
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        # Print the loaded data for debugging
        print(data)

        # Check if user_id exists in data
        if user_id in data:
            recommend_items = data[user_id]
            return {"user_id": user_id, "recommend_items": recommend_items}
        else:
            return {"error": f"No recommendations found for user {user_id}"}


class Build(Resource):
    def get(self):
        get_data()
        data = show_data()
        result = rec_with_ratings()

        file_path_0 = "data/cf0.json"

        # Save the data to a JSON file
        with open(file_path_0, "w") as json_file:
            json.dump(result[0], json_file)

        print(f"Data cf0 has been saved to {file_path_0}")

        file_path_1 = "src/data/cf1.json"

        # Save the data to a JSON file
        with open(file_path_1, "w") as json_file:
            json.dump(result[1], json_file)

        print(f"Data cf1 has been saved to {file_path_1}")

        return f"data: {data} \nresult: {result}"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
        )
    else:
        app.config.from_mapping(test_config)

    @app.get("/")
    def index():
        return "Hello ???"

    api.add_resource(Recommendation, "/recommendation/<string:user_id>")
    api.add_resource(Build, "/build")

    return app
