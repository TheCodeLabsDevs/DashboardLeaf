from flask import Blueprint, render_template

from page.PageManager import PageManager


def construct_blueprint(settings, pageManager: PageManager):
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        pages = pageManager.get_all_pages()
        for page in pages:
            print(page)

        return render_template('index.html')

    return routes
