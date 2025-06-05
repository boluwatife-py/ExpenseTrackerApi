from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.expense import Expense
from models.category import Category
from utils.db import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import dateutil.parser

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or not all(k in data for k in ['amount', 'description', 'category_id']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate amount
        if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
            return jsonify({'message': 'Amount must be a positive number'}), 400
        
        # Validate description length
        if len(data['description']) > 200:
            return jsonify({'message': 'Description too long (max 200 characters)'}), 400
        
        # Validate category
        if Category.query.filter_by(id=data['category_id'], user_id=user_id).first() is None:
            return jsonify({'message': 'Invalid category'}), 400
        
        # Parse date if provided
        date = datetime.utcnow()
        if 'date' in data:
            try:
                date = dateutil.parser.parse(data['date'])
            except ValueError:
                return jsonify({'message': 'Invalid date format'}), 400
        
        expense = Expense(
            amount=data['amount'],
            description=data['description'],
            category_id=data['category_id'],
            user_id=user_id,
            date=date
        )
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({'message': 'Expense created', 'expense': expense.to_dict()}), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    try:
        user_id = get_jwt_identity()
        expenses = Expense.query.filter_by(user_id=user_id).all()
        return jsonify([expense.to_dict() for expense in expenses]), 200
    
    except SQLAlchemyError as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@expense_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_expense(id):
    try:
        user_id = get_jwt_identity()
        expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        if not expense:
            return jsonify({'message': 'Expense not found'}), 404
        return jsonify(expense.to_dict()), 200
    
    except SQLAlchemyError as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@expense_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    try:
        user_id = get_jwt_identity()
        expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        if not expense:
            return jsonify({'message': 'Expense not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        if 'amount' in data:
            if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
                return jsonify({'message': 'Amount must be a positive number'}), 400
            expense.amount = data['amount']
        
        if 'description' in data:
            if len(data['description']) > 200:
                return jsonify({'message': 'Description too long (max 200 characters)'}), 400
            expense.description = data['description']
        
        if 'category_id' in data:
            if Category.query.filter_by(id=data['category_id'], user_id=user_id).first() is None:
                return jsonify({'message': 'Invalid category'}), 400
            expense.category_id = data['category_id']
        
        if 'date' in data:
            try:
                expense.date = dateutil.parser.parse(data['date'])
            except ValueError:
                return jsonify({'message': 'Invalid date format'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Expense updated', 'expense': expense.to_dict()}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@expense_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    try:
        user_id = get_jwt_identity()
        expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        if not expense:
            return jsonify({'message': 'Expense not found'}), 404
        
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted'}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500