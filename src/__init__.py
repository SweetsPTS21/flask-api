import json

from flask import Flask
from flask_restful import Resource, Api
from src.CF import get_data, show_data, rec_with_ratings
import os


class Recommendation(Resource):
    def get(self, user_id: str):
        file_path = "data/cf0.json"

        # Load data2 from the JSON file
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        # Print the loaded data for debugging
        # print(data)

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

        # show data from mongoDB
        print(f"mongoDB data: {data}")

        # build recommendation model
        result = rec_with_ratings()

        # Specify the directory where you want to save the json file
        directory = 'data'

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Specify the path for the json file within the directory
        file_path_0 = os.path.join(directory, 'cf0.json')

        # Save the data2 to a JSON file
        with open(file_path_0, "w") as json_file:
            json.dump(result[0], json_file)

        print(f"Data cf0 has been saved to {file_path_0}")

        file_path_1 = os.path.join(directory, 'cf1.json')

        # Save the data2 to a JSON file
        with open(file_path_1, "w") as json_file:
            json.dump(result[1], json_file)

        print(f"Data cf1 has been saved to {file_path_1}")

        return f"result: {result}"


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

    api.add_resource(Recommendation, "/recommend/<string:user_id>")
    api.add_resource(Build, "/build")

    return app
