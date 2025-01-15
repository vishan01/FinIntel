import google.generativeai as genai
from datetime import datetime
import markdown
from functools import lru_cache
from src.models import Expense, Budget, Goal
from flask import current_app
from datetime import datetime, timedelta

class FinancialService:

    def call(self,user_id):
        
        # Get user's financial data from the last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        
        with current_app.app_context():
            # Get expenses
            expenses = Expense.query.filter_by(user_id=user_id)\
                .filter(Expense.date >= six_months_ago)\
                .order_by(Expense.date.desc()).all()
            
            # Get budgets
            budgets = Budget.query.filter_by(user_id=user_id)\
                .filter(Budget.month >= six_months_ago)\
                .all()
            
            # Get goals
            goals = Goal.query.filter_by(user_id=user_id).all()
            
            # Format data for the AI
            self.expense_data = [
                {
                    'amount': expense.amount,
                    'category': expense.category,
                    'date': expense.date.strftime('%Y-%m-%d'),
                    'description': expense.description
                }
                for expense in expenses
            ]
            
            self.budget_data = [
                {
                    'category': budget.category,
                    'amount': budget.amount,
                    'month': budget.month.strftime('%Y-%m')
                }
                for budget in budgets
            ]
            
            self.goal_data = [
                {
                    'name': goal.name,
                    'target_amount': goal.target_amount,
                    'current_amount': goal.current_amount,
                    'target_date': goal.target_date.strftime('%Y-%m-%d')
                }
                for goal in goals
            ]
            
            # Calculate total expenses and savings
            total_expenses = sum(expense.amount for expense in expenses)
            total_budget = sum(budget.amount for budget in budgets)
            
            self.financial_summary = {
                'total_expenses_6m': total_expenses,
                'total_budget_6m': total_budget,
                'expense_count': len(expenses),
                'active_goals': len(goals)
            }

    def __init__(self, config):
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        )
        self.model = model

    def calculate_sip(self, monthly_investment: float, expected_return: float, years: int) -> dict:
        """Calculate SIP returns."""
        try:
            monthly_rate = expected_return / (12 * 100)  # Convert percentage to monthly decimal
            months = years * 12
            
            # Calculate future value using SIP formula
            # FV = P * (((1 + r)^n - 1) / r) * (1 + r)
            # where P is monthly investment, r is monthly rate, n is number of months
            amount = monthly_investment * ((pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate)
            
            total_investment = monthly_investment * months
            total_returns = amount - total_investment
            
            return {
                'total_investment': round(total_investment, 2),
                'total_returns': round(total_returns, 2),
                'final_amount': round(amount, 2)
            }
        except Exception as e:
            print(f"Error calculating SIP: {str(e)}")
            raise
    @lru_cache(maxsize=1)
    def get_financial_advice(self, topic: str,user_id:int) -> dict:
        self.call(user_id)
        """Get AI-generated financial advice."""
        prompt = f"""Provide concise, practical advice about {topic} in personal finance. Focus on actionable steps. Use markdown formatting for better readability.
        
        User's Financial Summary (Last 6 months):
        - Total Expenses: ₹{self.financial_summary['total_expenses_6m']}
        - Total Budgeted: ₹{self.financial_summary['total_budget_6m']}
        - Number of Expenses: {self.financial_summary['expense_count']}
        - Active Goals: {self.financial_summary['active_goals']}
        
        Recent Expenses: {self.expense_data if self.expense_data else 'No recent expenses'}
        
        Budget Information: {self.budget_data if self.budget_data else 'No budget set'}
        
        Financial Goals: {self.goal_data if self.goal_data else 'No goals set'}
        
        
        """
        response = self.model.generate_content(prompt)
        text = response.text
        html = markdown.markdown(text)
        return {
            'text': text,
            'html': html
        }
    def Chat(self, topic: str, user_id: int) -> str:
        """Get AI-generated Chat with user context."""
        
        self.call(user_id)
        # Create context-aware prompt
        prompt = f"""
        You are a financial assistant bot. Use the following user data to provide personalized advice.
        
        User's Financial Summary (Last 6 months):
        - Total Expenses: ₹{self.financial_summary['total_expenses_6m']}
        - Total Budgeted: ₹{self.financial_summary['total_budget_6m']}
        - Number of Expenses: {self.financial_summary['expense_count']}
        - Active Goals: {self.financial_summary['active_goals']}
        
        Recent Expenses: {self.expense_data if self.expense_data else 'No recent expenses'}
        
        Budget Information: {self.budget_data if self.budget_data else 'No budget set'}
        
        Financial Goals: {self.goal_data if self.goal_data else 'No goals set'}
        
        User Query: {topic}
        
        """
        
        response = self.model.generate_content(prompt)
        print(response.text)
        text = response.text
        html = markdown.markdown(text)
        return {
            'text': text,
            'html': html
        }

    def analyze_expenses(self, expenses: list) -> dict:
        """Analyze expense patterns and provide insights."""
        if not expenses:
            return {
                'total_spent': 0,
                'breakdown': {},
                'monthly_trend': []
            }
            
        total_spent = sum(expense.amount for expense in expenses)
        categories = {}
        print(f"Analyzing {len(expenses)} expenses, total: {total_spent}")
        
        for expense in expenses:
            categories[expense.category] = categories.get(expense.category, 0) + expense.amount
            
        # Calculate percentage per category
        insights = {
            'total_spent': total_spent,
            'breakdown': {
                category: {
                    'amount': float(amount),
                    'percentage': float((amount / total_spent * 100) if total_spent > 0 else 0)
                }
                for category, amount in categories.items()
            }
        }
        
        return insights

    def calculate_goal_savings(self, target_amount: float, target_date: datetime, current_amount: float = 0) -> dict:
        """Calculate monthly savings needed to reach a financial goal."""
        months_remaining = (datetime(target_date) - datetime.now()).days / 30
        amount_needed = target_amount - current_amount
        
        if months_remaining <= 0:
            return {'error': 'Target date must be in the future'}
            
        monthly_saving = amount_needed / months_remaining
        
        return {
            'monthly_saving_needed': round(monthly_saving, 2),
            'total_amount_needed': round(amount_needed, 2),
            'months_remaining': round(months_remaining, 1)
        }
