from flask import Blueprint, render_template

from page.PageManager import PageManager


def construct_blueprint(settings, pageManager: PageManager):
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        pageNames = pageManager.get_all_available_page_names()
        return render_template('index.html', pageNames=pageNames)

    return routes
