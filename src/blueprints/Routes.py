from flask import Blueprint, render_template


def construct_blueprint():
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    return routes
