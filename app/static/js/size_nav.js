var $seven = $('#seven_inches');
var $ten = $('#ten_inches');
var $twelve = $('#twelve_inches');
var $addrecord = $('#add-record');
var $mail = $('#mail');

// Keep the add field open if there is a validation error
if ( $('.error').length > 0 ) {
	$seven.hide();
	$ten.hide();
	$twelve.hide();
	$mail.hide();
	$addrecord.show();

	// remove active from all
	$('#sizes li:first-child').toggleClass('active');

	// add active to +
	$('#plus').toggleClass('active');
}

$('#sizes li').on('click', function(){

	// Remove Active Class
	$.each( $('#sizes li').not($(this)), function() {
	  $(this).removeClass('active');

	});
 
 	// Active Class Navigator
	if  ( $(this).hasClass('active') != true) {
		$(this).toggleClass('active');	
	}

	// Button Behavior 
	if ( $(this).text() == "7" ) {
		$addrecord.hide();
		$ten.hide();
		$twelve.hide();
		$mail.hide();
		$seven.show();

	} else if ( $(this).text() == "10" ) {
		$addrecord.hide();
		$seven.hide();
		$twelve.hide();
		$mail.hide();
		$ten.show();


	} else if ( $(this).text() == "12" ) {
		$addrecord.hide();
		$seven.hide();
		$ten.hide();
		$mail.hide();
		$twelve.show();

		
	} else if ( $(this).text() == "All" ) {
		$addrecord.hide();
		$mail.hide();
		$seven.show();
		$ten.show();
		$twelve.show();

	} else if ( $(this).text() == "+" ) {
		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$mail.hide();
		$addrecord.show();


	} else if ( $(this).text() == "Mail" ) {
		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$addrecord.hide();
		$mail.show();
	}

})