# prepare_model.py
import math
import pandas as pd
import numpy as np
import dill
from shapely.geometry import LineString

# -------------------
# Haversine расстояние
# -------------------
def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# -------------------
# Интерполяция сегмента
# -------------------
def interpolate_segment(p1, p2, step_m=500.0):
    lat1, lon1 = float(p1['lat']), float(p1['lng'])
    lat2, lon2 = float(p2['lat']), float(p2['lng'])
    dist = haversine_m(lat1, lon1, lat2, lon2)
    if dist == 0:
        return [dict(p1)]
    n_steps = max(1, int(dist // step_m))
    points = []
    for i in range(n_steps):
        t = i / n_steps
        lat = lat1 + (lat2 - lat1) * t
        lon = lon1 + (lon2 - lon1) * t
        points.append({'lat': lat, 'lng': lon, 'is_interpolated': True})
    return points

# -------------------
# Восстановление маршрутов
# -------------------
def reconstruct_paths(df, id_col='randomized_id', step_m=500.0):
    out_rows = []
    for gid, grp in df.groupby(id_col):
        grp = grp.reset_index(drop=True)
        if grp.shape[0] == 1:
            out_rows.append({
                'randomized_id': gid,
                'lat': grp.loc[0,'lat'],
                'lng': grp.loc[0,'lng'],
                'is_interpolated': False
            })
            continue
        for i in range(len(grp)-1):
            p1, p2 = grp.loc[i], grp.loc[i+1]
            seg = interpolate_segment(p1, p2, step_m=step_m)
            out_rows.extend([{
                'randomized_id': gid,
                'lat': pt['lat'],
                'lng': pt['lng'],
                'is_interpolated': True
            } for pt in seg])
        out_rows.append({
            'randomized_id': gid,
            'lat': grp.loc[len(grp)-1,'lat'],
            'lng': grp.loc[len(grp)-1,'lng'],
            'is_interpolated': False
        })
    return pd.DataFrame(out_rows)

# -------------------
# Модель маршрутов
# -------------------
class RouteModel:
    def __init__(self, reconstructed_df):
        self.reconstructed = reconstructed_df
        # заранее группируем по id
        self.routes = {
            gid: grp[['lat', 'lng']].values.tolist()
            for gid, grp in reconstructed_df.groupby('randomized_id')
        }

    def get_coords(self, route_id):
        return self.routes.get(route_id, [])

reconstructed = reconstruct_paths(df, step_m=500.0)

# -------------------
# 2. Создаём и сохраняем модель
# -------------------
model = RouteModel(reconstructed)

with open("route_model.pkl", "wb") as f:
    dill.dump(model, f)

print("✅ Модель сохранена в route_model.pkl")
