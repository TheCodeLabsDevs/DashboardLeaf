from flask import Blueprint, render_template

from page.PageManager import PageManager


def construct_blueprint(settings, pageManager: PageManager):
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        pageNames = pageManager.get_all_available_page_names()
        return render_template('index.html', pageNames=pageNames)

    @routes.route('/page/<pageName>', methods=['GET'])
    def show_page(pageName: str):
        pageInstance = pageManager.get_page_instance_by_name(pageName)
        return render_template('page.html', pageContent=pageInstance.update())

    return routes
