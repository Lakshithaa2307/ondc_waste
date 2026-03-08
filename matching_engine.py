import pandas as pd
from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def match_orders(farms, orders):

    if farms.empty or orders.empty:
        return pd.DataFrame()

    matches = []

    for _, order in orders.iterrows():

        available_farms = farms[
            (farms["crop"] == order["crop"]) &
            (farms["quantity"] > 0)
        ]

        if available_farms.empty:
            continue

        min_distance = float("inf")
        best_farm = None

        for _, farm in available_farms.iterrows():
            distance = haversine(
                farm["latitude"], farm["longitude"],
                order["latitude"], order["longitude"]
            )

            if distance < min_distance:
                min_distance = distance
                best_farm = farm

        if best_farm is not None:
            matches.append({
                "order_id": order["order_id"],
                "farm_id": best_farm["farm_id"],
                "distance_km": round(min_distance, 2),
                "order_lat": order["latitude"],
                "order_lon": order["longitude"],
                "farm_lat": best_farm["latitude"],
                "farm_lon": best_farm["longitude"],
            })

    return pd.DataFrame(matches)
