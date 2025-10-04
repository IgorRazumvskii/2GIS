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
        "locale": "ru"
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
    result_data = {
        "total_info": {},
        "segments": [],
        "pedestrian_paths": []
    }

    if "result" in data and isinstance(data["result"], list) and len(data["result"]) > 0:
        route = data["result"][0]

        # Общая информация о маршруте
        if "total_duration" in route:
            result_data["total_info"]["total_duration_seconds"] = route["total_duration"]
            result_data["total_info"]["total_duration_minutes"] = route["total_duration"] / 60

        if "total_distance" in route:
            result_data["total_info"]["total_distance_meters"] = route["total_distance"]
            result_data["total_info"]["total_distance_km"] = route["total_distance"] / 1000

        # Сегменты маршрута
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
                            "geometry": path.get("geometry", [])
                        }
                        result_data["segments"].append(segment)

        # Пешеходные пути
        if "begin_pedestrian_path" in route:
            begin_path = route["begin_pedestrian_path"]
            if "duration" in begin_path and "distance" in begin_path:
                result_data["pedestrian_paths"].append({
                    "type": "start",
                    "distance_meters": begin_path["distance"],
                    "duration_seconds": begin_path["duration"]
                })

        if "end_pedestrian_path" in route:
            end_path = route["end_pedestrian_path"]
            if "duration" in end_path and "distance" in end_path:
                result_data["pedestrian_paths"].append({
                    "type": "end",
                    "distance_meters": end_path["distance"],
                    "duration_seconds": end_path["duration"]
                })
    return result_data
