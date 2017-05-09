var $seven = $('#seven_inches');
var $ten = $('#ten_inches');
var $twelve = $('#twelve_inches');
var $mail = $('#mail');

$('#sizes li').on('click', function(){

	// Remove Active Class
	$.each( $('#sizes li').not($(this)), function() {
	  $(this).removeClass('active');

	});
 
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
			break;

		case "10 Inches":
			$seven.hide();
			$twelve.hide();
			$mail.hide();
			$ten.show();
			break;

		case "12 Inches":
			$seven.hide();
			$ten.hide();
			$mail.hide();
			$twelve.show();
			break;

		case "Incoming":
			$seven.hide();
	  		$ten.hide();
	  		$twelve.hide();
	 		$mail.show();
			break;	

		default:
			$mail.hide();
			$seven.show();
			$ten.show();
			$twelve.show();
			break;
	}
})