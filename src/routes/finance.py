from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime
from src.models import db, Expense, Budget, Goal
from src.services.financial import FinancialService
from src.services.market_data import MarketDataService
from src.services.budget_alert import BudgetAlertService

finance_bp = Blueprint('finance', __name__)
financial_service = FinancialService()
market_service = MarketDataService()

@finance_bp.route('/sip-calculator', methods=['GET', 'POST'])
def calculate_sip():
    if request.method == 'GET':
        return render_template('sip_calculator.html')
    
    data = request.get_json()
    result = financial_service.calculate_sip(
        monthly_investment=float(data['monthly_investment']),
        expected_return=float(data['expected_return']),
        years=int(data['years'])
    )
    return jsonify(result)

@finance_bp.route('/expenses', methods=['POST'])
@login_required
def add_expense():
    data = request.get_json()
    expense = Expense(
        amount=float(data['amount']),
        category=data['category'],
        description=data.get('description', ''),
        date=datetime.now(),
        user_id=current_user.id
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully', 'id': expense.id})

@finance_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    expense.amount = float(data['amount'])
    expense.category = data['category']
    expense.description = data.get('description', '')
    
    db.session.commit()
    return jsonify({'message': 'Expense updated successfully'})

@finance_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted successfully'})

@finance_bp.route('/market-data')
def get_market_data():
    """Get current market data."""
    data = market_service.get_market_indices()
    return jsonify(data)

@finance_bp.route('/budget/alerts')
@login_required
def get_budget_alerts():
    """Get budget alerts for the current user."""
    alerts = BudgetAlertService.check_budget_status(current_user.id)
    return jsonify(alerts)

@finance_bp.route('/expenses')
@login_required
def expenses():
    user_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    alerts = BudgetAlertService.check_budget_status(current_user.id)
    return render_template('expenses.html', expenses=user_expenses, alerts=alerts)

@finance_bp.route('/expenses/analysis')
@login_required
def analyze_expenses():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        analysis = financial_service.analyze_expenses(expenses)
        print("Analysis data:", analysis)  # Debug print
        return jsonify(analysis)
    return render_template('expenses.html')

@finance_bp.route('/goals', methods=['POST'])
@login_required
def create_goal():
    data = request.get_json()
    goal = Goal(
        name=data['name'],
        target_amount=float(data['target_amount']),
        current_amount=float(data.get('current_amount', 0)),
        target_date=datetime.strptime(data['target_date'], '%Y-%m-%d'),
        user_id=current_user.id
    )
    db.session.add(goal)
    db.session.commit()
    
    # Calculate required savings
    savings_plan = financial_service.calculate_goal_savings(
        goal.target_amount,
        goal.target_date,
        goal.current_amount
    )
    
    return jsonify({
        'message': 'Goal created successfully',
        'savings_plan': savings_plan
    })

@finance_bp.route('/goals')
@login_required
def goals():
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', goals=user_goals)

@finance_bp.route('/advice')
async def get_advice():
    topic = request.args.get('topic', 'personal finance basics')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            advice = await financial_service.get_financial_advice(topic)
            return jsonify({'advice': advice})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('advice.html')

@finance_bp.route('/chat')
async def chat():
    message = request.args.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = await financial_service.get_financial_advice(message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
