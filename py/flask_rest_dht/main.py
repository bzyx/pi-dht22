'''
Created on 30 lip 2013

@author: Marcin Jabrzyk
'''

import sqlite3
from flask import Flask, g
from flask.ext import restful

DATABASE = ''

DB_GET_MEASUREMENT_COMMAND = """
    SELECT timestamp, temp, humid, id FROM measurement WHERE id in
    (SELECT value FROM settings WHERE key = "last_measurement_id");
    """

app = Flask(__name__)
api = restful.Api(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class IndexAPI(restful.Resource):
    def get(self):
        return {'index': 'EMPTY',
                }


class DHT(restful.Resource):
    def get(self):
        cur = get_db().cursor()
        cur.execute(DB_GET_MEASUREMENT_COMMAND)
        data = cur.fetchone()
        try:
            assert(len(data) == 4)
        except AssertionError:
            return {
                'status': 500,
                'message': "AssertionError"
                }

        return {'status': 200,
                'timestamp': data[0],
                'temperature': data[1],
                'humidity': data[2],
                'id': data[3],
                }

#api.add_resource(IndexAPI, '/')
api.add_resource(DHT, '/api/dht/last')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
