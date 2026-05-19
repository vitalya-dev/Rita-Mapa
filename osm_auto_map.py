import folium
import requests
import time

def fetch_coordinates(search_query):
    """Отправляет запрос к OpenStreetMap и возвращает (широту, долготу) или (None, None)"""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'SchoolGeographyHomeworkBot/1.5'}
    params = {
        'q': search_query,
        'format': 'json',
        'limit': 1
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"⚠️ Ошибка сети при поиске '{search_query}': {e}")
        
    return None, None

def create_osm_auto_map():
    print("🚀 Создаем карту и начинаем умный поиск объектов... Подожди минутку!")
    
    # Топографическая подложка
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

    # Список слов-паразитов, которые мы будем отрезать, если поиск не удался
    words_to_remove = [
        "горы", "гора", "хребет", "река", "озеро", "море", 
        "залив", "пролив", "губа", "нагорье", "плоскогорье", "россия"
    ]

    for name in places:
        # 1. Попытка №1: Ищем как есть
        lat, lon = fetch_coordinates(name)
        time.sleep(1.5) # Обязательная пауза!
        
        # 2. Попытка №2: Если не нашли, включаем запасной план
        if lat is None:
            # Разбиваем строку на слова, выкидываем слова-паразиты и склеиваем обратно
            fallback_name = " ".join([
                w for w in name.split() 
                if w.lower().replace(',', '') not in words_to_remove
            ])
            
            # Если после очистки что-то осталось (например "Бырранга"), ищем снова
            if fallback_name and fallback_name != name:
                print(f"🔄 Уточняем поиск: '{name}' -> ищем просто '{fallback_name}'...")
                lat, lon = fetch_coordinates(fallback_name)
                time.sleep(1.5) # Снова пауза после запроса
        
        # 3. Финальная проверка: ставим маркер, если координаты нашлись
        if lat is not None:
            clean_name = name.replace(", Россия", "") # Чистим для красивой всплывашки
            
            # Определяем цвет маркера по оригинальному названию
            is_water = any(word in clean_name.lower() for word in ["река", "море", "озеро", "залив", "пролив", "губа"])
            marker_color = "blue" if is_water else "red"
            
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{clean_name}</b>",
                tooltip=clean_name,
                icon=folium.Icon(color=marker_color, icon="info-sign")
            ).add_to(my_map)
            
            print(f"✅ Найдено: {clean_name}")
        else:
            print(f"❌ Провал: не удалось найти даже по запасному варианту: {name}")

    # Сохраняем готовую карту
    output_file = "osm_geography_map_smart.html"
    my_map.save(output_file)
    print(f"\n🎉 ГОТОВО! Карта сохранена в файл {output_file}.")

# Запуск
create_osm_auto_map()