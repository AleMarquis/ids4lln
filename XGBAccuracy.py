from numpy import loadtxt
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve
from sklearn.utils import class_weight
from imblearn.over_sampling import SMOTE

# threshold = 0.1

dataset = loadtxt('treino.csv', delimiter=",")
X = dataset[:,1:14]
Y = dataset[:,15]

# sm = SMOTE(random_state=42)
# X, Y = sm.fit_resample(X, Y)

seed = 123456
test_size = 0.40
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)


classes_weights = class_weight.compute_sample_weight(
    class_weight='balanced',
    y=y_train
)

model = XGBClassifier(scale_pos_weight=5)

model.fit(X_train, y_train, sample_weight=classes_weights)

# dataset2 = loadtxt('teste.csv', delimiter=",")
# X_test = dataset2[:,1:14]
# y_test = dataset2[:,15]

# predictions = []
# y_pred = model.predict_proba(X_test)
# for value in y_pred:
#     if value[0] > threshold: predictions.append(0)
#     else: predictions.append(1)

y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]

accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
precision = precision_score(y_test, predictions)
print("Precision: %.2f%%" % (precision * 100.0))
recall = recall_score(y_test, predictions)
print("Recall: %.2f%%" % (recall * 100.0))
f1 = f1_score(y_test, predictions)
print("F1-Score: %.2f%%" % (f1 * 100.0))

cm = confusion_matrix(y_test, predictions, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)

disp.plot(cmap="Blues")

plt.show()
