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

$(document).ready(function() {
    $("#report_type").change(function() {
//        document.write(this.value);
        if (this.value == 'type_1') {
            $('#source_database').show();
        } else if (this.value == 'type_2') {
            $('#source_database').hide();
        } else if (this.value == 'type_3') {
            $('#source_database').hide();
        }
    });
});


