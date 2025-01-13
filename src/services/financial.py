import google.generativeai as genai
from datetime import datetime
import os

class FinancialService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    def calculate_sip(self, monthly_investment: float, expected_return: float, years: int) -> dict:
        """Calculate SIP returns."""
        monthly_rate = expected_return / (12 * 100)
        months = years * 12
        
        # Calculate future value using SIP formula
        amount = monthly_investment * ((pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate)
        
        total_investment = monthly_investment * months
        total_returns = amount - total_investment
        
        return {
            'total_investment': round(total_investment, 2),
            'total_returns': round(total_returns, 2),
            'final_amount': round(amount, 2)
        }

    async def get_financial_advice(self, topic: str) -> str:
        """Get AI-generated financial advice."""
        prompt = f"Provide concise, practical advice about {topic} in personal finance. Focus on actionable steps."
        response = await self.model.generate_content(prompt)
        return response.text

    def analyze_expenses(self, expenses: list) -> dict:
        """Analyze expense patterns and provide insights."""
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
                    'amount': amount,
                    'percentage': (amount / total_spent * 100) if total_spent > 0 else 0
                }
                for category, amount in categories.items()
            }
        }
        
        return insights

    def calculate_goal_savings(self, target_amount: float, target_date: datetime, current_amount: float = 0) -> dict:
        """Calculate monthly savings needed to reach a financial goal."""
        months_remaining = (target_date - datetime.now()).days / 30
        amount_needed = target_amount - current_amount
        
        if months_remaining <= 0:
            return {'error': 'Target date must be in the future'}
            
        monthly_saving = amount_needed / months_remaining
        
        return {
            'monthly_saving_needed': round(monthly_saving, 2),
            'total_amount_needed': round(amount_needed, 2),
            'months_remaining': round(months_remaining, 1)
        }
