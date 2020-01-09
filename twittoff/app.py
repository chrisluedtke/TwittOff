"""Main application and routing logic."""
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import func
from flask import Flask, redirect, render_template, request, url_for

from .models import DB, User
from .twitter import add_or_update_user, update_all_users
from .predict import predict_user


load_dotenv()


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ENV'] = getenv('FLASK_ENV')
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.order_by(func.lower(User.name)).all()
        return render_template('index.html', title='Home', 
                               users=users)

    @app.route('/update')
    def update():
        update_all_users()
        return redirect(url_for('root'))

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return redirect(url_for('root'))

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                db_user = add_or_update_user(name)
                message = f"User {db_user.name} successfully added!"
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = "Error adding or fetching {}: {}".format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']
        if user1 == user2:
            # TODO: error message
            return redirect(url_for('root'))
        else:
            pre_dict = predict_user(user1, user2, tweet_text)
        return render_template('prediction.html', title='Prediction', 
                               tweet_text=tweet_text, pre_dict=pre_dict)

    return app
