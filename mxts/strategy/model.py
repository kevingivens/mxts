from ray import serve
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


@serve.deployment
class BoostingModel:
    def __init__(self):
        self.model = LinearRegression()
        self._calibrate_model()

    def _calibrate_model(self):
        np.random.shuffle(data), 
        np.random.shuffle(target)
        train_x, train_y = data[:100], target[:100]
        
        # Train and evaluate models
        self.model.fit(train_x, train_y)


    async def __call__(self, data):
        # print("MSE:", mean_squared_error(model.predict(val_x), val_y))
        prediction = self.model.predict([data])[0]
        human_name = self.label_list[prediction]
        return {"result": human_name}