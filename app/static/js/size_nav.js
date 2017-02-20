$('#sizes li').on('click', function(){

	var $seven = $('table:nth-of-type(1)');
	var $ten = $('table:nth-of-type(2)');
	var $twelve = $('table:nth-of-type(3)');
	var $addrecord = $('#add-record');

	$.each( $('#sizes li').not($(this)), function() {
	  $(this).removeClass('active');

	});
 
	if  ( $(this).hasClass('active') != true) {
		$(this).toggleClass('active');	
	}

	

	if ( $(this).text() == "7" ) {
		$addrecord.hide();
		$seven.show();
		$ten.hide();
		$twelve.hide();

	} else if ( $(this).text() == "10" ) {
		$addrecord.hide();
		$seven.hide();
		$ten.show();
		$twelve.hide();

	} else if ( $(this).text() == "12" ) {
		$addrecord.hide();
		$seven.hide();
		$ten.hide();
		$twelve.show();
		
	} else if ( $(this).text() == "All" ) {
		$addrecord.hide();
		$seven.show();
		$ten.show();
		$twelve.show();
	} else if ( $(this).text() == "+" ) {
		$seven.hide();
		$ten.hide();
		$twelve.hide();
		$addrecord.show();
	}

})