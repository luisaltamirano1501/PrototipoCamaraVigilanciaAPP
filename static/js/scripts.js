
// Cantidad de personas
var CantidadPersonas = registros.map(function(objeto) {
    return objeto.CantidadPersonas;
  });

console.log(CantidadPersonas)

// hora donde se detecto gente
var hora = registros.map(function(objeto) {
    return objeto.hora;
  });
console.log(hora)

// usuarios
var emails = sesiones.map(function(objeto) {
    return objeto.email;
  });
console.log(emails)

// cantidad de conexiones 
var conexiones = sesiones.map(function(objeto) {
    return objeto.sesiones;
  });
console.log(conexiones)


//Grafico lineas
const ctxLinea = document.getElementById('myChartLinea');

new Chart(ctxLinea, {
  type: 'line',
  data: {
    labels: hora,
    datasets: [{
      label: '# of Votes',
      data: CantidadPersonas,
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

const ctxBarra = document.getElementById('myChartBarras');

//Grafico Barras
new Chart(ctxBarra, {
  type: 'bar',
  data: {
    labels: emails,
    datasets: [{
      label: '# of Votes',
      data: conexiones,
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

//Grafico Circular
const ctxCirculo = document.getElementById('myChartCircular');

new Chart(ctxCirculo, {
  type: 'doughnut',
  data: {
    labels: emails,
    datasets: [{
      label: '# of Votes',
      data: conexiones,
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});





