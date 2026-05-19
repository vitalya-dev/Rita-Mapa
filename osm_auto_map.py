import folium
import requests
import time

def fetch_data(search_query, need_polygon=False):
    """Отправляем запрос к OSM. Если need_polygon=True, просим геометрию (границы/русло)."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'SchoolGeographyHomeworkBot/6.0'}
    params = {
        'q': search_query,
        'format': 'json',
        'limit': 1
    }
    
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

def create_natgeo_ultimate_map():
    print("🚀 Создаем полную карту (National Geographic) со всеми правками...")
    
    # Красивая топографическая подложка в стиле школьного атласа
    natgeo_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}"
    
    my_map = folium.Map(
        location=[61.5, 90.0], 
        zoom_start=3, 
        tiles=natgeo_tiles, 
        attr="Esri National Geographic"
    )

    places = [
        # --- ГОРЫ (Красный) ---
        "Алтайские горы, Россия", "горы Бырранга", "Верхоянский хребет", "Восточный Саян", 
        "хребет Джугджур", "Западный Саян", "Кавказские горы", "Колымское нагорье", 
        "Корякское нагорье", "хребет Сихотэ-Алинь", "Становое нагорье", "Уральские горы, Россия", 
        "Чукотское нагорье", "Среднесибирское плоскогорье", "гора Эльбрус",
        
        # --- ВОДА (Синий) ---
        "река Ангара", "река Амур", "река Волга", "река Дон", "река Енисей", 
        "река Индигирка", "река Иртыш", "река Колыма", "река Кубань", "река Лена", 
        "река Обь", "река Печора", "река Северная Двина",
        "Азовское море", "Балтийское море", "Баренцево море", "Белое море", 
        "Берингово море", "Восточно-Сибирское море", "Карское море", "море Лаптевых", 
        "Охотское море", "Чёрное море", "Чукотское море", "Японское море", "Каспийское море",
        "озеро Байкал", "Ладожское озеро", "Онежское озеро", "озеро Таймыр", "озеро Ханка",
        "Анадырский залив", "Енисейский залив", "Обская губа", "Финский залив", "залив Шелихова",
        "Берингов пролив", "пролив Карские Ворота", "Керченский пролив", "пролив Лаперуза", 
        "пролив Дмитрия Лаптева", "пролив Лонга", "Татарский пролив",
        
        # --- ОСТРОВА И ПОЛУОСТРОВА (Черный) ---
        "остров Врангеля", "Земля Франца-Иосифа", "Курильские острова",
        "Новая Земля", "Сахалин", "Северная Земля",
        "Гыданский полуостров", "Камчатка", "полуостров Канин",
        "Кольский полуостров", "Крым", "полуостров Таймыр", 
        "Чукотка", "Ямал",
        
        # --- РАВНИНЫ И НИЗМЕННОСТИ (Зеленый) ---
        "Восточно-Европейская равнина", "Западно-Сибирская равнина",
        "Прикаспийская низменность", "Северо-Сибирская низменность",
        "Колымская низменность", "Среднерусская возвышенность",
        "Северные Увалы", "Тиманский кряж", "Енисейский кряж"
    ]

    # Слова для очистки названий, если первый поиск не удался (без слова "земля")
    words_to_remove = [
        "горы", "гора", "хребет", "река", "озеро", "море", "залив", "пролив", "губа", 
        "нагорье", "плоскогорье", "россия", "остров", "полуостров", "архипелаг", 
        "равнина", "низменность", "возвышенность", "увалы", "кряж"
    ]

    for name in places:
        name_lower = name.lower()
        
        # Просим полигоны для масштабных объектов и рек
        is_polygon_query = any(w in name_lower for w in ["река", "равнина", "низменность", "возвышенность", "увалы", "кряж", "плоскогорье"])
        
        result_data = fetch_data(name, need_polygon=is_polygon_query)
        time.sleep(1.5) # Бережем сервера OSM!
        
        if not result_data:
            # Запасной план: отрезаем лишние слова
            fallback_name = " ".join([w for w in name.split() if w.lower().replace(',', '') not in words_to_remove])
            if fallback_name and fallback_name != name:
                print(f"🔄 Уточняем поиск: '{name}' -> ищем '{fallback_name}'...")
                result_data = fetch_data(fallback_name, need_polygon=is_polygon_query)
                time.sleep(1.5)
        
        if result_data:
            clean_name = name.replace(", Россия", "")
            name_lower_clean = clean_name.lower()
            
            # Цвета по правилам контурной карты
            if any(w in name_lower_clean for w in ["река", "море", "озеро", "залив", "пролив", "губа"]):
                marker_color = "blue"
            elif any(w in name_lower_clean for w in ["остров", "полуостров", "архипелаг", "земля", "сахалин", "камчатка", "крым", "чукотка", "ямал"]):
                marker_color = "black"
            elif any(w in name_lower_clean for w in ["равнина", "низменность", "возвышенность", "увалы", "кряж"]):
                marker_color = "green"
            else:
                marker_color = "red" 
            
            geom = result_data.get('geojson', {})
            geom_type = geom.get('type', 'Point')

            # Рисуем полигон/линию, если запрашивали и сервер её вернул
            if is_polygon_query and geom_type in ['LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']:
                folium.GeoJson(
                    geom,
                    name=clean_name,
                    tooltip=clean_name,
                    style_function=lambda x, c=marker_color: {'color': c, 'weight': 4, 'fillOpacity': 0.3}
                ).add_to(my_map)
                print(f"🌍 Нарисована область/линия ({marker_color}): {clean_name}")
            else:
                # В остальных случаях ставим метку
                lat, lon = float(result_data['lat']), float(result_data['lon'])
                folium.Marker(
                    location=[lat, lon],
                    popup=f"<b>{clean_name}</b>",
                    tooltip=clean_name,
                    icon=folium.Icon(color=marker_color, icon="info-sign")
                ).add_to(my_map)
                print(f"📍 Поставлена метка ({marker_color}): {clean_name}")
                
        else:
            print(f"❌ Не удалось найти: {name}")

    output_file = "geography_final_master_map.html"
    my_map.save(output_file)
    print(f"\n🎉 ГОТОВО! Карта сохранена в {output_file}.")

# Запуск!
create_natgeo_ultimate_map()