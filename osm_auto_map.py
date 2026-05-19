import folium
import requests
import time

def fetch_data(search_query, need_polygon=False):
    """Отправляем запрос к OSM. Если need_polygon=True, просим форму русла."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'SchoolGeographyHomeworkBot/3.0'}
    params = {
        'q': search_query,
        'format': 'json',
        'limit': 1
    }
    
    # Если это река, просим сервер вернуть сжатую линию
    if need_polygon:
        params['polygon_geojson'] = 1
        params['polygon_threshold'] = 0.05 
        
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data:
            return data[0]
    except Exception as e:
        print(f"⚠️ Ошибка сети при поиске '{search_query}': {e}")
        
    return None

def create_natgeo_final_map():
    print("🚀 Создаем финальную карту в стиле National Geographic...")
    
    # Подложка National Geographic
    natgeo_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}"
    
    my_map = folium.Map(
        location=[61.5, 90.0], 
        zoom_start=3, 
        tiles=natgeo_tiles, 
        attr="Esri National Geographic"
    )

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

    words_to_remove = ["горы", "гора", "хребет", "река", "озеро", "море", "залив", "пролив", "губа", "нагорье", "плоскогорье", "россия"]

    for name in places:
        is_river_query = "река" in name.lower()
        
        result_data = fetch_data(name, need_polygon=is_river_query)
        time.sleep(1.5)
        
        if not result_data:
            fallback_name = " ".join([w for w in name.split() if w.lower().replace(',', '') not in words_to_remove])
            if fallback_name and fallback_name != name:
                print(f"🔄 Уточняем поиск: '{name}' -> ищем '{fallback_name}'...")
                result_data = fetch_data(fallback_name, need_polygon=is_river_query)
                time.sleep(1.5)
        
        if result_data:
            clean_name = name.replace(", Россия", "")
            
            is_water = any(word in clean_name.lower() for word in ["река", "море", "озеро", "залив", "пролив", "губа"])
            is_river = "река" in clean_name.lower()
            marker_color = "blue" if is_water else "red"
            
            geom = result_data.get('geojson', {})
            geom_type = geom.get('type', 'Point')

            if is_river and geom_type in ['LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']:
                folium.GeoJson(
                    geom,
                    name=clean_name,
                    tooltip=clean_name,
                    style_function=lambda x, c=marker_color: {'color': c, 'weight': 4, 'fillOpacity': 0.3}
                ).add_to(my_map)
                print(f"🌊 Нарисовано русло реки: {clean_name}")
            
            else:
                lat, lon = float(result_data['lat']), float(result_data['lon'])
                folium.Marker(
                    location=[lat, lon],
                    popup=f"<b>{clean_name}</b>",
                    tooltip=clean_name,
                    icon=folium.Icon(color=marker_color, icon="info-sign")
                ).add_to(my_map)
                print(f"📍 Поставлена метка: {clean_name}")
                
        else:
            print(f"❌ Не удалось найти: {name}")

    output_file = "natgeo_geography_map.html"
    my_map.save(output_file)
    print(f"\n🎉 КРАСОТА НАВЕДЕНА! Карта сохранена в {output_file}.")

create_natgeo_final_map()