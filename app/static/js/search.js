
function searchFunction() {

// Declare variables 
var input, filter, tables, td, i;
input = document.getElementById("search");
filter = input.value.toUpperCase();
var tr = document.querySelectorAll("tr")
var resultsElement = document.getElementById("results");
var visible = 0;


	// Hide/show results 
  for (i = 0; i < tr.length; i++) {
    artist_td = tr[i].getElementsByTagName("td")[0];
    title_td = tr[i].getElementsByTagName("td")[1];
    color_td = tr[i].getElementsByTagName("td")[3];
    year_td = tr[i].getElementsByTagName("td")[4];

    if (artist_td || title_td) {
      if (artist_td.innerHTML.toUpperCase().indexOf(filter) > -1 || 
        title_td.innerHTML.toUpperCase().indexOf(filter) > -1 ||
        color_td.innerHTML.toUpperCase().indexOf(filter) > -1 ||
        year_td.innerHTML.toString().indexOf(filter) > -1) {
        
      	var parentTable = tr[i].closest(".panel-default")
      	var inMailTable = tr[i].closest("#mail"); //null

        if (parentTable.style.display != "none" && inMailTable == null) {
        	tr[i].style.display = "";
        	resultsElement.style.display = "";
        	visible += 1
        }
        
      } else {
        tr[i].style.display = "none";
      }
    } 
  }

  var noun = visible != 1 ? "Records" : "Record"
  resultsElement.innerHTML = visible.toString() + " " + noun;

  if (input.value.length == 0) {
  	resultsElement.style.display = "none";
  }
}

$("#searchClear").on("click", function () {
	$("#search").val("");
	$("#results").hide();

	allRows = document.querySelectorAll("tr");

	for (var i = allRows.length - 1; i >= 0; i--) {
		allRows[i].style.display = "";
	}
})