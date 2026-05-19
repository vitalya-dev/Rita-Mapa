import folium
import requests
import time

def fetch_data(search_query):
    """Отправляем запрос к OSM и просим вернуть полную форму объекта (линию русла или границы)"""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'SchoolGeographyHomeworkBot/2.0'}
    params = {
        'q': search_query,
        'format': 'json',
        'limit': 1,
        'polygon_geojson': 1,
        'polygon_threshold': 0.05  # 👈 Тот самый секретный параметр для получения контуров!
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data:
            return data[0] # Возвращаем первый найденный объект целиком
    except Exception as e:
        print(f"⚠️ Ошибка сети при поиске '{search_query}': {e}")
        
    return None

def create_osm_pro_map():
    print("🚀 Создаем PRO-карту: загружаем русла рек и границы морей... Подожди минутку!")
    
    # Топографическая подложка (хорошо видны высоты)
    topo_tiles = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
    my_map = folium.Map(location=[61.5, 90.0], zoom_start=3, tiles=topo_tiles, attr="OpenTopoMap")

    places = [
        "Алтайские горы, Россия", "горы Бырранга", "Верхоянский хребет", "Восточный Саян", 
        "хребет Джугджур", "Западный Саян", "Кавказские горы", "Колымское нагорье", 
        "Корякское нагорье", "хребет Сихотэ-Алинь", "Становое нагорье", "Уральские горы, Россия", 
        "Чукотское нагорье", "Среднесибирское плоскогорье", "гора Эльбрус",
        "река Ангара", "река Амур", "река Волга", "река Дон", "река Енисей", 
        "река Индигирка", "река Иртыш", "река Колыма", "река Кубань", "река Лена", 
        "река Обь", "река Печора", "река Северная Двина",
        "Азовское море", "Балтийское море", "Баренцево море", "Белое море", 
        "Берингово море", "Восточно-Сибирское море", "Карское море", "море Лаптевых", 
        "Охотское море", "Чёрное море", "Чукотское море", "Японское море", "Каспийское море",
        "озеро Байкал", "Ладожское озеро", "Онежское озеро", "озеро Таймыр", "озеро Ханка",
        "Анадырский залив", "Енисейский залив", "Обская губа", "Финский залив", "залив Шелихова",
        "Берингов пролив", "пролив Карские Ворота", "Керченский пролив", "пролив Лаперуза", 
        "пролив Дмитрия Лаптева", "пролив Лонга", "Татарский пролив"
    ]

    # Слова для обрезки (наш запасной план)
    words_to_remove = ["горы", "гора", "хребет", "река", "озеро", "море", "залив", "пролив", "губа", "нагорье", "плоскогорье", "россия"]

    for name in places:
        result_data = fetch_data(name)
        time.sleep(1.5) # Не забываем про паузу для сервера
        
        # Если не нашли, отрезаем лишние слова и ищем снова
        if not result_data:
            fallback_name = " ".join([w for w in name.split() if w.lower().replace(',', '') not in words_to_remove])
            if fallback_name and fallback_name != name:
                print(f"🔄 Уточняем поиск: '{name}' -> ищем просто '{fallback_name}'...")
                result_data = fetch_data(fallback_name)
                time.sleep(1.5)
        
        # Если наконец что-то нашли
        if result_data:
            clean_name = name.replace(", Россия", "")
            
            # Определяем цвет по названию
            is_water = any(word in clean_name.lower() for word in ["река", "море", "озеро", "залив", "пролив", "губа"])
            marker_color = "blue" if is_water else "red"
            
            # Достаем геометрию. Если её нет, считаем, что это точка
            geom = result_data.get('geojson', {})
            geom_type = geom.get('type', 'Point')

            if geom_type in ['LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']:
                # 🔥 МАГИЯ: Рисуем извилистую реку или закрашиваем море!
                # Передаем цвет в лямбда-функцию, чтобы линии раскрашивались правильно
                folium.GeoJson(
                    geom,
                    name=clean_name,
                    tooltip=clean_name,
                    style_function=lambda x, c=marker_color: {'color': c, 'weight': 5, 'fillOpacity': 0.3}
                ).add_to(my_map)
                print(f"🌊 Нарисована линия/форма ({geom_type}): {clean_name}")
            
            else:
                # 📍 Классический маркер, если форма неизвестна или это вулкан (точка)
                lat, lon = float(result_data['lat']), float(result_data['lon'])
                folium.Marker(
                    location=[lat, lon],
                    popup=f"<b>{clean_name}</b>",
                    tooltip=clean_name,
                    icon=folium.Icon(color=marker_color, icon="info-sign")
                ).add_to(my_map)
                print(f"📍 Поставлена точка: {clean_name}")
                
        else:
            print(f"❌ Провал: не удалось найти в базе: {name}")

    # Сохраняем карту
    output_file = "osm_geography_map_pro.html"
    my_map.save(output_file)
    print(f"\n🎉 ГОТОВО! PRO-карта сохранена в файл {output_file}. Скорей открывай!")

# Запускаем
create_osm_pro_map()