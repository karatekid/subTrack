$(document).ready(function(){
	$("#contact-subs").submit(function(event){
		event.preventDefault();
		//alert($(this).serialize());
		var vals = $(this).serializeArray();
		console.log(vals);
		//populate send-list
		for(var i = 0; i < vals.length; ++i){
			console.log(vals[i].value);
			$("#send-list").append('<li>'+
				vals[i].value+'</li');
		}
		//populate needed-header & needed-footer
		$.get("/api/message-info", function(data) {
			$('#needed-header').text(data['head']);
			$('#needed-footer').text(data['foot']);
		});
		$("#myModal").modal();
	});
	$("#send-mail").click(function(){
		alert('sending');
		var vals = $("#contact-subs").serializeArray();
		var msg  = $("#msg").val();
		var emails = new Array();
		for(var i = 0; i < vals.length; ++i){
			console.log(vals[i].value);
			emails.push(vals[i].value);
		}
		var packet = {
			"body": msg,
			"receivers": emails
		};
		var spacket = JSON.stringify(packet);
		console.log(spacket);
		//TODO: Post this data

		//TODO: Wait for reply that it got sent
		$("#myModal").modal('hide');
	});
});
