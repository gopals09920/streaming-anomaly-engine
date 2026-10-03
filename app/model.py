class AnomalyModel:
    def __init__(self):
        pass

    def predict(self, amount: float, velocity: int) -> float:
        score = (amount * 0.001) + (velocity * 0.1)
        return float(min(score, 1.0))

model = AnomalyModel()