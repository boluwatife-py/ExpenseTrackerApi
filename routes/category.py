from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from utils.db import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Missing name field'}), 400
        
        # Validate name length
        if len(data['name']) < 1 or len(data['name']) > 50:
            return jsonify({'message': 'Category name must be between 1 and 50 characters'}), 400
        
        if Category.query.filter_by(name=data['name'], user_id=user_id).first():
            return jsonify({'message': 'Category already exists'}), 400
        
        category = Category(name=data['name'], user_id=user_id)
        db.session.add(category)
        db.session.commit()
        
        return jsonify({'message': 'Category created', 'category': category.to_dict()}), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error: Category name already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@category_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    try:
        user_id = get_jwt_identity()
        categories = Category.query.filter_by(user_id=user_id).all()
        return jsonify([category.to_dict() for category in categories]), 200
    
    except SQLAlchemyError as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@category_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    try:
        user_id = get_jwt_identity()
        category = Category.query.filter_by(id=id, user_id=user_id).first()
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Missing name field'}), 400
        
        # Validate name length
        if len(data['name']) < 1 or len(data['name']) > 50:
            return jsonify({'message': 'Category name must be between 1 and 50 characters'}), 400
        
        if Category.query.filter_by(name=data['name'], user_id=user_id).first():
            return jsonify({'message': 'Category name already exists'}), 400
        
        category.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Category updated', 'category': category.to_dict()}), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error: Category name already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@category_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    try:
        user_id = get_jwt_identity()
        category = Category.query.filter_by(id=id, user_id=user_id).first()
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        if category.expenses:
            return jsonify({'message': 'Cannot delete category with associated expenses'}), 400
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted'}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500