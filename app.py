#imports
from sqlite3 import IntegrityError
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta


#flask app
# Create a Flask web application
app = Flask(__name__)

CORS(app)

# Configure your database connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'  # You can change this to your preferred database

db = SQLAlchemy(app)

migrate = Migrate(app, db)


#app routes (Crud routes are in cruds)
@app.route('/')
def hello_world():
    return 'Hello, Flask!'


#table for books
class Book(db.Model):
    __tablename__ = 'books'

    BookID = db.Column(db.Integer, primary_key=True)
    bookname = db.Column(db.String(25), nullable=False)
    bookauthor = db.Column(db.String(25), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=5, nullable=False)

# Function to check year_published range
def check_year_published_range(target, value, oldvalue, initiator):
    if not (0 <= value <= 9999):
        raise ValueError("Year published must be between 0 and 9999")
db.event.listen(Book.year_published, 'set', check_year_published_range)

#table for customers

class Customer(db.Model):
    __tablename__ = 'customers'

    CustID = db.Column(db.Integer, primary_key=True)
    CustName = db.Column(db.String(25), nullable=False)
    City = db.Column(db.String(25), nullable=False)
    Age = db.Column(db.Integer, nullable=False)

def check_age_range(target, value, oldvalue, initiator):
    if not (0 <= value <= 999):
        raise ValueError("Age must be between 0 and 999")
db.event.listen(Customer.Age, 'set', check_age_range)

#table for loans 
class Loan(db.Model):
    __tablename__ = 'loans'

    LoanID = db.Column(db.Integer, primary_key=True)
    CustID = db.Column(db.Integer, db.ForeignKey('customers.CustID'), nullable=False)
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID'), nullable=False)
    LoanDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ReturnDate = db.Column(db.DateTime, nullable=True)
    MaxReturnDate = db.Column(db.DateTime, nullable=True)
    LoanType = db.Column(db.Integer, nullable=False)

    # Establish foreign key relationships
    customer = db.relationship('Customer', foreign_keys=[CustID])
    book = db.relationship('Book', foreign_keys=[BookID])


# CRUD for Books
@app.route('/books', methods=['GET', 'POST'])
@app.route('/books/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def books(id=None):
    if request.method == 'GET':
        if id is not None:
            book = Book.query.get(id)
            if book:
                return jsonify({'BookID': book.BookID, 'bookname': book.bookname, 'bookauthor': book.bookauthor, 'year_published': book.year_published, 'stock': book.stock})
            else:
                return jsonify({'error': 'Book not found'}), 404
        else:
            books = Book.query.all()
            book_list = [{'BookID': book.BookID, 'bookname': book.bookname, 'bookauthor': book.bookauthor, 'year_published': book.year_published, 'stock': book.stock} for book in books]
            return jsonify(book_list)

    if request.method == 'POST':
        data = request.json
        new_book = Book(bookname=data['bookname'], bookauthor=data['bookauthor'], year_published=data['year_published'], stock=data.get('stock', 5))
        try:
            db.session.add(new_book)
            db.session.commit()
            return jsonify({'done': 'success', 'Book': 'created'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Book creation failed'}), 400

    if request.method == 'DELETE':
        book = Book.query.get(id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return jsonify({'done': 'success', 'Book': 'deleted'})
        else:
            return jsonify({'error': 'Book not found'}), 404

    if request.method == 'PUT':
        data = request.json
        book = Book.query.get(id)
        if book:
            book.bookname = data['bookname']
            book.bookauthor = data['bookauthor']
            book.year_published = data['year_published']
            book.stock = data.get('stock', 5)
            db.session.commit()
            return jsonify({'done': 'success', 'Book': 'updated'})
        else:
            return jsonify({'error': 'Book not found'}), 404



# CRUD for Customers
@app.route('/customers', methods=['GET', 'POST'])
@app.route('/customers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def customers(id=None):
    if request.method == 'GET':
        if id is not None:
            customer = Customer.query.get(id)
            if customer:
                return jsonify({'CustID': customer.CustID, 'CustName': customer.CustName, 'City': customer.City, 'Age': customer.Age})
            else:
                return jsonify({'error': 'Customer not found'}), 404
        else:
            customers = Customer.query.all()
            customer_list = [{'CustID': customer.CustID, 'CustName': customer.CustName, 'City': customer.City, 'Age': customer.Age} for customer in customers]
            return jsonify(customer_list)

    if request.method == 'POST':
        data = request.json
        new_customer = Customer(CustName=data['CustName'], City=data['City'], Age=data['Age'])
        try:
            db.session.add(new_customer)
            db.session.commit()
            return jsonify({'done': 'success', 'Customer': 'created'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Customer creation failed'}), 400

    if request.method == 'DELETE':
        customer = Customer.query.get(id)
        if customer:
            db.session.delete(customer)
            db.session.commit()
            return jsonify({'done': 'success', 'Customer': 'deleted'})
        else:
            return jsonify({'error': 'Customer not found'}), 404

    if request.method == 'PUT':
        data = request.json
        customer = Customer.query.get(id)
        if customer:
            customer.CustName = data['CustName']
            customer.City = data['City']
            customer.Age = data['Age']
            db.session.commit()
            return jsonify({'done': 'success', 'Customer': 'updated'})
        else:
            return jsonify({'error': 'Customer not found'}), 404


# CRUD for Loans
@app.route('/loans', methods=['GET', 'POST'])
@app.route('/loans/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def loans(id=None):
    if request.method == 'GET':
        if id is not None:
            loan = Loan.query.get(id)
            if loan:
                return jsonify({'LoanID': loan.LoanID, 'CustID': loan.CustID, 'BookID': loan.BookID, 'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'), 'ReturnDate': loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None, 'LoanType': loan.LoanType})
            else:
                return jsonify({'error': 'Loan not found'}), 404
        else:
            loans = Loan.query.all()
            loan_list = [{'LoanID': loan.LoanID, 'CustID': loan.CustID, 'BookID': loan.BookID, 'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'), 'ReturnDate': loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None, 'LoanType': loan.LoanType} for loan in loans]
            return jsonify(loan_list)

    if request.method == 'POST':
        data = request.json
        loan_type = data.get('LoanType')

        # Check if the loan type is valid (1, 2, or 3)
        if loan_type not in [1, 2, 3]:
            return jsonify({'error': 'Invalid loan type'}), 400

        # Check if the book is available (stock > 0)
        book = Book.query.get(data['BookID'])
        if book and book.stock > 0:
            # Decrease the stock of the book by 1
            book.stock -= 1

            loan_date = datetime.utcnow()  # Current UTC time
            if loan_type == 1:
                return_date = loan_date + timedelta(days=10)
            elif loan_type == 2:
                return_date = loan_date + timedelta(days=5)
            elif loan_type == 3:
                return_date = loan_date + timedelta(days=2)
            else:
                return_date = None

            new_loan = Loan(CustID=data['CustID'], BookID=data['BookID'], LoanType=loan_type, LoanDate=loan_date, ReturnDate=return_date)
            try:
                db.session.add(new_loan)
                db.session.commit()
                return jsonify({'done': 'success', 'Loan': 'created'}), 201
            except IntegrityError:
                db.session.rollback()
                return jsonify({'error': 'Loan creation failed'}), 400
        else:
            return jsonify({'error': 'Book is not available for loan'}), 400

    if request.method == 'PUT':
        data = request.json
        loan = Loan.query.get(id)
        if loan:
            loan.CustID = data['CustID']
            loan.BookID = data['BookID']
            loan.LoanType = data['LoanType']
            db.session.commit()
            return jsonify({'done': 'success', 'Loan': 'updated'})
        else:
            return jsonify({'error': 'Loan not found'}), 404


@app.route('/return_loan/<int:id>', methods=['PUT'])
def return_loan(id):
    if request.method == 'PUT':
        loan = Loan.query.get(id)

        if loan:
            if loan.ReturnDate is not None:
                return jsonify({'error': 'Loan has already been returned'}), 400

            # Set the return date to the current UTC time
            return_date = datetime.utcnow()
            loan.ReturnDate = return_date

            # Increment the stock of the associated book by 1
            book = Book.query.get(loan.BookID)
            if book:
                book.stock += 1

            db.session.commit()
            return jsonify({'done': 'success', 'Loan': 'returned'}), 200
        else:
            return jsonify({'error': 'Loan not found'}), 404
        

if __name__ == '__main__':
    app.run(debug=True)