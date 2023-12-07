// books.js
const MYSERVER = 'http://127.0.0.1:5000'

// Function to fetch and display books
function getBooks() {
    fetch(MYSERVER+'/books') // Make a GET request to the /books endpoint
        .then(response => response.json()) // Parse the response as JSON
        .then(books => {
            // Assuming you have a table with the id 'books-table'
            const table = document.getElementById('books-table');
            table.innerHTML = ''; // Clear the table

            // Iterate over the books and add rows to the table
            books.forEach(book => {
                const row = table.insertRow();
                row.insertCell(0).textContent = book.BookID;
                row.insertCell(1).textContent = book.bookname;
                row.insertCell(2).textContent = book.bookauthor;
                row.insertCell(3).textContent = book.year_published;
                row.insertCell(4).textContent = book.stock;

                // Add buttons for Delete and Modify
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.addEventListener('click', () => deleteBook(book.BookID));
                row.insertCell(5).appendChild(deleteButton);

                const modifyButton = document.createElement('button');
                modifyButton.textContent = 'Modify';
                modifyButton.addEventListener('click', () => modifyBook(book.BookID));
                row.insertCell(6).appendChild(modifyButton);
            });
        })
        .catch(error => console.error(error));
}

// Function to delete a book
function deleteBook(bookID) {
    fetch(`${MYSERVER}/books/${bookID}`, {
        method: 'DELETE',
    })
        .then(() => {
            // Reload books after deletion
            getBooks();
        })
        .catch(error => console.error(error));
}

// Function to modify a book
function modifyBook(bookID) {
    // Implement code for modifying a book (e.g., showing a form to edit book details)
}

// Call getBooks() when the page loads
window.addEventListener('load', getBooks);


// Function to add a new book
function addBook() {
    const bookname = document.getElementById('bookname').value;
    const bookauthor = document.getElementById('bookauthor').value;
    const year_published = parseInt(document.getElementById('year_published').value);
    const stock = parseInt(document.getElementById('stock').value);

    const newBook = {
        bookname,
        bookauthor,
        year_published,
        stock,
    };

    fetch(MYSERVER+'/books', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(newBook),
    })
        .then(response => response.json())
        .then(data => {
            if (data.done === 'success') {
                // Clear the form and reload the books
                document.getElementById('book-form').reset();
                getBooks();
            } else {
                console.error(data.error);
            }
        })
        .catch(error => console.error(error));
}

// Function to modify a book
function modifyBook(bookID) {
    // Implement code for modifying a book (e.g., showing a form to edit book details)
    // You'll need to populate the form with the book details and handle the form submission
    // using a similar approach as the addBook function.
}

// Add event listeners to buttons
document.getElementById('add-book-button').addEventListener('click', addBook);



// searchbar
function searchBooks() {
  let input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("searchInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("booksTable");
  tr = table.getElementsByTagName("tr");

  for (i = 1; i < tr.length; i++) { // Start from 1 to skip the table header row
    td = tr[i].getElementsByTagName("td")[0]; // Assuming the title is in the first column
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

