function increaseImageSize()
{
    document.getElementById("cover").style.width='180px';
}
function resetImageSize()
{
    document.getElementById("cover").style.width='120px';
}

function showDiv()
{
    var btn = document.getElementById("myButton");
    if (btn.value == "Расширенный поиск")
    {
        btn.value = "Свернуть";
        btn.innerHTML = "Свернуть";
    }
    else
    {
        btn.value = "Расширенный поиск";
        btn.innerHTML = "Расширенный поиск";
    }
    var x = document.getElementById("myDiv");
    if (x.style.display == "none")
    {
        x.style.display = "block";
    }
    else
    {
        x.style.display = "none";
    }
}

