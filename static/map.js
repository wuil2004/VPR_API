const coords = {
    "EDO.MEX": [19.2938, -99.6536],
    "QRO": [20.5935, -100.3900],
    "CDMX": [19.4328, -99.1333],
    "SLP": [22.1517, -100.9765],
    "MTY": [25.6731, -100.2974],
    "PUE": [19.0635, -98.3072],
    "GDL": [20.6771, -103.3469],
    "MICH": [19.7026, -101.1922],
    "SON": [29.0752, -110.9596]
};

const map = L.map("map").setView(coords["CDMX"], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

rutas.forEach((ruta, i) => {
    const latlngs = ruta.map(ciudad => coords[ciudad]);
    const polyline = L.polyline(latlngs, { color: getColor(i), weight: 4 }).addTo(map);
    latlngs.forEach((punto, j) => {
        L.marker(punto).bindPopup(`${ruta[j]}`).addTo(map);
    });
});

function getColor(i) {
    const colores = ["red", "blue", "green", "orange", "purple", "brown"];
    return colores[i % colores.length];
}