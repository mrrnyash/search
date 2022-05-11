$(document).ready(function(){
    $(".myLink2").click(function(){
    $(".myDiv").fadeToggle();
    $(this).text($(this).text() == 'Расширенный поиск' ? 'Свернуть' : 'Расширенный поиск');
    });
});

$(document).ready(function(){
    $(".myDropdown").click(function(){
    $(".myList").slideToggle();
    });
});

$(document).ready(function(){
    $(".myLink").click(function(){
        $(this).parent().find(".myParagraph").slideToggle();
        $(this).text($(this).text() == 'Подробнее' ? 'Свернуть' : 'Подробнее');
    });
});

$(document).ready(function(){
	// bind and scroll header div
	$(window).bind('resize', function(e){
		$(".affix").css('width',$(".container-fluid" ).width());
	});
	$(window).on("scroll", function() {
		$(".affix").css('width',$(".container-fluid" ).width());
	});
});


