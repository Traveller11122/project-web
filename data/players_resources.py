from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.player import Player
from data.reqparse import parser, parser2


def abort_if_player_not_found(player_id):
    session = db_session.create_session()
    player = session.query(Player).get(player_id)
    if not player:
        abort(404, message=f"Player {player_id} not found")


class PlayerResource(Resource):
    def get(self, player_id):
        abort_if_player_not_found(player_id)
        session = db_session.create_session()
        player = session.query(Player).get(player_id)
        return jsonify({'player': player.to_dict(
            only=('player_id', 'email', 'surname', 'name', 'nickname', 'place', 'points'))})

    def delete(self, player_id):
        abort_if_player_not_found(player_id)
        session = db_session.create_session()
        player = session.query(Player).get(player_id)
        session.delete(player)
        session.commit()
        return jsonify({'success': 'OK'})


class PlayersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        players = session.query(Player).all()
        return jsonify({'players': [item.to_dict(
            only=('player_id', 'email', 'surname', 'name', 'nickname', 'place', 'points')) for item in players]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        player = Player(
            surname=args['surname'],
            name=args['name'],
            nickname=args['nickname'],
            player_id=args['player_id'],
            email=args['email'],
            public=args['public']
        )
        session.add(player)
        session.commit()
        return jsonify({'success': 'OK'})


class PlayerInGame(Resource):
    def get(self):
        args = parser2.parse_args()
        session = db_session.create_session()
        player = session.query(Player).filter(Player.email == args['email']).first()
        if player.check_password(args['password']):
            return jsonify({'success': 'OK'})
        return jsonify({'failed': 'wrong email or password'})
