from numpy import loadtxt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve
from sklearn.utils import class_weight
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm

    # dataset2 = loadtxt('teste.csv', delimiter=",")
    # X_test = dataset2[:,[3, 4, 7, 8, 9, 14]]
    # X_test = dataset2[:,1:14]
    # y_test = dataset2[:,15]

df = pd.read_csv('treino.csv')

print(df['classification'].value_counts(normalize=True))

droplist = []
droplist.append([0, 15])
droplist.append([0, 1, 2, 5, 6, 10, 11, 12, 13, 15])
droplist.append([0, 3, 4, 7, 8, 9, 14, 15])

dropist_name = ['Full Data', 'Network Data', 'Operational Data']

seed = 414251
test_size = 0.33
train, test = train_test_split(df, test_size=test_size, random_state=seed)

results = pd.DataFrame(columns=['Data', 'Classifier', 'Accuracy', 'Precision', 'Recall', 'F1-Score'])

for k in range (len(droplist)):

    X_train = train.drop(train.columns[droplist[k]], axis=1)
    X_test  = test.drop(train.columns[droplist[k]], axis=1)

    columns = X_train.columns.tolist()
    corr = X_train.corr()
    correlated_vars = []
    for i in range(len(columns) - 1):
        for j in range(i+1, len(columns)):
            if corr[columns[i]][columns[j]] > 0.98:
                print(columns[i], columns[j], corr[columns[i]][columns[j]])
                correlated_vars.append(columns[j])
    X_train = X_train.drop(columns=correlated_vars)
    X_test  = X_test.drop(columns=correlated_vars)
    
    y_train = train.iloc[:,15]
    y_test  = test.iloc[:,15]




    modelXGB = XGBClassifier()
    modelXGB.fit(X_train, y_train)

    modelRF = RandomForestClassifier(random_state=0)
    modelRF.fit(X_train, y_train)

    modelDT = DecisionTreeClassifier()
    modelDT.fit(X_train, y_train)

    modelLR = LinearRegression()
    modelLR.fit(X_train, y_train)

    modelKNN = KNeighborsClassifier()
    modelKNN.fit(X_train, y_train)

    modelSVM = svm.SVC()
    modelSVM.fit(X_train, y_train)

    models = []
    models.append(modelXGB)
    models.append(modelRF)
    models.append(modelDT)
    models.append(modelLR)
    models.append(modelKNN)
    models.append(modelSVM)

    print(X_train)
    
    for obj in models:

        y_pred = obj.predict(X_test)
        predictions = [round(value) for value in y_pred]
        
        row = []

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        
        row.append(dropist_name[k])
        row.append(type(obj))
        row.append(accuracy * 100.0)
        row.append(precision * 100.0)
        row.append(recall * 100.0)
        row.append(f1 * 100.0)
        results.loc[len(results)] = row

print(results)
# cm = confusion_matrix(y_test, predictions, labels=modelXGB.classes_)
# disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=modelXGB.classes_)
# disp.plot(cmap="Blues")
# plt.show()
