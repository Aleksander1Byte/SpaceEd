from data.db_session import global_init
import os
from flask import Flask, render_template
from flask_login import (
    current_user,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
global_init('db/database.db')
DEBUG = True

@app.route('/')
def main():
    return render_template(
        'homepage.html',
        title='SpaceEd',
        current_user=current_user,
    )


if __name__ == '__main__':
    if DEBUG:
        PORT = 5050
        HOST = '127.0.0.1'
    else:
        PORT = int(os.environ.get("PORT", 5000))
        HOST = '0.0.0.0'
    ADDRESS = HOST + ':' + str(PORT)
    app.run(host=HOST, port=PORT)
