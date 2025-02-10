import json


def open_rc():

    with open("src/json/russian-cities.json", "r", encoding="utf-8") as f:
        data: dict = json.load(f)

    population = []
    oblasts = []
    respublics = []
    districts_set = set()
    subjects = set()
    for obj in data:
        population.append(obj.get("population"))
        subjects.add(obj.get("subject"))
        districts_set.add(obj.get("district"))

    districts = list(districts_set)
    districts.sort(key=lambda x: len(x))

    for subject in subjects:
        if "область" in subject:
            oblasts.append(subject)
        else:
            respublics.append(subject)
            print(subject)


open_rc()

# python src_test/rc.py
