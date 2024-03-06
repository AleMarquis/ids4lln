from numpy import loadtxt
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve
from sklearn.utils import class_weight
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

dataset = loadtxt('treino.csv', delimiter=",")
X = dataset[:,1:14]
Y = dataset[:,15]

seed = 123456
test_size = 0.40
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)


classes_weights = class_weight.compute_sample_weight(
    class_weight='balanced',
    y=y_train
)

modelXGB = XGBClassifier(scale_pos_weight=5)
modelXGB.fit(X_train, y_train, sample_weight=classes_weights)

modelRF = RandomForestClassifier(random_state=0)
modelRF.fit(X_train, y_train)

modelKNN = KNeighborsClassifier()
modelKNN.fit(X_train, y_train)

# dataset2 = loadtxt('teste.csv', delimiter=",")
# X_test = dataset2[:,1:14]
# y_test = dataset2[:,15]

models = []
models.append(modelXGB)
models.append(modelRF)
models.append(modelKNN)

for obj in models:

    y_pred = obj.predict(X_test)
    predictions = [round(value) for value in y_pred]
    print(type(obj))
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))
    precision = precision_score(y_test, predictions)
    print("Precision: %.2f%%" % (precision * 100.0))
    recall = recall_score(y_test, predictions)
    print("Recall: %.2f%%" % (recall * 100.0))
    f1 = f1_score(y_test, predictions)
    print("F1-Score: %.2f%%" % (f1 * 100.0))

# cm = confusion_matrix(y_test, predictions, labels=modelXGB.classes_)
# disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=modelXGB.classes_)

# disp.plot(cmap="Blues")

# plt.show()
