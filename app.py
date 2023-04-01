from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models.users import User
from config import db, SECRET_KEY
from os import environ, path, getcwd
from dotenv import load_dotenv

load_dotenv(path.join(getcwd(), '.env'))

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get('DB_URI') 
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = SECRET_KEY
    db.init_app(app)
    print("DB Initialized Successfully")


    with app.app_context():
        @app.route('/user', methods=['POST'])
        def create_user():
            data = request.get_json()
            user_id = data.get('user_id')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone = data.get('phone')

            if not all([user_id, first_name, last_name, email, phone]):
                return jsonify({'error': 'Missing required fields.'}), 400

            if User.query.filter_by(user_id=user_id).first():
                return jsonify({'error': 'User already exists with the same user ID.'}), 400

            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'User already exists with the same email.'}), 400

            if User.query.filter_by(phone=phone).first():
                return jsonify({'error': 'User already exists with the same phone number.'}), 400

            user = User(user_id=user_id, first_name=first_name, last_name=last_name, email=email, phone=phone)
            db.session.add(user)
            db.session.commit()

            return jsonify({'message': 'User created successfully.'}), 201


        @app.route('/user/<user_id>', methods=['GET', 'POST'])
        def update_user(user_id):
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({'error': 'User does not exist with the given user ID.'}), 404
            
            if request.method == 'GET':
                return jsonify({
                    'user_id': user.user_id,
                    'email': user.email,
                    'phone': user.phone
                }), 200
            
            if request.method == 'POST':
                data = request.get_json()
                email = data.get('email')
                phone = data.get('phone')

                if not email and not phone:
                    return jsonify({'error': 'Missing fields to update.'}), 400

                if email:
                    if User.query.filter(User.email == email, User.id != user.id).first() is not None:
                        return jsonify({'error': 'User already exists with the same email.'}), 400
                    user.email = email

                if phone:
                    if User.query.filter(User.phone == phone, User.id != user.id).first() is not None:
                        return jsonify({'error': 'User already exists with the same phone number.'}), 400
                    user.phone = phone

                db.session.commit()

                return jsonify({'message': 'User updated successfully.'}), 200


        
        
        # db.drop_all()
        db.create_all()
        db.session.commit()
        return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
