from views import *
from main import app, CONFIG
import time
from flask import send_file


if __name__ == '__main__':
    app.run(debug=CONFIG.DEBUG, host=CONFIG.HOST, port=CONFIG.PORT)