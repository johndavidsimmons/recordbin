var $seven = $('#seven_inches');
var $ten = $('#ten_inches');
var $twelve = $('#twelve_inches');
var $addrecord = $('#add-record');
var $mail = $('#mail');


switch ( sessionStorage.getItem('nav') ) {
	case '7':
		var $seven_li = $('#sizes li:nth-child(2)');
		$.each( $('#sizes li').not($seven_li), function() {
		  $(this).removeClass('active');
		});
		$seven_li.addClass('active');

		$addrecord.hide();
		$ten.hide();
		$twelve.hide();
		$mail.hide();
		$seven.show();

		break;
	case '10':
		var $ten_li = $('#sizes li:nth-child(3)');
		$.each( $('#sizes li').not($ten_li), function() {
		  $(this).removeClass('active');
		});
		$ten_li.addClass('active');

		$addrecord.hide();
		$seven.hide();
		$twelve.hide();
		$mail.hide();
		$ten.show();

		break;
	case '12':
		var $twelve_li = $('#sizes li:nth-child(4)');
		$.each( $('#sizes li').not($twelve_li), function() {
		  $(this).removeClass('active');
		});
		$twelve_li.addClass('active');

		$addrecord.hide();
		$seven.hide();
		$ten.hide();
		$mail.hide();
		$twelve.show();

		break;
	case '+':
		var $add_li = $('#sizes li:nth-child(6)');
		$.each( $('#sizes li').not($add_li), function() {
		  $(this).removeClass('active');
		});
		$add_li.addClass('active');

		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$mail.hide();
		$addrecord.show();

		break;
	case 'Mail':
		var $mail_li = $('#sizes li:nth-child(5)');
		$.each( $('#sizes li').not($mail_li), function() {
		  $(this).removeClass('active');
		});
		$mail_li.addClass('active');

		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$addrecord.hide();
		$mail.show();

		break;
	default:
		// All
		var $all_li = $('#sizes li:nth-child(1)');
		$.each( $('#sizes li').not($all_li), function() {
		  $(this).removeClass('active');
		});
		$all_li.addClass('active');

		$addrecord.hide();
		$mail.hide();
		$seven.show();
		$ten.show();
		$twelve.show();

		break;
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
		sessionStorage.setItem('nav',$(this).text())
		$addrecord.hide();
		$ten.hide();
		$twelve.hide();
		$mail.hide();
		$seven.show();

	} else if ( $(this).text() == "10" ) {
		sessionStorage.setItem('nav',$(this).text())
		$addrecord.hide();
		$seven.hide();
		$twelve.hide();
		$mail.hide();
		$ten.show();


	} else if ( $(this).text() == "12" ) {
		sessionStorage.setItem('nav',$(this).text())
		$addrecord.hide();
		$seven.hide();
		$ten.hide();
		$mail.hide();
		$twelve.show();

		
	} else if ( $(this).text() == "All" ) {
		sessionStorage.setItem('nav',$(this).text())
		$addrecord.hide();
		$mail.hide();
		$seven.show();
		$ten.show();
		$twelve.show();

	} else if ( $(this).text() == "+" ) {
		sessionStorage.setItem('nav',$(this).text())
		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$mail.hide();
		$addrecord.show();


	} else if ( $(this).text() == "Mail" ) {
		sessionStorage.setItem('nav',$(this).text())
		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$addrecord.hide();
		$mail.show();
	}

})