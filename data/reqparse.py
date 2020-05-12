from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('player_id', required=True)
parser.add_argument('email', required=True)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('name', required=True, type=str)
parser.add_argument('nickname', required=True, type=str)
parser.add_argument('public', required=True, type=bool)


parser2 = reqparse.RequestParser()
parser2.add_argument('email', required=True, type=str)
parser2.add_argument('password', required=True, type=str)
