const coordenadas = {
  'EDO.MEX': [19.2938258568844, -99.65366252023884],
  'QRO': [20.593537489366717, -100.39004057702225],
  'CDMX': [19.432854452264177, -99.13330004822943],
  'SLP': [22.151725492903953, -100.97657666103268],
  'MTY': [25.673156272083876, -100.2974200019319],
  'PUE': [19.063532268065185, -98.30729139446866],
  'GDL': [20.67714565083998, -103.34696388920293],
  'MICH': [19.702614895389996, -101.19228631929688],
  'SON': [29.075273188617818, -110.95962477655333]
};

const pedido = {
  'EDO.MEX': 10,
  'QRO': 13,
  'CDMX': 7,
  'SLP': 11,
  'MTY': 15,
  'PUE': 8,
  'GDL': 6,
  'MICH': 7,
  'SON': 8
};

async function calcularRutas() {
  const almacen = document.getElementById('almacen').value;
  const ciudadesSeleccionadas = Array.from(document.getElementById('ciudades').selectedOptions)
                                    .map(option => option.value)
                                    .filter(c => c !== almacen);

  const resultadoDiv = document.getElementById('resultado');
  resultadoDiv.innerHTML = '<p>Calculando rutas...</p>';

  if (ciudadesSeleccionadas.length === 0) {
      resultadoDiv.innerHTML = '<p style="color:red;">Debes seleccionar al menos una ciudad para visitar.</p>';
      return;
  }

  const coord = {};
  const pedidos = {};

  for (const ciudad of ciudadesSeleccionadas.concat(almacen)) {
      coord[ciudad] = coordenadas[ciudad];
      pedidos[ciudad] = pedido[ciudad];
  }

  try {
      const response = await fetch('/api/calcular', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              coord: coord,
              pedidos: pedidos,
              almacen: coordenadas[almacen],
              max_carga: parseInt(document.getElementById('max_carga').value),
              max_litros: parseFloat(document.getElementById('max_litros').value),
              max_distancia: parseFloat(document.getElementById('max_distancia').value),
              litros_por_km: parseFloat(document.getElementById('litros_por_km').value)
          })
      });

      const data = await response.json();

      if (data.rutas.length === 0) {
          resultadoDiv.innerHTML = '<p style="color: darkred;">No se encontraron rutas que cumplan las restricciones dadas.</p>';
          return;
      }

      let html = '';
      data.rutas.forEach((ruta, i) => {
          html += `
              <div style="margin-bottom: 1rem; border-bottom: 1px dashed #ccc;">
                  <h3>Ruta ${i + 1}</h3>
                  <p><strong>Ciudades:</strong> ${ruta.ruta.join(' → ')}</p>
                  <p><strong>Distancia:</strong> ${ruta.distancia.toFixed(2)} unidades</p>
                  <p><strong>Combustible:</strong> ${ruta.combustible.toFixed(2)} litros</p>
              </div>
          `;
      });

      resultadoDiv.innerHTML = html;

  } catch (error) {
      console.error(error);
      resultadoDiv.innerHTML = '<p style="color:red;">Error al calcular rutas. Revisa la consola para más información.</p>';
  }
}
