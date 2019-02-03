$(document).ready(function(){
	var cookies = document.cookie.split(";");
	for (var i = 0; i < cookies.length; i++) {
		var args = cookies[i].replace(/\s/g,"").split("=");
		if (args[0] == "user") document.body.style.background = args[1];
	}
    $("#result").html("");
    $("#q").keyup(function(){
        var host = window.location.hostname;
        var port = window.location.port;
        var query = $("#q").val();
        var url = "http://" + host + ":" + port +"/api?q=" + query;
        console.log(url);
        $.get(url, function(response){
            var output = "<div id=\"searchtable\"><table align=\"center\">";
            $.each(response, function (index, value) {
                console.log(value);
                //splitt the string by " ";
                var string = value;
                string = string.split("^");
                output += "<tr><td> <a target=\"_blank\" href=\"" + string[0] +"\"> "+ string[1]
				+"</a></td><td>" + string[2]+"</td><td>"+ string[3]+" "+ "</td></tr>";
            });
			output += "</table></div>";
            $("#result").html(output);
        })
    })
})
function changeBackground(str) {
	document.cookie = "user=" + str;
	document.body.style.background = str;
}
