# Используем официальный образ OSRM
FROM osrm/osrm-backend:latest

# Копируем карту в контейнер
COPY north-caucasus-fed-district-latest.osm.pbf /data/north-caucasus-fed-district-latest.osm.pbf

RUN osrm-extract -p /opt/car.lua /data/north-caucasus-fed-district-latest.osm.pbf

# Разбиваем карту для алгоритма MLD
RUN osrm-partition /data/north-caucasus-fed-district-latest.osm.pbf

# Подготавливаем данные для маршрутизации
RUN osrm-customize /data/north-caucasus-fed-district-latest.osm.pbf

# Запускаем OSRM сервер на порту 5000
CMD ["osrm-routed", "--algorithm", "mld", "/data/north-caucasus-fed-district-latest.osm.pbf"]