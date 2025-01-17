from flask import Flask

from database import db_session
from flask_graphql import GraphQLView
from schema import schema
from flask import request

app = Flask(__name__)
app.debug = True

app.add_url_rule(rule='/graphql', endpoint= 'graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True, context={'session': db_session}))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    print('run')
    app.run()
    