import requests
import json
import datetime
import os
from typing import List
from models import Point


def get_routing_curl_style(api_key, app_id, points: List[Point]):
    url = f"http://routing.api.2gis.com/routing/7.0.0/global?key={api_key}"

    headers = {
        'Content-Type': 'application/json',
        'X-App-Id': app_id
    }

    points_data = [point.dict() for point in points]

    data = {
        "points": points_data,
        "transport": "driving",
        "filters": [],
        "output": "detailed",
        "locale": "ru",
        "traffic_mode": "jam",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )
        print(f"Status Code: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_route_data_from_json(data: dict):
    """
    Преобразует JSON с маршрутом от 2ГИС в удобный формат для визуализации:
    - total_info: общая длительность и расстояние
    - segments: список сегментов с геометрией, временем, расстоянием и скоростью
    - pedestrian_paths: данные о пешеходных участках
    """
    def parse_linestring(selection: str):
        """Парсинг строки LINESTRING в список [lon, lat]"""
        selection = selection.replace("LINESTRING(", "").replace(")", "")
        points = []
        for pair in selection.split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                lon, lat = map(float, parts[:2])
                points.append([lon, lat])
        return points

    result_data = {
        "total_info": {},
        "segments": [],
        "pedestrian_paths": []
    }

    if "result" in data and isinstance(data["result"], list) and len(data["result"]) > 0:
        route = data["result"][0]

        # --- Общая информация ---
        if "total_duration" in route:
            total_sec = route["total_duration"]
            result_data["total_info"]["total_duration_seconds"] = total_sec
            result_data["total_info"]["total_duration_minutes"] = total_sec / 60

        if "total_distance" in route:
            total_m = route["total_distance"]
            result_data["total_info"]["total_distance_meters"] = total_m
            result_data["total_info"]["total_distance_km"] = total_m / 1000

        # --- Сегменты маршрута ---
        if "maneuvers" in route:
            for i, maneuver in enumerate(route["maneuvers"]):
                if "outcoming_path" in maneuver:
                    path = maneuver["outcoming_path"]
                    if "duration" in path and "distance" in path:
                        segment = {
                            "segment_number": i + 1,
                            "type": maneuver.get("type", "unknown"),
                            "comment": maneuver.get("comment", ""),
                            "distance_meters": path["distance"],
                            "duration_seconds": path["duration"],
                            "speed_mps": path["distance"] / path["duration"] if path["duration"] > 0 else 0,
                            "geometry": path.get("geometry", []),
                            "geometry_coords": []
                        }
                        # Разбираем геометрию для анимации
                        for g in path.get("geometry", []):
                            if "selection" in g:
                                segment["geometry_coords"].extend(parse_linestring(g["selection"]))
                        # Опционально: угол и направление поворота
                        segment["turn_angle"] = maneuver.get("turn_angle")
                        segment["turn_direction"] = maneuver.get("turn_direction")
                        result_data["segments"].append(segment)

        # --- Пешеходные пути ---
        for key, path_key in [("begin_pedestrian_path", "start"), ("end_pedestrian_path", "end")]:
            if key in route:
                ppath = route[key]
                if "distance" in ppath and "duration" in ppath:
                    path_dict = {
                        "type": path_key,
                        "distance_meters": ppath["distance"],
                        "duration_seconds": ppath["duration"],
                        "speed_mps": ppath["distance"] / ppath["duration"] if ppath["duration"] > 0 else 0,
                        "geometry_coords": []
                    }
                    # Геометрия пешеходного пути
                    geometry = ppath.get("geometry", {})
                    if "selection" in geometry:
                        path_dict["geometry_coords"] = parse_linestring(geometry["selection"])
                    result_data["pedestrian_paths"].append(path_dict)

    return result_data

