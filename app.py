import datetime
import logging

from flask import Flask, jsonify, request

# from DBOperation.db import select_query, add_record, update_rating, update_genre
from DBOperation import logs
from DBOperation.db_sqlite3 import select_query, add_record, update_rating, update_genre
from OMDb.api import OMDB

logs.initialize_logger("flask-imdb-api")

app = Flask(__name__)

api_key = "ghg678hjyui4589dfdshucv45218uyrgdd54"


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


@app.route('/')
def index():
    logging.debug("index")
    return jsonify({'message': 'Welcome To Movie Data API'})



# endpoint to get detail by title
@app.route("/movie/title", methods=["GET"])
def movie_detail_by_title():
    title = request.args['title']
    db_result = {'data': select_query("SELECT * FROM movie_details WHERE title LIKE'{0}' limit 1".format(title))}
    if not db_result['data']:
        obj = OMDB(apikey=api_key)
        obj.get(title=title)
        add_record(obj)
        db_result = {'data': select_query("SELECT * FROM movie_details WHERE title LIKE'{0}' limit 1".format(title))}
        if not db_result:
            return jsonify({'message': 'No data found!'}), 404

    print(db_result)
    genre_result = select_query("SELECT genre FROM movie_genres WHERE id='{0}'".format(db_result['data'][0]['id']))
    print(genre_result)
    db_result['data'][0]['genres'] = list(genre['genre'] for genre in genre_result)
    db_result['time'] = datetime.datetime.now()
    return jsonify(db_result)


# endpoint to get detail by id
@app.route("/movie/<id>", methods=["GET"])
def movie_detail_by_id(id):
    db_result = {'data': select_query("SELECT * FROM movie_details WHERE id='{0}' limit 1".format(id))}
    if not db_result['data']:
        return jsonify({'message': 'No data found in local!'}), 404

    genre_result = select_query("SELECT genre FROM movie_genres WHERE id='{0}'".format(id))
    db_result['data'][0]['genres'] = list(genre['genre'] for genre in genre_result)
    db_result['time'] = datetime.datetime.now()
    return jsonify(db_result)

