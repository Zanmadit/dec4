from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import folium
import dill
import pandas as pd
from model import RouteModel

df = pd.read_parquet("reconstructed.parquet")
app = FastAPI()

with open("route_model.pkl", "rb") as f:
    model: RouteModel = dill.load(f)


@app.get("/", response_class=HTMLResponse)
def form():
    return """
    <form method="post" action="/map">
        <input name="user_id" placeholder="Введите ID">
        <button type="submit">Показать карту</button>
    </form>
    """


@app.post("/map", response_class=HTMLResponse)
def show_map(user_id: str = Form(...)):
    try:
        user_id = int(user_id) 
    except ValueError:
        return f"<h3>Неверный формат ID: {user_id}</h3>"

    df_user = df[df["randomized_id"] == user_id]

    if df_user.empty:
        return f"<h3>Нет данных для ID {user_id}</h3>"

    m = folium.Map(
        location=[df_user["lat"].mean(), df_user["lng"].mean()],
        zoom_start=12
    )

    for _, row in df_user.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    return m._repr_html_()

