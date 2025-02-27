import json


def open_rc():

    with open("src/parser/json/russian-cities.json", "r", encoding="utf-8") as f:
        data: dict = json.load(f)

    population = []
    oblasts = []
    respublics = []
    districts_set = set()
    districts = list(districts_set)
    subjects = set()
    central_district_cities = []
    millions_cities = []

    for obj in data:
        population.append(obj.get("population"))
        subjects.add(obj.get("subject"))
        districts_set.add(obj.get("district"))

    districts = list(districts_set)
    districts.sort(key=lambda x: len(x))

    districts_population = {district: 0 for district in districts}
    millions_cities_population = {city: 0 for city in millions_cities}

    for obj in data:
        districts_population[obj.get("district")] += obj.get("population")

        if obj.get("district") == "Центральный":
            central_district_cities.append(obj.get("name"))

        if obj.get("population") >= 1000000:
            millions_cities.append(obj.get("name"))

    for obj in data:

        if obj.get("population") >= 1000000:
            millions_cities_population[obj.get("name")] = obj.get("population")

    sorted_districts_population = {
        district: population
        for district, population in sorted(
            districts_population.items(), key=lambda x: x[1], reverse=True
        )
    }

    sorted_m_cities_population = {
        city: population
        for city, population in sorted(
            millions_cities_population.items(), key=lambda x: x[1], reverse=True
        )
    }

    sum_m_population = 0

    for city, population in sorted_m_cities_population.items():
        print(f"{city} : {population}")
        sum_m_population += population

    print(f"Общее население городов миллионников: {sum_m_population}")


open_rc()

# python tests/rc.py
