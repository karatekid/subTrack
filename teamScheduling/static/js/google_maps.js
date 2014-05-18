//(function() {
function initialize() {
    var map_canvas = $('#map_canvas')[0];

    var llPts = JSON.parse(llPtsJson);

    /*
    for(var i = 0; i < llPts.length; ++i) {
	for(var j = i+1; j < llPts.length; ++j) {
	    if(llPts[i]['lat'] == llPts[j]['lat'] &&
		    llPts[i]['lng'] == llPts[j]['lng']) {
		llPts.splice(j,1);
	    }
	}
    }
    */

	if(llPts.length > 0) {
		var llArr = [];
		for(var i = 0; i < llPts.length; ++i) {
			console.log(llPts[i]);
			llArr.push(
				new google.maps.LatLng(
					llPts[i]['lat'],
					llPts[i]['lng']
					)
				);
		}
		var bounds = new google.maps.LatLngBounds();
		for(var i = 0; i < llArr.length; ++i) {
			bounds.extend(llArr[i]);
		}
		var coolStyleArr = [ {
			"featureType":"all",
			"elementType":"all",
			"stylers":[
				{"invert_lightness":true},
				{"saturation":10},
				{"lightness":30},
				{"gamma":0.5},
				{"hue":"#435158"}
			]
		}];
		var map_options = {
			center: llArr[0], 
			zoom: 8,
			mapTypeId: google.maps.MapTypeId.ROADMAP,
			styles:    coolStyleArr,
		};
		var map = new google.maps.Map(map_canvas, map_options);
		map.fitBounds(bounds);
		//Create search
		var input = $('#map_search')[0];
		map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
		var searchBox = new google.maps.places.SearchBox(input);
		var markers = [];
		google.maps.event.addListener(searchBox, 'places_changed',
			function() {
				var places = searchBox.getPlaces();
				for(var i = 0, marker; marker = markers[i]; ++i) {
					marker.setMap(null);
				}
				// For each place, get the icon, place name, and location.
				markers = [];
				var bounds = new google.maps.LatLngBounds();
				for (var i = 0, place; place = places[i]; i++) {
					console.log(place);
					var image = {
						url: place.icon,
						size: new google.maps.Size(71, 71),
						origin: new google.maps.Point(0, 0),
						anchor: new google.maps.Point(17, 34),
						scaledSize: new google.maps.Size(25, 25) 
					};
					// Create a marker for each place.
					var marker = new
					google.maps.Marker({ 
						map: map, 
						icon: image,
						title: place.name,
						position: place.geometry.location
					});

					markers.push(marker);

					bounds.extend(place.geometry.location);
				}

				map.fitBounds(bounds);
			});

		// Bias the SearchBox results towards places that are within
		// the bounds of the
		// current map's viewport.
		google.maps.event.addListener(map, 'bounds_changed',
			function() {
				var bounds = map.getBounds();
				searchBox.setBounds(bounds);
			}
		);

		markerArr = [];
		//Set Markers
		for(var i = 0; i < llArr.length; ++i) {
			markerArr.push(new google.maps.Marker({
				position: llArr[i],
				map: map,
				title: llPts[i]['title'],
				//title: String(i)
			}));
		}
		//Add info Window for clicks
		var contentString = '<p>Hello World!</p>';
		var infoWindow = new google.maps.InfoWindow({
			content: contentString
		});
		for(var i = 0; i < markerArr.length; ++i) {
			//TODO: add necessary Info
			markerArr[i].contentString = '<p>' +
				markerArr[i].title+'</p>';

			google.maps.event.addListener(
				markerArr[i], 
				'click',
				function() {
					infoWindow.setContent(this.contentString);
					infoWindow.setPosition(this.position);
					infoWindow.open(map,this);
				}
			);
		}
	}
    //If no previous concerts
    else {
		$('#map_canvas').remove();
    }

    function onMarkerClick(event, marker) {
		infoWindow.setContent(contentString);
		infoWindow.setPosition(this.position);
		infoWindow.open(map,this);
    }
}
google.maps.event.addDomListener(window, 'load', initialize);

//}());
