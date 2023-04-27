from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('id', required=False)
parser.add_argument('title', required=True)
parser.add_argument('description', required=True)
parser.add_argument('video_path', required=False)
parser.add_argument('picture_path', required=False)
parser.add_argument('allowed_groups', required=True)
