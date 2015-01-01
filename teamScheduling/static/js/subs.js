$(document).ready(function(){
	var getMailToTemplate = function(recipients, subject, body){
		return "mailto:"+recipients.join(',')
			+  "?subject=" + subject
			+  "&body="+body;
	};
	var getMailTo = function(vals){
		var recipients = new Array();
		for(var i = 0; i < vals.length; ++i){
			recipients.push(vals[i].value);
		}
		var re = /\/team\/(\d+)\/game\/(\d+)/;
		var result = re.exec(window.location.pathname);
		var teamNum = result[1];
		var gameNum = result[2];
		var msgData = $.ajax({
			type: "GET",
			url:  "/api/message-info/team/"+teamNum+"/game/"+gameNum,
			async: false
		}).responseJSON;
		console.log(msgData);
		return getMailToTemplate(recipients, 
			msgData['subject'], 
			msgData['body']);
	};
	$("#contact-subs").submit(function(event){
		event.preventDefault();
		//alert($(this).serialize());
		var vals = $(this).serializeArray();
		var link = $('<a>').attr('target','_top')
					.attr('href',getMailTo(vals))
					.attr('id','mail-link')
					.appendTo('body')
					.hide()[0].click();
		//populate send-list
		/*
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
		*/
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
