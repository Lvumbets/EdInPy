from flask_restful import reqparse

lesson_parser = reqparse.RequestParser()
lesson_parser.add_argument('title')
lesson_parser.add_argument('description')

task_parser = reqparse.RequestParser()
task_parser.add_argument('title')
task_parser.add_argument('condition')
task_parser.add_argument('examples')
task_parser.add_argument('less_id')