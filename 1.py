import folium

# 1. Создаем базовую карту мира. 
# location=[20, 0] - центр карты, zoom_start=2 - начальный масштаб
my_map = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# --- ДОБАВЛЯЕМ ОБЪЕКТЫ ---

# 1. Полуостров (например, Флорида). Поставим обычный маркер
folium.Marker(
    location=[28.0, -81.5], # Координаты Флориды
    popup="<b>Полуостров Флорида</b>",
    tooltip="Нажми меня",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(my_map)

# 2. Остров (например, Мадагаскар). 
folium.Marker(
    location=[-18.7669, 46.8691],
    popup="<b>Остров Мадагаскар</b>",
    tooltip="Мадагаскар",
    icon=folium.Icon(color="green", icon="leaf")
).add_to(my_map)

# 3. Пустыня (например, Сахара). Нарисуем желтый круг, покрывающий территорию
folium.Circle(
    location=[23.8, 11.2], # Центр Сахары
    radius=1500000,        # Радиус в метрах (1500 км)
    popup="Пустыня Сахара",
    color="orange",        # Цвет границы
    fill=True,
    fill_color="yellow"    # Цвет заливки
).add_to(my_map)

# 4. Горная система (например, Уральские горы). Нарисуем линию вдоль хребта
ural_mountains_coords = [
    [68.0, 60.0], # Северная часть
    [60.0, 59.0], # Средняя часть
    [52.0, 58.0]  # Южная часть
]
folium.PolyLine(
    locations=ural_mountains_coords,
    color="brown",
    weight=5, # Толщина линии
    tooltip="Уральские горы"
).add_to(my_map)


# --- СОХРАНЯЕМ РЕЗУЛЬТАТ ---
# Сохраняем нашу карту в HTML файл
my_map.save("geography_map.html")
print("Карта готова! Открой файл geography_map.html в браузере.")