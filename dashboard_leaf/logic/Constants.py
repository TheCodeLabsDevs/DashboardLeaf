import os

from TheCodeLabs_BaseUtils.Color import Color

APP_NAME = 'DashboardLeaf'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')


# colors
RED = Color(230, 76, 60)
ORANGE = Color(254, 151, 0)
GREEN = Color(117, 190, 84)
BLUE = Color(70, 138, 221)
WHITE = Color(255, 255, 255)
