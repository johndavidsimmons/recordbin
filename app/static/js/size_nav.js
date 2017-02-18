$('#sizes li').on('click', function(){

	var $seven = $('table:nth-of-type(1)');
	var $ten = $('table:nth-of-type(2)');
	var $twelve = $('table:nth-of-type(3)');

	$.each( $('#sizes li').not($(this)), function() {
	  $(this).removeClass('active');

	});

	$(this).toggleClass('active');

	if ( $(this).text() == "7" ) {

		$seven.show();
		$ten.hide();
		$twelve.hide();

	} else if ( $(this).text() == "10" ) {

		$seven.hide();
		$ten.show();
		$twelve.hide();

	} else if ( $(this).text() == "12" ) {

		$seven.hide();
		$ten.hide();
		$twelve.show();
		
	} else if ( $(this).text() == "All" ) {

		$seven.show();
		$ten.show();
		$twelve.show();
	}

})