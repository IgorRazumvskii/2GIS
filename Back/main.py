from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
import httpx
from dotenv import load_dotenv
import os


# modules
from scripts import get_routing_curl_style, parse_route_data_from_json
from models import *

app = FastAPI()
load_dotenv()
API_KEY = os.getenv("API_KEY")
APP_ID = os.getenv("APP_ID")


@app.post("/points")
async def receive_points(request: PointsRequest):
    points_list = request.points
    routing_result = get_routing_curl_style(API_KEY, APP_ID, points_list)
    # return routing_result
    parsed_result = parse_route_data_from_json(routing_result)
    return parsed_result
