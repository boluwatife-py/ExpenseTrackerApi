from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from utils.db import db
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate input lengths
        if len(data['username']) < 3 or len(data['password']) < 6:
            return jsonify({'message': 'Username must be at least 3 characters and password at least 6 characters'}), 400
        
        if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Username or email already exists'}), 400
        
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error: Username or email already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200
    
    except SQLAlchemyError as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500