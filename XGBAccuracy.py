from numpy import loadtxt
from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

dataset = loadtxt('treino.csv', delimiter=",")
X = dataset[:,1:15]
Y = dataset[:,16]

seed = 7
test_size = 0.33
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

model = XGBClassifier()
model.fit(X_train, y_train)

dataset2 = loadtxt('teste.csv', delimiter=",")
X_test = dataset2[:,1:15]
y_test = dataset2[:,16]

y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]

accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))