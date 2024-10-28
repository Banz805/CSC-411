# server/app.py
from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import json
import mysql.connector
from database import connect_to_db, save_book_to_db, get_books_from_db, initialize_books
import requests

app = Flask(__name__)

# Initialize the books when the server starts
initialize_books()

# Endpoint to add a new book (supports XML/JSON)
@app.route('/add-book', methods=['POST'])
def add_book():
    data = request.data.decode('utf-8')

    if request.headers['Content-Type'] == 'application/xml':
        root = ET.fromstring(data)
        title = root.find('title').text
        author = root.find('author').text
        price = root.find('price').text
        save_book_to_db(title, author, price)
        return f"Book '{title}' by {author} added."

    elif request.headers['Content-Type'] == 'application/json':
        json_data = json.loads(data)
        title = json_data['title']
        author = json_data['author']
        price = json_data['price']
        save_book_to_db(title, author, price)
        return f"Book '{title}' by {author} added."

    return "Unsupported data format."

# Endpoint to get the list of books
@app.route('/books', methods=['GET'])
def get_books():
    books = get_books_from_db()
    return jsonify(books)

# Function to convert prices using a currency conversion API
def convert_currency(amount, from_currency, to_currency):
    api_key = 'your_api_key'
    url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
    response = requests.get(url)
    rates = response.json()['rates']
    converted_amount = amount * rates[to_currency]
    return converted_amount

# Endpoint to convert book price from USD to EUR (or other currencies)
@app.route('/convert-price', methods=['GET'])
def convert_price():
    try:
        price = float(request.args.get('price'))
        converted_price = convert_currency(price, 'USD', 'EUR')
        return jsonify({'converted_price': converted_price})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
