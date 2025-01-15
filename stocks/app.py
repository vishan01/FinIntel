from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import yfinance as yf
from utils import fetch_stock_info

app = Flask(__name__)
stock_watchlist = []
app.secret_key = '918237981y48t9580y4t8y5t'
@app.route('/')
def dashboard():
    stocks_data = []
    for ticker in stock_watchlist:
        stocks_data.append(fetch_stock_info(ticker))
    print(stocks_data)
    return render_template('dashboard.html', stocks=stocks_data)

@app.route('/stock/<ticker>', methods=['GET'])
def get_stock_details(ticker):
    return jsonify(fetch_stock_info(ticker))

@app.route('/watchlist', methods=['POST'])
def watchlist():
    ticker = request.form.get('ticker')
    print(ticker)
    print(stock_watchlist)
    if ticker and ticker not in stock_watchlist:
        stock_watchlist.append(ticker)
        flash(f'{ticker} added to watchlist', 'success')
    else:
        flash(f'{ticker} already in watchlist', 'info')
        
    return redirect(url_for('dashboard'))

@app.route('/watchlist/<ticker>', methods=['POST'])
def remove_from_watchlist(ticker):
    if ticker in stock_watchlist:
        stock_watchlist.remove(ticker)
        flash(f'{ticker} removed from watchlist', 'success')
        return redirect(url_for('dashboard'))
    return jsonify({'message': 'Stock not in watchlist'}), 404

if __name__ == '__main__':
    app.run(debug=True)