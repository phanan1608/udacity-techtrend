from enum import Enum
import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys
import datetime

db_connection_count = 0
db_file = 'database.db'
log_file = 'app.log'

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    try:
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row
        global db_connection_count
        db_connection_count += 1
        return connection
    except Exception as e:
        app.logger.error('Error connecting to the database: %s', e)
        return None

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        log_message('A non-existing article is accessed and a 404 page is returned', level=logging.ERROR)
        return render_template('404.html'), 404
    else:
        post_title = post['title']
        log_message(f'Article "{post_title}" retrieved!')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    log_message('The "About Us" page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.error('Title is required!')
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            log_message(f'Article "{title}" created!')
            return redirect(url_for('index'))
        
    return render_template('create.html')

@app.route('/healthz')
def health_check():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    response = app.response_class(
        response=json.dumps({"db_connection_count": db_connection_count, "post_count": post_count}),
        status=200,
        mimetype='application/json'
    )
    return response

def create_log_message_with_time(message):
    now = datetime.datetime.now()
    return f'{now.strftime("%m/%d/%Y, %H:%M:%S")}, {message}'
    
def log_message(message, level=logging.INFO):
    if level == logging.ERROR:
        app.logger.error(create_log_message_with_time(message))
    else:
        app.logger.info(create_log_message_with_time(message))

def config_logger():
    global log_file
    
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.DEBUG)
    
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.DEBUG)
    
    handlers = [info_handler, logging.FileHandler(log_file, mode='w')]

    format_output = ('%(levelname)s: %(name)s: %(message)s')

    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)

# start the application on port 3111
if __name__ == "__main__":
    config_logger()
    app.run(host='0.0.0.0', port='3111')
