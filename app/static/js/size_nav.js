var $seven = $('#seven_inches');
var $ten = $('#ten_inches');
var $twelve = $('#twelve_inches');
var $mail = $('#mail');
var $searchDiv = $($("#search").parents()[0]);


$('#sizes li').on('click', function(){

	// Remove Active Class
	$.each( $('#sizes li').not($(this)), function() {
	  $(this).removeClass('active');

	});


	// Clear the search box && show all rows
	$("#search").val("");
	$("#results").hide();

	allRows = document.querySelectorAll("tr");

	for (var i = allRows.length - 1; i >= 0; i--) {
		allRows[i].style.display = "";
	}
 
 	// Active Class Navigator
	if  ( $(this).hasClass('active') != true) {
		$(this).toggleClass('active');	
	}

	switch ( $(this).text() ) {
		case "7 Inches":
			$ten.hide();
			$twelve.hide();
			$mail.hide();
			$seven.show();
			$searchDiv.show();
			break;

		case "10 Inches":
			$seven.hide();
			$twelve.hide();
			$mail.hide();
			$ten.show();
			$searchDiv.show();
			break;

		case "12 Inches":
			$seven.hide();
			$ten.hide();
			$mail.hide();
			$twelve.show();
			$searchDiv.show();
			break;

		case "Incoming":
			$seven.hide();
	  		$ten.hide();
	  		$twelve.hide();
	 		$mail.show();
	 		$searchDiv.hide();
			break;	

		default:
			$mail.hide();
			$seven.show();
			$ten.show();
			$twelve.show();
			$searchDiv.show();
			break;
	}
})