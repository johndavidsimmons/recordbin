var editPencils = $("span[data-target='.edit-modal']");

var parentRow;
var record_dimensions;
var tableId;
var recordId;
var trashcan = $('h4.modal-title > a');


// Autofill the form
editPencils.on("click", function(){

	// Table Dimensions
	tableId = $(this).closest("div.panel").attr("id");
	parentRow = $(this).closest("tr");
	record_dimensions = parentRow.children();
	var artist = $(record_dimensions[0]).text();
	var title = $(record_dimensions[1]).text();
	var color = $(record_dimensions[2]).text();
	var year = $(record_dimensions[3]).text();
	var notes = $(record_dimensions[4]).text();
	var timestamp = $(record_dimensions[5]).text();
	recordId = $(record_dimensions[0]).attr('id');
	trashcan.attr("href", "delete-record/" + recordId)


	// Form inputs
	var hiddenIDInput = $("form[name='edit-record'] input[name='edit_id']");
	var artistInput = $("form[name='edit-record'] input[name='edit_artist']");
	var titleInput = $("form[name='edit-record'] input[name='edit_title']");
	var colorInput = $("form[name='edit-record'] input[name='edit_color']");
	var yearInput = $("form[name='edit-record'] select[name='edit_year']");
	var notesInput = $("form[name='edit-record'] textarea[name='edit_notes']");
	var mailInput = $("form[name='edit-record'] input[name='edit_incoming']");
	var sizeInput = $("form[name='edit-record'] select[name='edit_size']");
	

	artistInput.val(artist);
	titleInput.val(title);
	colorInput.val(color);
	yearInput.val(year);
	notesInput.val(notes);
	hiddenIDInput.val(recordId);

	if (tableId.indexOf("mail") > -1 ) {
		mailInput.prop("checked", true);
	}

	if (tableId.indexOf("seven") > -1) {
		sizeInput.val("1")
	} else if (tableId.indexOf("ten") > -1) {
		sizeInput.val("2")
	} else if (tableId.indexOf("twelve") > -1) {
		sizeInput.val("3")
	}

});