// Initialize the map
const map = L.map('map').setView([51.505, -0.09], 16); // Set to your desired coordinates

// Add a tile layer to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Define streetlight locations (coordinates)
const streetlights = [
    { id: 1, coords: [51.505, -0.09], marker: null },
    { id: 2, coords: [51.506, -0.091], marker: null },
    { id: 3, coords: [51.504, -0.089], marker: null }
];

// Add markers for streetlights and initialize them as "off"
streetlights.forEach(light => {
    light.marker = L.circleMarker(light.coords, {
        color: 'gray',
        radius: 10
    }).addTo(map).bindPopup("Streetlight " + light.id);
});

// Function to update streetlight states
function updateStreetlights() {
    fetch("/motion")
        .then(response => response.json())
        .then(data => {
            if (data.motion_detected) {
                // Turn lights "on"
                streetlights.forEach(light => {
                    light.marker.setStyle({ color: 'yellow' });
                });
            } else {
                // Turn lights "off"
                streetlights.forEach(light => {
                    light.marker.setStyle({ color: 'gray' });
                });
            }
        });
}

// Periodically check motion data and update the map
setInterval(updateStreetlights, 1000);
