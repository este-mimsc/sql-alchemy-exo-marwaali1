"""Minimal Flask application setup for the SQLAlchemy assignment."""
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# These extension instances are shared across the app and models
# so that SQLAlchemy can bind to the application context when the
# factory runs.
db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    """Application factory used by Flask and the tests.

    The optional ``test_config`` dictionary can override settings such as
    the database URL to keep student tests isolated.
    """

    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here so SQLAlchemy is aware of them before migrations
    # or ``create_all`` run. Students will flesh these out in ``models.py``.
    import models  # noqa: F401
    User = models.User
    Post = models.Post

    @app.route("/")
    def index():
        """Simple sanity check route."""
        return jsonify({"message": "Welcome to the Flask + SQLAlchemy assignment"})

    @app.route("/users", methods=["GET", "POST"])
    def users():
        """List or create users.

        TODO: Students should query ``User`` objects, serialize them to JSON,
        and handle incoming POST data to create new users.
        """
        if request.method == "GET":
            users = User.query.all()
            return jsonify([{"id": u.id, "username": u.username} for u in users])

        if request.method == "POST":
            data = request.get_json()
            if not data.get("username"):
                return jsonify({"error": "username is required"}), 400
            if User.query.filter_by(username=data["username"]).first():
                return jsonify({"error": "username already exists"}), 400

            user = User(username=data["username"])
            db.session.add(user)
            db.session.commit()
            return jsonify({"id": user.id, "username": user.username}), 201

    @app.route("/posts", methods=["GET", "POST"])
    def posts():
        """List or create posts.

        TODO: Students should query ``Post`` objects, include user data, and
        allow creating posts tied to a valid ``user_id``.
        """
        if request.method == "GET":
            posts = Post.query.all()
            return jsonify([
                {
                    "id": p.id,
                    "title": p.title,
                    "content": p.content,
                    "user_id": p.user_id,
                    "username": p.author.username
                } for p in posts
            ])

        if request.method == "POST":
            data = request.get_json()
            if not all(k in data for k in ("title", "content", "user_id")):
                return jsonify({"error": "title, content, and user_id are required"}), 400
            user = User.query.get(data["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 404

            post = Post(title=data["title"], content=data["content"], author=user)
            db.session.add(post)
            db.session.commit()
            return jsonify({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "user_id": post.user_id,
                "username": post.author.username
            }), 201

    return app


# Expose a module-level application for convenience with certain tools
app = create_app()


if __name__ == "__main__":
    # Running ``python app.py`` starts the development server.
    app.run(debug=True)
