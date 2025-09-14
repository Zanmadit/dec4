import pickle

class RouteModel:
    def __init__(self, df):
        self.df = df

    def get_routes_by_id(self, user_id: str):
        return self.df[self.df["id"] == user_id]

def save_model(model, filename="route_model.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(model, f)

def load_model(filename="route_model.pkl"):
    with open(filename, "rb") as f:
        return pickle.load(f)
