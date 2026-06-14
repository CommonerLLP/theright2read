#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.recipes.accessibility.library_access import haversine_m, threshold_share, weighted_quantile


WARDS = REPO / "data" / "cities" / "ahmedabad" / "layers" / "wards.geojson"
LIBRARIES = REPO / "data" / "cities" / "ahmedabad" / "source" / "libraries" / "ahmedabad_library_locations.csv"
TRANSIT_STOPS = REPO / "data" / "cities" / "ahmedabad" / "source" / "transit" / "transit_stops.json"
ROUTE_CORRIDORS = REPO / "data" / "cities" / "ahmedabad" / "source" / "transit" / "route_corridors.json"
OUT_DIR = REPO / "data" / "cities" / "ahmedabad" / "derived" / "library_access"

WALK_SPEED_KMPH = 4.8
TRANSIT_SPEED_KMPH = 18.0
ROUTE_DISTANCE_FACTOR = 1.35
WAIT_AND_TRANSFER_MINUTES = 10.0

ORIGIN_FIELDS = [
    "ward_no",
    "ward_name",
    "population",
    "centroid_latitude",
    "centroid_longitude",
    "nearest_library_id",
    "nearest_library_name",
    "distance_m_to_nearest_library",
    "walk_minutes_to_nearest_library",
    "nearest_transit_stop_m",
    "walk_minutes_to_nearest_transit_stop",
    "nearest_transit_corridor_m",
    "walk_minutes_to_nearest_transit_corridor",
    "transit_proxy_minutes_to_nearest_library",
    "best_walk_or_transit_proxy_minutes",
    "routing_tier",
    "confidence",
    "notes",
]

SUMMARY_FIELDS = [
    "city",
    "origins",
    "population",
    "library_locations",
    "coordinate_verified_locations",
    "transit_stops",
    "routing_tier",
    "p50_minutes_to_nearest_library_walk",
    "p75_minutes_to_nearest_library_walk",
    "p90_minutes_to_nearest_library_walk",
    "pct_population_within_10_min_walk",
    "pct_population_within_15_min_walk",
    "pct_population_within_20_min_walk",
    "pct_population_within_30_min_walk",
    "pct_population_within_45_min_walk",
    "p50_minutes_to_nearest_transit_stop_walk",
    "p50_minutes_to_nearest_transit_corridor_walk",
    "p50_minutes_to_nearest_library_transit_proxy",
    "p50_minutes_to_nearest_library_best_proxy",
    "access_status",
    "confidence",
    "notes",
]

CATCHMENT_FIELDS = [
    "library_id",
    "library_name",
    "assigned_ward_count",
    "assigned_population",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Ahmedabad population-weighted library accessibility outputs.")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    origin_rows, catchment_rows, summary_rows, metadata = build_ahmedabad_library_access()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "origin_travel_times.csv", origin_rows, ORIGIN_FIELDS)
    write_csv(args.out_dir / "library_catchments.csv", catchment_rows, CATCHMENT_FIELDS)
    write_csv(args.out_dir / "library_access_summary.csv", summary_rows, SUMMARY_FIELDS)
    write_json(args.out_dir / "library_access_metadata.json", metadata)
    print(f"wrote {args.out_dir / 'origin_travel_times.csv'} ({len(origin_rows)} rows)")
    print(f"wrote {args.out_dir / 'library_catchments.csv'} ({len(catchment_rows)} rows)")
    print(f"wrote {args.out_dir / 'library_access_summary.csv'} ({len(summary_rows)} rows)")
    print(f"wrote {args.out_dir / 'library_access_metadata.json'}")


def build_ahmedabad_library_access() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    wards = ward_origins(WARDS)
    libraries = library_locations(LIBRARIES)
    stops = transit_stop_points(TRANSIT_STOPS)
    corridors = transit_corridors(ROUTE_CORRIDORS)
    library_stop_access = {
        library["library_id"]: nearest_stop_distance_m(float(library["longitude"]), float(library["latitude"]), stops)
        for library in libraries
    }

    origin_rows: list[dict[str, str]] = []
    for ward in wards:
        access = nearest_library_for_origin(ward, libraries)
        stop_m = nearest_stop_distance_m(ward["longitude"], ward["latitude"], stops)
        corridor_m = distance_to_corridors_m(ward["longitude"], ward["latitude"], corridors)
        transit_proxy = transit_proxy_minutes(ward, libraries, library_stop_access, stop_m)
        walk_minutes = access["walk_minutes"]
        best_proxy = min(walk_minutes, transit_proxy)
        origin_rows.append(
            {
                "ward_no": ward["ward_no"],
                "ward_name": ward["ward_name"],
                "population": str(round(ward["population"])),
                "centroid_latitude": f"{ward['latitude']:.7f}",
                "centroid_longitude": f"{ward['longitude']:.7f}",
                "nearest_library_id": access["library"]["library_id"],
                "nearest_library_name": access["library"]["name"],
                "distance_m_to_nearest_library": f"{access['distance_m']:.1f}",
                "walk_minutes_to_nearest_library": f"{walk_minutes:.1f}",
                "nearest_transit_stop_m": f"{stop_m:.1f}",
                "walk_minutes_to_nearest_transit_stop": f"{minutes_from_meters(stop_m):.1f}",
                "nearest_transit_corridor_m": f"{corridor_m:.1f}",
                "walk_minutes_to_nearest_transit_corridor": f"{minutes_from_meters(corridor_m):.1f}",
                "transit_proxy_minutes_to_nearest_library": f"{transit_proxy:.1f}",
                "best_walk_or_transit_proxy_minutes": f"{best_proxy:.1f}",
                "routing_tier": "ward_centroid_walk_and_transit_proxy",
                "confidence": "medium",
                "notes": (
                    "Ward centroid weighted by ward population_2020. Transit estimate is a proxy using nearest stop, "
                    "10 minute wait/transfer, straight-line in-vehicle distance adjusted by 1.35, and nearest stop at destination."
                ),
            }
        )

    catchment_rows = library_catchments(origin_rows)
    summary_rows = [summary_row(origin_rows, libraries, stops)]
    metadata = {
        "city": "ahmedabad",
        "model": "ward_centroid_walk_and_transit_proxy",
        "sources": {
            "wards": str(WARDS.relative_to(REPO)),
            "libraries": str(LIBRARIES.relative_to(REPO)),
            "transit_stops": str(TRANSIT_STOPS.relative_to(REPO)),
            "route_corridors": str(ROUTE_CORRIDORS.relative_to(REPO)),
        },
        "assumptions": {
            "walk_speed_kmph": WALK_SPEED_KMPH,
            "transit_speed_kmph": TRANSIT_SPEED_KMPH,
            "route_distance_factor": ROUTE_DISTANCE_FACTOR,
            "wait_and_transfer_minutes": WAIT_AND_TRANSFER_MINUTES,
            "population_origin": "ward centroid, weighted by layers/wards.geojson population_2020",
        },
        "limitations": [
            "This is not full scheduled routing.",
            "Raw GTFS trips/stop_times are not present on this branch.",
            "Ward centroid origins understate within-ward inequality and edge effects.",
        ],
    }
    return origin_rows, catchment_rows, summary_rows, metadata


def ward_origins(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for feature in data["features"]:
        props = feature.get("properties", {})
        lon, lat = centroid_of_geometry(feature["geometry"])
        population = float(props.get("population_2020") or 0)
        if population <= 0:
            continue
        rows.append(
            {
                "ward_no": str(props.get("ward_no") or ""),
                "ward_name": str(props.get("Name") or ""),
                "population": population,
                "latitude": lat,
                "longitude": lon,
            }
        )
    return rows


def library_locations(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    libraries = []
    for index, row in enumerate(rows, start=1):
        if not row.get("latitude") or not row.get("longitude"):
            continue
        libraries.append(
            {
                "library_id": f"ahmedabad_library_{index:03d}",
                "name": row.get("name", ""),
                "latitude": row["latitude"],
                "longitude": row["longitude"],
            }
        )
    if not libraries:
        raise ValueError("Ahmedabad library source has no coordinate rows")
    return libraries


def transit_stop_points(path: Path) -> list[tuple[float, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    points: set[tuple[float, float]] = set()
    for mode_rows in data.values():
        if not isinstance(mode_rows, list):
            continue
        for row in mode_rows:
            try:
                points.add((round(float(row["lon"]), 7), round(float(row["lat"]), 7)))
            except (KeyError, TypeError, ValueError):
                continue
    return sorted(points)


def transit_corridors(path: Path) -> list[list[list[float]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    corridors = []
    for agency_rows in data.values():
        if isinstance(agency_rows, list):
            corridors.extend(agency_rows)
    return corridors


def nearest_library_for_origin(origin: dict[str, Any], libraries: list[dict[str, str]]) -> dict[str, Any]:
    best_library = min(
        libraries,
        key=lambda library: haversine_m(origin["latitude"], origin["longitude"], library["latitude"], library["longitude"]),
    )
    distance = haversine_m(origin["latitude"], origin["longitude"], best_library["latitude"], best_library["longitude"])
    return {"library": best_library, "distance_m": distance, "walk_minutes": minutes_from_meters(distance)}


def nearest_stop_distance_m(lon: float, lat: float, stops: list[tuple[float, float]]) -> float:
    if not stops:
        return float("nan")
    return min(haversine_m(lat, lon, stop_lat, stop_lon) for stop_lon, stop_lat in stops)


def transit_proxy_minutes(
    origin: dict[str, Any],
    libraries: list[dict[str, str]],
    library_stop_access: dict[str, float],
    origin_stop_m: float,
) -> float:
    best = float("inf")
    for library in libraries:
        destination_stop_m = library_stop_access[library["library_id"]]
        direct_m = haversine_m(origin["latitude"], origin["longitude"], library["latitude"], library["longitude"])
        in_vehicle_m = direct_m * ROUTE_DISTANCE_FACTOR
        minutes = (
            minutes_from_meters(origin_stop_m)
            + WAIT_AND_TRANSFER_MINUTES
            + in_vehicle_m / (TRANSIT_SPEED_KMPH * 1000.0 / 60.0)
            + minutes_from_meters(destination_stop_m)
        )
        best = min(best, minutes)
    return best


def population_weighted_summary(rows: list[dict[str, str]], value_key: str) -> dict[str, str]:
    return {
        "p50": f"{weighted_quantile(rows, value_key, 'population', 0.50):.1f}",
        "p75": f"{weighted_quantile(rows, value_key, 'population', 0.75):.1f}",
        "p90": f"{weighted_quantile(rows, value_key, 'population', 0.90):.1f}",
        "within_10_pct": f"{threshold_share(rows, value_key, 'population', 10.0):.1f}",
        "within_15_pct": f"{threshold_share(rows, value_key, 'population', 15.0):.1f}",
        "within_20_pct": f"{threshold_share(rows, value_key, 'population', 20.0):.1f}",
        "within_30_pct": f"{threshold_share(rows, value_key, 'population', 30.0):.1f}",
        "within_45_pct": f"{threshold_share(rows, value_key, 'population', 45.0):.1f}",
    }


def summary_row(origin_rows: list[dict[str, str]], libraries: list[dict[str, str]], stops: list[tuple[float, float]]) -> dict[str, str]:
    walk = population_weighted_summary(origin_rows, "walk_minutes_to_nearest_library")
    transit_stop = population_weighted_summary(origin_rows, "walk_minutes_to_nearest_transit_stop")
    transit_corridor = population_weighted_summary(origin_rows, "walk_minutes_to_nearest_transit_corridor")
    transit_proxy = population_weighted_summary(origin_rows, "transit_proxy_minutes_to_nearest_library")
    best_proxy = population_weighted_summary(origin_rows, "best_walk_or_transit_proxy_minutes")
    population = sum(float(row["population"]) for row in origin_rows)
    return {
        "city": "ahmedabad",
        "origins": str(len(origin_rows)),
        "population": str(round(population)),
        "library_locations": str(len(libraries)),
        "coordinate_verified_locations": str(len(libraries)),
        "transit_stops": str(len(stops)),
        "routing_tier": "ward_centroid_walk_and_transit_proxy",
        "p50_minutes_to_nearest_library_walk": walk["p50"],
        "p75_minutes_to_nearest_library_walk": walk["p75"],
        "p90_minutes_to_nearest_library_walk": walk["p90"],
        "pct_population_within_10_min_walk": walk["within_10_pct"],
        "pct_population_within_15_min_walk": walk["within_15_pct"],
        "pct_population_within_20_min_walk": walk["within_20_pct"],
        "pct_population_within_30_min_walk": walk["within_30_pct"],
        "pct_population_within_45_min_walk": walk["within_45_pct"],
        "p50_minutes_to_nearest_transit_stop_walk": transit_stop["p50"],
        "p50_minutes_to_nearest_transit_corridor_walk": transit_corridor["p50"],
        "p50_minutes_to_nearest_library_transit_proxy": transit_proxy["p50"],
        "p50_minutes_to_nearest_library_best_proxy": best_proxy["p50"],
        "access_status": "computed_proxy",
        "confidence": "medium",
        "notes": "Ward population-weighted proxy model; not full scheduled transit routing.",
    }


def library_catchments(origin_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    aggregate: dict[str, dict[str, Any]] = defaultdict(lambda: {"name": "", "wards": 0, "population": 0.0})
    for row in origin_rows:
        bucket = aggregate[row["nearest_library_id"]]
        bucket["name"] = row["nearest_library_name"]
        bucket["wards"] += 1
        bucket["population"] += float(row["population"])
    return [
        {
            "library_id": library_id,
            "library_name": values["name"],
            "assigned_ward_count": str(values["wards"]),
            "assigned_population": str(round(values["population"])),
        }
        for library_id, values in sorted(aggregate.items(), key=lambda item: (-item[1]["population"], item[0]))
    ]


def centroid_of_geometry(geometry: dict[str, Any]) -> tuple[float, float]:
    polygons = polygon_rings(geometry)
    if not polygons:
        raise ValueError(f"unsupported geometry: {geometry.get('type')}")
    centroids = []
    for ring in polygons:
        centroid_lon, centroid_lat, area = ring_centroid(ring)
        if area:
            centroids.append((centroid_lon, centroid_lat, abs(area)))
    if not centroids:
        points = [point for ring in polygons for point in ring]
        return (sum(point[0] for point in points) / len(points), sum(point[1] for point in points) / len(points))
    total_area = sum(area for _, _, area in centroids)
    return (
        sum(lon * area for lon, _, area in centroids) / total_area,
        sum(lat * area for _, lat, area in centroids) / total_area,
    )


def polygon_rings(geometry: dict[str, Any]) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    if geometry["type"] == "MultiPolygon":
        return [polygon[0] for polygon in geometry["coordinates"]]
    return []


def ring_centroid(ring: list[list[float]]) -> tuple[float, float, float]:
    area2 = 0.0
    cx = 0.0
    cy = 0.0
    for start, end in zip(ring, ring[1:]):
        cross = start[0] * end[1] - end[0] * start[1]
        area2 += cross
        cx += (start[0] + end[0]) * cross
        cy += (start[1] + end[1]) * cross
    if area2 == 0:
        return 0.0, 0.0, 0.0
    return cx / (3.0 * area2), cy / (3.0 * area2), area2 / 2.0


def distance_to_corridors_m(lon: float, lat: float, corridors: list[list[list[float]]]) -> float:
    best = float("inf")
    for corridor in corridors:
        for start, end in zip(corridor, corridor[1:]):
            best = min(best, point_segment_distance_m(lon, lat, start[0], start[1], end[0], end[1]))
    return best


def point_segment_distance_m(lon: float, lat: float, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    coslat = math.cos(math.radians(lat))
    x = lon * coslat
    y = lat
    x1 = lon1 * coslat
    y1 = lat1
    x2 = lon2 * coslat
    y2 = lat2
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return haversine_m(lat, lon, lat1, lon1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    proj_lon = (x1 + t * dx) / coslat
    proj_lat = y1 + t * dy
    return haversine_m(lat, lon, proj_lat, proj_lon)


def minutes_from_meters(distance_m: float) -> float:
    return distance_m / (WALK_SPEED_KMPH * 1000.0 / 60.0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
