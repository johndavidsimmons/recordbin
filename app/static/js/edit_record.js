var editPencils = $("span[data-target='.edit-modal']");

var parentRow;
var record_dimensions;
var tableId;
var recordId;
var trashcan = $('h4.modal-title > a');


// Autofill the form
editPencils.on("click", function(){

	// Clear upload thumbnail
	$("#edit_gallery").css("background-image", "none");

	// Table Dimensions
	tableId = $(this).closest("div.panel").attr("id");
	parentRow = $(this).closest("tr");
	record_dimensions = parentRow.children();
	var artist = $(record_dimensions[0]).text();
	var title = $(record_dimensions[1]).text();
	var color = $(record_dimensions[3]).text();
	var year = $(record_dimensions[4]).text();
	var notes = $(record_dimensions[5]).text();
	var timestamp = $(record_dimensions[6]).text();
	var imageURL = $(record_dimensions[7]).attr("value");
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
		// sizeInput.val("1");
		document.querySelector('select[name="edit_size"] option[value="1"]').setAttribute('selected', "selected");
	} else if (tableId.indexOf("ten") > -1) {
		// sizeInput.val("2");
		document.querySelector('select[name="edit_size"] option[value="2"]').setAttribute('selected', "selected");
	} else if (tableId.indexOf("twelve") > -1) {
		// sizeInput.val("3");
		document.querySelector('select[name="edit_size"] option[value="3"]').setAttribute('selected', "selected");
	}

	// Load the image
	if (imageURL) {
		var tokens = imageURL.split('/');
		tokens.splice(6, 0, 't_media_lib_thumb');
		var thumbURL = tokens.join('/');

		var img = $("<img />").attr('src', thumbURL)
		.on('load', function() {
		    if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
		        console.log('broken image!');
		    } else {
		        $("#edit_gallery").css({
		        	'background-image': 'url(' + thumbURL + ')',
		        	'background-size': 'cover',
		        	'background-repeat': 'no-repeat',
		        	'background-position' : 'center center'  
		        });
		    }
		});
	} 
});