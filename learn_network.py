import json
from joblib import dump
import numpy as np
import pandas as pd
from math import log
from random import shuffle

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_squared_error

from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor

p_norm = [1.15, 1.15, 1.15, 1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.4]
p_target = 1.4


def ExpThScaler(data):
    for i in range(len(data)):
        norm = data[i].pop()
        for j in range(len(data[i])):
            x = (data[i][j] / norm - 1) * 100
            data[i][j] = (p_norm[j % 14] ** x - 1) / (p_norm[j % 14] ** x + 1)


with open('price_test.json', 'r') as json_file:
    price1 = json.load(json_file)
    ExpThScaler(price1)

with open('volume_test.json', 'r') as json_file:
    volume1 = json.load(json_file)

with open('target_up_test.json', 'r') as json_file:
    target_up1 = json.load(json_file)

with open('price.json', 'r') as json_file:
    price = json.load(json_file)
    ExpThScaler(price)

with open('volume.json', 'r') as json_file:
    volume = json.load(json_file)

with open('target_up.json', 'r') as json_file:
    target_up = json.load(json_file)

perm = [i for i in range(len(price))]
shuffle(perm)
price = [price[i] for i in range(len(perm))]
volume = [volume[i] for i in range(len(perm))]
target_up = [target_up[i] for i in range(len(perm))]

# Преобразование списков признаков в двумерный массив NumPy
X = np.column_stack([price, volume])
X1 = np.column_stack([price1, volume1])

# Преобразование списка целевого признака в одномерный массив NumPy
y_up = np.array(target_up)
y_up1 = np.array(target_up1)

# Разделение данных на обучающую и тестовую выборки
X_train_up, X_test_up, y_train_up, y_test_up = train_test_split(X, y_up, test_size=0.2, random_state=179)
eval_set = [(X1, y_up1), (X_train_up, y_train_up), (X_test_up, y_test_up)]

# Создание модели градиентного бустинга
# model = XGBRegressor(n_estimators=500, learning_rate=0.055, max_depth=11, early_stopping_rounds=5)
model = XGBRegressor(n_estimators=400, learning_rate=0.055, max_depth=3, early_stopping_rounds=5) # model for pr=3
# model = RandomForestRegressor(n_estimators=100, max_depth=10)


print("go")

# Обучение модели

model.fit(X_train_up, y_train_up, eval_set=eval_set)

predictions = model.predict(X_test_up)
mse = mean_squared_error(y_test_up, predictions)
print(f"RMSE: {mse ** 0.5}\n")

print("learned\n")

# Предсказание на тестовых данных
predictions_up = model.predict(X1)

# Оценка модели
mse_up = mean_squared_error(y_up1, predictions_up)
print("Mean Squared Error Up:", mse_up ** 0.5)

dump(model, 'model.joblib')
