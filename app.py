#imports
from sqlite3 import IntegrityError
from flask import Flask, jsonify, make_response, render_template, request, send_from_directory
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
@app.route('/', methods=["GET"])
def homepageload():
    return render_template("index.html")

@app.route('/bookpage', methods=["GET"])
def bookspageload():
    return render_template("books.html")

@app.route('/customerpage', methods=["GET"])
def customerspageload():
    return render_template("customers.html")

@app.route('/loanpage', methods=["GET"])
def loanspageload():
    return render_template("loans.html")

@app.route('/static/js/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


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

#CRUDS for everything

# CRUD for Books

@app.route('/books', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

@app.route('/books/', methods=['GET', 'POST'])
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


#CRUD for Loans
@app.route('/loans', methods=['GET', 'POST'])
@app.route('/loans/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def loans(id=None):
    if request.method == 'GET':
        if id is not None:
            loan = Loan.query.get(id)
            if loan:
                max_return_date = calculate_max_return_date(loan.LoanDate, loan.LoanType)
                return_date = loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None
                return jsonify({'LoanID': loan.LoanID, 'CustID': loan.CustID, 'BookID': loan.BookID, 'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'), 'ReturnDate': return_date, 'MaxReturnDate': max_return_date, 'LoanType': loan.LoanType})
            else:
                return jsonify({'error': 'Loan not found'}), 404
        else:
            loans = Loan.query.all()
            loan_list = []
            for loan in loans:
                max_return_date = calculate_max_return_date(loan.LoanDate, loan.LoanType)
                return_date = loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None
                loan_data = {'LoanID': loan.LoanID, 'CustID': loan.CustID, 'BookID': loan.BookID, 'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'), 'ReturnDate': return_date, 'MaxReturnDate': max_return_date, 'LoanType': loan.LoanType}
                loan_list.append(loan_data)
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
            max_return_date = calculate_max_return_date(loan_date, loan_type)

            new_loan = Loan(CustID=data['CustID'], BookID=data['BookID'], LoanType=loan_type, LoanDate=loan_date, MaxReturnDate=max_return_date)
            try:
                db.session.add(new_loan)
                db.session.commit()
                return_date = new_loan.MaxReturnDate.strftime('%Y-%m-%d %H:%M:%S') if new_loan.MaxReturnDate else None
                return jsonify({'done': 'success', 'Loan': 'created', 'MaxReturnDate': return_date}), 201
            except IntegrityError:
                db.session.rollback()
                return jsonify({'error': 'Loan creation failed'}), 400
        else:
            return jsonify({'error': 'Book is not available for loan'}), 400

    if request.method == 'PUT':
        data = request.json
        loan = Loan.query.get(id)
        if loan:
            new_loan_type = data.get('LoanType')

            # Recalculate MaxReturnDate if LoanType is modified
            if new_loan_type != loan.LoanType:
                loan.LoanType = new_loan_type
                max_return_date = calculate_max_return_date(loan.LoanDate, new_loan_type)
                loan.MaxReturnDate = max_return_date

            db.session.commit()
            return jsonify({'done': 'success', 'Loan': 'updated'})
        else:
            return jsonify({'error': 'Loan not found'}), 404


    if request.method == 'DELETE':
        loan = Loan.query.get(id)
        if loan:
            db.session.delete(loan)
            db.session.commit()
            return jsonify({'done': 'success', 'Loan': 'deleted'})
        else:
            return jsonify({'error': 'Loan not found'}), 404

def calculate_max_return_date(loan_date, loan_type):
    if not isinstance(loan_date, datetime):
        raise ValueError("Invalid loan_date. Please provide a valid datetime object.")
    
    if not isinstance(loan_type, int) or loan_type not in [1, 2, 3]:
        raise ValueError("Invalid loan_type. Please provide 1, 2, or 3.")
    
    if loan_type == 1:
        return_date = loan_date + timedelta(days=10)
    elif loan_type == 2:
        return_date = loan_date + timedelta(days=5)
    elif loan_type == 3:
        return_date = loan_date + timedelta(days=2)
    else:
        raise ValueError("Invalid loan_type. Please provide 1, 2, or 3.")

    return return_date


@app.route('/return_loan/<int:id>', methods=['PUT'])
def return_loan(id):
    if request.method == 'PUT':
        loan = Loan.query.get(id)

        if loan:
            if loan.ReturnDate is not None:
                return jsonify({'error': 'Loan has already been returned'}), 400

            # Set the return date and update the stock only when the loan is returned
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


#some Extra Shit for loans

@app.route('/loans/expired', methods=['GET'])
def expired_loans():
    # Get expired loans
    current_date = datetime.utcnow()
    expired_loans = Loan.query.filter(Loan.MaxReturnDate < current_date).all()

    # Process the expired loans and return them as needed
    expired_loan_data = []

    for loan in expired_loans:
        max_return_date = calculate_max_return_date(loan.LoanDate, loan.LoanType)
        return_date = loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None
        loan_data = {
            'LoanID': loan.LoanID,
            'CustID': loan.CustID,
            'BookID': loan.BookID,
            'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'),
            'ReturnDate': return_date,
            'MaxReturnDate': max_return_date,
            'LoanType': loan.LoanType,
        }
        expired_loan_data.append(loan_data)

    return jsonify(expired_loan_data)

@app.route('/loans/not-returned', methods=['GET'])
def not_returned_loans():
    # Get loans that haven't been returned
    not_returned_loans = Loan.query.filter(Loan.ReturnDate.is_(None)).all()

    # Process the not returned loans and return them as needed
    not_returned_loan_data = []

    for loan in not_returned_loans:
        max_return_date = calculate_max_return_date(loan.LoanDate, loan.LoanType)
        return_date = loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None
        loan_data = {
            'LoanID': loan.LoanID,
            'CustID': loan.CustID,
            'BookID': loan.BookID,
            'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'),
            'ReturnDate': return_date,
            'MaxReturnDate': max_return_date,
            'LoanType': loan.LoanType,
        }
        not_returned_loan_data.append(loan_data)

    return jsonify(not_returned_loan_data)

@app.route('/loans/returned', methods=['GET'])
def returned_loans():
    # Get loans that have been returned
    returned_loans = Loan.query.filter(Loan.ReturnDate.isnot(None)).all()

    # Process the returned loans and return them as needed
    returned_loan_data = []

    for loan in returned_loans:
        max_return_date = calculate_max_return_date(loan.LoanDate, loan.LoanType)
        return_date = loan.ReturnDate.strftime('%Y-%m-%d %H:%M:%S') if loan.ReturnDate else None
        loan_data = {
            'LoanID': loan.LoanID,
            'CustID': loan.CustID,
            'BookID': loan.BookID,
            'LoanDate': loan.LoanDate.strftime('%Y-%m-%d %H:%M:%S'),
            'ReturnDate': return_date,
            'MaxReturnDate': max_return_date,
            'LoanType': loan.LoanType,
        }
        returned_loan_data.append(loan_data)

    return jsonify(returned_loan_data)

#something something
@app.route('/books/<int:book_id>/loanstatus', methods=['GET'])
def check_book_loan_status(book_id):
    book = Book.query.get(book_id)
    
    if book:
        loan = Loan.query.filter_by(BookID=book_id, ReturnDate=None).first()
        return jsonify({'loaned': loan is not None})
    else:
        return jsonify({'error': 'Book not found'}), 404

@app.route('/customers/<int:CustID>/loanstatus', methods=['GET'])
def check_customer_loan_status(CustID):
    customer = Customer.query.get(CustID)
    
    if customer:
        loan = Loan.query.filter_by(CustID=CustID, ReturnDate=None).first()
        return jsonify({'loaned': loan is not None})
    else:
        return jsonify({'error': 'Customer not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)