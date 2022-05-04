$(document).ready(function(){
    $(".myLink2").click(function(){
    $(".myDiv").slideToggle();
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


