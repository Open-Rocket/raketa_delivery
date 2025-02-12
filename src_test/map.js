function initMap() {
  // Создание карты
  var map = new ymaps.Map('map', {
    center: [55.7558, 37.6176], // Центр карты (Москва)
    zoom: 5,
  });

  // Добавление точек
  window.points.forEach(function (point) {
    var marker = new ymaps.Placemark([point.coords[0], point.coords[1]], {
      hintContent: point.name,
      balloonContent: point.name,
    });
    map.geoObjects.add(marker);
  });
}

// Инициализация карты после загрузки API
ymaps.ready(initMap);
