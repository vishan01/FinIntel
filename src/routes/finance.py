from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from src.models import db, Expense, Budget, Goal
from src.services.financial import FinancialService
from src.services.market_data import MarketDataService, fetch_top_stocks, fetch_stock_info, plot_stocks
from src.services.budget_alert import BudgetAlertService

# Initialize globals before blueprint creation
financial_service = None
market_service = None

def init_services(fin_service, mkt_service):
    global financial_service, market_service
    financial_service = fin_service
    market_service = mkt_service
finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/sip-calculator', methods=['GET', 'POST'])
@login_required
def calculate_sip():
    if request.method == 'GET':
        return render_template('sip_calculator.html')
    
    try:
        data = request.get_json()
        print("Received SIP calculation request:", data)  # Debug log
        
        if not data:
            print("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        # Extract and validate inputs
        try:
            monthly_investment = float(data.get('monthly_investment', 0))
            expected_return = float(data.get('expected_return', 0))
            years = int(data.get('years', 0))
        except (ValueError, TypeError) as e:
            print(f"Input conversion error: {str(e)}")
            return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
        
        # Validate values
        if monthly_investment <= 0:
            return jsonify({'error': 'Monthly investment must be greater than 0'}), 400
        if expected_return <= 0:
            return jsonify({'error': 'Expected return must be greater than 0'}), 400
        if years <= 0:
            return jsonify({'error': 'Investment period must be greater than 0'}), 400
            
        print(f"Processing SIP calculation: {monthly_investment=}, {expected_return=}, {years=}")
        
        result = financial_service.calculate_sip(
            monthly_investment=monthly_investment,
            expected_return=expected_return,
            years=years
        )
        
        print("SIP calculation result:", result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in SIP calculator: {str(e)}")
        return jsonify({'error': f'Failed to calculate SIP: {str(e)}'}), 500

@finance_bp.route('/expenses', methods=['POST'])
@login_required
def add_expense():
    data = request.get_json()
    expense = Expense(
        amount=float(data['amount']),
        category=data['category'],
        description=data.get('description', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
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
    
    expense.date = datetime.strptime(data['date'], '%Y-%m-%d')
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

@finance_bp.route('/stocks')
def top_stocks():
    """Display top stocks page."""
    stocks_data = fetch_top_stocks()
    return render_template('stocks.html', stocks=stocks_data)

@finance_bp.route('/my-watchlist')
@login_required
def my_watchlist():
    """Display user's stock watchlist."""
    stocks_data = []
    plot_url = ''
    if current_user.stock_tickers:
        tickers = current_user.stock_tickers.split(',')
        for ticker in tickers:
            stocks_data.append(fetch_stock_info(ticker))
        if tickers:
            plot_url = plot_stocks(tickers)
    return render_template('watchlist.html', stocks=stocks_data, plot_url=plot_url)

@finance_bp.route('/stock/<ticker>')
def get_stock_details(ticker):
    """Get details for a specific stock."""
    return jsonify(fetch_stock_info(ticker))

@finance_bp.route('/watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    """Add a stock to user's watchlist."""
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Please provide a ticker symbol', 'error')
        return redirect(url_for('home'))
        
    if market_service.add_stock_to_watchlist(ticker):
        flash(f'{ticker} added to watchlist', 'success')
    else:
        flash(f'{ticker} already in watchlist', 'info')
    return redirect(url_for('home'))

@finance_bp.route('/watchlist/<ticker>', methods=['POST', 'DELETE'])
@login_required
def remove_from_watchlist(ticker):
    """Remove a stock from user's watchlist."""
    # Handle both POST and DELETE methods for removal
    if request.method in ['POST', 'DELETE']:
        if market_service.remove_stock_from_watchlist(ticker):
            flash(f'{ticker} removed from watchlist', 'success')
        else:
            flash('Stock not in watchlist', 'error')
    return redirect(url_for('home'))

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
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.asc()).all()
    analysis = financial_service.analyze_expenses(expenses)
    
    # Add monthly trend data
    monthly_data = {}
    
    # Get all expenses from the last 12 months
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Initialize all months with 0
    current = start_date
    while current <= end_date:
        month_key = current.strftime('%Y-%m')
        monthly_data[month_key] = 0
        current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
    
    # Fill in actual expense data
    for expense in expenses:
        if start_date <= expense.date <= end_date:
            month_key = expense.date.strftime('%Y-%m')
            monthly_data[month_key] = monthly_data.get(month_key, 0) + expense.amount
    
    analysis['monthly_trend'] = [
        {
            'month': datetime.strptime(month, '%Y-%m').strftime('%b %Y'),
            'amount': amount
        }
        for month, amount in sorted(monthly_data.items())
    ]
    
    return jsonify(analysis)

@finance_bp.route('/goals', methods=['POST', 'PUT'])
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

@finance_bp.route('/goals/<int:goal_id>', methods=['PUT'])
@login_required
def update_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    goal.name = data['name']
    goal.target_amount = float(data['target_amount'])
    goal.current_amount = float(data.get('current_amount', 0))
    goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d')
    
    db.session.commit()
    
    savings_plan = financial_service.calculate_goal_savings(
        goal.target_amount,
        goal.target_date,
        goal.current_amount
    )
    
    return jsonify({
        'message': 'Goal updated successfully',
        'savings_plan': savings_plan
    })

@finance_bp.route('/goals/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Goal deleted successfully'})

@finance_bp.route('/goals')
@login_required
def goals():
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', goals=user_goals)

@finance_bp.route('/advice')
@login_required
def get_advice():
    return render_template('advice.html')

@finance_bp.route('/advice_info/<info>',methods=['GET'])
@login_required
def get_advice_info(info):
    topic=info
    try:
        advice_response = financial_service.get_financial_advice(topic,current_user.id)
        return jsonify(advice_response.get("html",""))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/chat-page')
@login_required
def chat_page():
    return render_template('chat.html')

@finance_bp.route('/chat')
@login_required
def chat():
    message = request.args.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = financial_service.Chat(message, current_user.id)
        return jsonify({'response': response.get("html","")})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500
