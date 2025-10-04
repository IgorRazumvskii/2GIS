from pydantic import BaseModel
from typing import List


class Point(BaseModel):
    type: str
    lon: float
    lat: float


class PointsRequest(BaseModel):
    points: List[Point]