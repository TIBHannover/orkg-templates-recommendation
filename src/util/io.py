import os
import json


class Writer:

    def validate_path(func):
        """
            Last argument of functions using this decorator must be a path
        """

        def wrapper(self, *args, **kwargs):
            if not os.path.exists(os.path.dirname(args[-1])):
                os.makedirs(os.path.dirname(args[-1]))
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    @validate_path
    def write_json(json_data, output_path):
        with open(output_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    @staticmethod
    @validate_path
    def write_png(image, output_path):
        image.save(output_path)


class Reader:

    @staticmethod
    def read_json(input_path):
        with open(input_path, encoding='utf-8') as f:
            json_data = json.load(f)

        return json_data
