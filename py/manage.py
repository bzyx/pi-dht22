# -*- coding: utf-8 -*-

from flask.ext.script import Manager

from dht22_www import create_app

app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run(threaded=True)


@manager.command
def runpublic():
    """Run in web mode"""
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    manager.run()
