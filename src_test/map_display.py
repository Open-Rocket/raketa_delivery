import os

# Координаты точек (широта, долгота)
points = [
    {"name": "Точка 1", "coords": [55.7558, 37.6176]},  # Москва
    {"name": "Точка 2", "coords": [59.9343, 30.3351]},  # Санкт-Петербург
    {"name": "Точка 3", "coords": [56.3287, 44.0020]},  # Нижний Новгород
]

# Ваш API-ключ Яндекс.Карт
api_key = "a8e2ea04-3a2c-4932-83b0-bf4c4e0600e8"

# Чтение HTML-шаблона
with open("yandex_map.html", "r", encoding="utf-8") as f:
    html_template = f.read()

# Замена плейсхолдеров в шаблоне
html_content = html_template.replace("ваш_api_ключ", api_key)

# Сохранение HTML-файла
with open("yandex_map.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Карта сохранена в файл yandex_map.html. Откройте его в браузере.")

# Автоматическое открытие в браузере
import webbrowser

webbrowser.open(f"file://{os.path.abspath('yandex_map.html')}")


# python src_test/map_display.py
