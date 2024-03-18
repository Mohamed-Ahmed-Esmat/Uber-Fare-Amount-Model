var map;
var pickupMarker = null;
var dropoffMarker = null;
var pickupSelected = false;
var bothSelected = false;
var clickListener = null;
var searchBox;
var pick_lat, pick_long, drop_lat, drop_long; // Added variables

function initMap() {
    var newYorkBounds = {
        north: 40.9176,
        south: 40.4774,
        west: -74.2591,
        east: -73.7004,
    };

    map = new google.maps.Map(document.getElementById('map'), {
        center: {
            lat: 40.75091443379888,
            lng: -73.97553852673146,
        },
        zoom: 10.6,
        mapId: '862b3a13a839d655',
        mapTypeControl: false,
        fullscreenControl: false,
        streetViewControl: false,
        restriction: {
            latLngBounds: newYorkBounds,
            strictBounds: true,
        },
        minZoom: 8,
    });

    var input = document.getElementById("pac-input");
    searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    map.addListener("bounds_changed", function () {
        searchBox.setBounds(map.getBounds());
    });

    var markers = [];

    searchBox.addListener("places_changed", function () {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        markers.forEach(function (marker) {
            marker.setMap(null);
        });
        markers = [];

        var bounds = new google.maps.LatLngBounds();

        places.forEach(function (place) {
            if (!place.geometry || !place.geometry.location) {
                console.log("Returned place contains no geometry");
                return;
            }

            var icon = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25),
            };

            markers.push(
                new google.maps.Marker({
                    map: map,
                    icon: icon,
                    title: place.name,
                    position: place.geometry.location,
                })
            );

            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);
    });

    clickListener = map.addListener('click', function (e) {
        if (!pickupSelected) {
            handlePickupSelection(e.latLng);
        } else if (!bothSelected) {
            handleDropoffSelection(e.latLng);
        }
    });

    document.getElementById('selectLocations').addEventListener('click', function () {
        if (bothSelected) {
            handleBothSelected();
        } else {
            searchBoxPlaces();
        }
    });

    function handlePickupSelection(latLng) {
        if (pickupMarker) {
            pickupMarker.setMap(null);
        }
        pick_lat = latLng.lat();
        pick_long = latLng.lng();
        console.log('Pickup Latitude: ' + pick_lat + ', Pickup Longitude: ' + pick_long);
        pickupMarker = createMarker(latLng, 'http://maps.google.com/mapfiles/ms/icons/green-dot.png');
        pickupSelected = true;
    }

    function handleDropoffSelection(latLng) {
        if (dropoffMarker) {
            dropoffMarker.setMap(null);
        }
        drop_lat = latLng.lat();
        drop_long = latLng.lng();
        console.log('Dropoff Latitude: ' + drop_lat + ', Dropoff Longitude: ' + drop_long);
        dropoffMarker = createMarker(latLng, 'http://maps.google.com/mapfiles/ms/icons/red-dot.png');
        bothSelected = true;
        google.maps.event.removeListener(clickListener);
    }

    function handleBothSelected() {
        if (pickupMarker) {
            pickupMarker.setMap(null);
        }
        if (dropoffMarker) {
            dropoffMarker.setMap(null);
        }
        pickupSelected = false;
        bothSelected = false;
        clickListener = map.addListener('click', function (e) {
            if (!pickupSelected) {
                handlePickupSelection(e.latLng);
            } else if (!bothSelected) {
                handleDropoffSelection(e.latLng);
            }
        });
    }

    function searchBoxPlaces() {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        var bounds = new google.maps.LatLngBounds();

        places.forEach(function (place) {
            if (!place.geometry || !place.geometry.location) {
                console.log("Returned place contains no geometry");
                return;
            }

            var icon = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25),
            };

            markers.push(
                createMarker(place.geometry.location, icon, place.name)
            );

            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);
    }

    function createMarker(position, iconUrl, title) {
        return new google.maps.Marker({
            position: position,
            map: map,
            icon: iconUrl,
            title: title || '',
        });

        
    }
    document.getElementById('predictButton').addEventListener('click', function() {
        console.log('Button clicked!');
        sendCoordinatesToServer();
    });

    document.getElementById('trip-form').addEventListener('submit', function(event) {
        var tripDate = document.getElementById('trip-date').value;
        var tripTime = document.getElementById('trip-time').value;
        var passengerCount = document.getElementById('passenger-count').value;
        event.preventDefault(); // Prevent form from submitting
        
        if (!tripDate) {
            alert('Please select a trip date before submitting.');
            event.preventDefault(); // Prevent form from submitting
        } else if (!passengerCount) {
            alert('Please enter the passenger count before submitting.');
            event.preventDefault(); // Prevent form from submitting
        }else if (!tripTime) {
            alert('Please select a trip time before submitting.');
            event.preventDefault(); // Prevent form from submitting
        } else if (!pickupSelected || !bothSelected) {
            //  alert('Please select both pickup and dropoff locations on the map before submitting.');
            event.preventDefault(); // Prevent form from submitting
        }
    });

    $(document).ready(function() {
        console.log($('#fare-amount').text());
    });

}

initMap();
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.onload = function() {
    // Update the HTML with the predicted fare amount
    var fareAmount = sessionStorage.getItem("fare-amount");
    if (fareAmount) {
        document.getElementById('fare-amount').innerText = fareAmount.toFixed(2); // Display fare amount with two decimal places
    }
}

function sendCoordinatesToServer() {
    var url = '/predict';

    // Check if both pickup and dropoff markers are selected
    if (!pickupSelected || !bothSelected) {
        alert('Please select both pickup and dropoff locations on the map before predicting.');
        return;
    }

    console.log("Final data before sending them:")
    console.log("pick_lat: ", pick_lat)
    console.log("pick_long: ", pick_long)
    console.log("drop_lat: ", drop_lat)
    console.log("drop_long: ", drop_long)

    var data = {
        'pick_lat': pick_lat,
        'pick_long': pick_long,
        'drop_lat': drop_lat,
        'drop_long': drop_long,
        'trip-date': document.getElementById('trip-date').value,
        'trip-time': document.getElementById('trip-time').value,
        'passenger-count': document.getElementById('passenger-count').value
    };
    console.log("Trying to check the function")

    var csrftoken = getCookie('csrftoken');
    data_json = JSON.stringify(data)
    console.log("Data Json: ", data_json)
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: data_json,
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            console.error('Error:', response.statusText);
        }
    })
    .then(data => {
        console.log('Server response:', data.result);
    
        // Store data.result in localStorage
        // Convert data.result to float and store in sessionStorage
        sessionStorage.setItem('fare-amount', parseFloat(data.result));
        // Update the HTML with the predicted fare amount
        document.getElementById('fare-amount').innerText = '$' + parseFloat(data.result).toFixed(2); // Display fare amount with two decimal places and a dollar sign
    })
    .catch((error) => console.error('Error:', error));
}
