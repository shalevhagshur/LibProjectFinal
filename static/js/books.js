



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

