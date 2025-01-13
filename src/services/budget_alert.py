from datetime import datetime
from src.models import Budget, Expense

class BudgetAlertService:
    @staticmethod
    def check_budget_status(user_id):
        """Check budget status and generate alerts."""
        current_date = datetime.now()
        alerts = []
        
        # Get all active budgets for the user
        budgets = Budget.query.filter_by(user_id=user_id).all()
        
        for budget in budgets:
            # Get expenses for the current month in this category
            expenses = Expense.query.filter_by(
                user_id=user_id,
                category=budget.category
            ).filter(
                Expense.date.between(
                    datetime(current_date.year, current_date.month, 1),
                    current_date
                )
            ).all()
            
            total_spent = sum(expense.amount for expense in expenses)
            budget_limit = budget.amount
            spent_percentage = (total_spent / budget_limit) * 100 if budget_limit > 0 else 0
            
            # Generate alerts based on spending thresholds
            if spent_percentage >= 90:
                alerts.append({
                    'category': budget.category,
                    'severity': 'danger',
                    'message': f'Critical: You have spent {spent_percentage:.1f}% of your {budget.category} budget'
                })
            elif spent_percentage >= 75:
                alerts.append({
                    'category': budget.category,
                    'severity': 'warning',
                    'message': f'Warning: You have spent {spent_percentage:.1f}% of your {budget.category} budget'
                })
            
            # Daily average spending alert
            days_in_month = current_date.day
            daily_average = total_spent / days_in_month if days_in_month > 0 else 0
            budget_daily_limit = budget_limit / 30
            
            if daily_average > budget_daily_limit * 1.2:  # 20% over daily average
                alerts.append({
                    'category': budget.category,
                    'severity': 'info',
                    'message': f'Your daily spending in {budget.category} is higher than recommended'
                })
        
        return alerts
