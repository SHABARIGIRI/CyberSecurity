# -*- coding: utf-8 -*-
"""CyberSecurity1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cbjl7t8dQiQytcvoL9MXzWe8Hkdno4hI

# Security Analysis for Book My Show

##**Importing Packages and Installations**
"""

# Commented out IPython magic to ensure Python compatibility.
!pip install pandas-profiling
# %matplotlib notebook
# %matplotlib inline
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas_profiling import ProfileReport
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn. neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import chi2
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from pprint import pprint
from sklearn.model_selection import RandomizedSearchCV

Data = pd.read_csv("dataset.csv")

# Profile=ProfileReport(DataX
# Profile.to_file("EDA_BookMyShow.html")

Data

Data.info()

"""##Exploratory Data Analysis"""

Data.isnull().sum()

Data_new=Data.iloc[:,1:]
Data_new.hist(figsize=(20,20))
plt.show()

pieces = []
for col in Data_new.columns:
    tmp_series = Data_new[col].value_counts()
    tmp_series.name = col
    pieces.append(tmp_series)
df_value_counts = pd.concat(pieces, axis=1)
df_value_counts

transposed_DataFrame = df_value_counts.T
transposed_DataFrame

transposed_DataFrame.plot(kind="bar",stacked = False, figsize = (25,10))

for cols in Data_new.columns:
    print("Feature {0} Unique Value {1}".format(cols,Data_new[cols].unique()))

x = Data_new.iloc[:,:-1]
y = Data_new[["Result"]]

X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=.3,random_state=0)

"""###Model Based feature Selection"""

rnd_clf = RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=42)
rnd_clf.fit(X_train.iloc[:,:], Y_train["Result"])
imp_features=[]
for name, importance in zip(X_train.columns, rnd_clf.feature_importances_):
  print(name, "=", importance)
  imp_features.append(name)
imp_features=imp_features[:25]

df_skb=X_train[imp_features]
df_test_skb=X_test[imp_features]

features = X_train.columns
importances = rnd_clf.feature_importances_
indices = np.argsort(importances)
plt.figure(figsize=(10,10))
plt.title('Feature Importances')
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [features[i] for i in indices])
plt.xlabel('Relative Importance')
plt.show()

"""###Correlation

"""

X_train.corr()

dfCorr = X_train.corr()
filteredDf = dfCorr[((dfCorr >= .7) | (dfCorr <= -.7)) & (dfCorr !=1.000)]
plt.figure(figsize=(30,10))
sns.heatmap(filteredDf, annot=True, cmap="Reds")
plt.show()

columns=np.full((dfCorr.shape[0],), True, dtype=bool)
for i in range(dfCorr.shape[0]):
  for j in range(i+1,dfCorr.shape[0]):
    if dfCorr.iloc[i,j]>=0.7:
      if columns[j]:
        columns[j] = False
corr_columns=X_train.columns[columns]
X_train=X_train[corr_columns]
X_train

df_skb=X_train
df_skb

df_test_skb=X_test[corr_columns]
df_test_skb

f_train=df_skb.values
l_train=Y_train.values.ravel()
f_test=df_test_skb.values
l_test=Y_test.values.ravel()

"""##Model Implementation

###Random Forest
"""

rf = RandomForestClassifier()
rf.fit(f_train, l_train)
rf.score(f_test,l_test)

# Look at parameters used by our current forest
print('Parameters currently in use:\n')
pprint(rf.get_params())

"""### Hyperparameter Tuning for RF (RandomSearchCV)"""

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 50, stop = 200, num = 5)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(3, 7, num = 10)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2,3,4]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
pprint(random_grid)

# Use the random grid to search for best hyperparameters
# First create the base model to tune
# Random search of parameters, using 3 fold cross validation, 
# search across 100 different combinations, and use all available cores
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)
# Fit the random search model
rf_random.fit(f_train, l_train)

rf_random.best_params_

rf_random = RandomForestClassifier(bootstrap= False, 
                            max_depth= None,
                            max_features= 'sqrt',
                            min_samples_leaf= 1,
                            min_samples_split = 3,
                            n_estimators = 125 )
rf_random.fit(f_train, l_train)
rf_random.score(f_test,l_test)

"""###Decision Tree"""

dt = DecisionTreeClassifier(random_state=0)
dt.fit(f_train, l_train)
dt.score(f_test,l_test)

"""###Logistic Regression"""

lr = LogisticRegression()
lr.fit(f_train, l_train)
lr.score(f_test,l_test)

"""###Support Vector Machines"""

svm = SVC(probability=True)
svm.fit(f_train,l_train)
svm.score(f_test,l_test)

"""###K Nearest Neighbors"""

kn = KNeighborsClassifier(n_neighbors=3)
kn.fit(f_train,l_train)
kn.score(f_test,l_test)

"""###Gradient Boosting"""

gb = GradientBoostingClassifier(learning_rate=0.1,n_estimators=100,max_depth=3,random_state=10)
gb.fit(f_train,l_train)
gb.score(f_test,l_test)

"""##Plotting ROC-AUC Curve"""

r_probs = [0 for _ in range(len(l_test))]
rf_probs = rf.predict_proba(f_test)
dt_probs = dt.predict_proba(f_test)
lr_probs = lr.predict_proba(f_test)
kn_probs = kn.predict_proba(f_test)
gb_probs = gb.predict_proba(f_test)
sv_probs = svm.predict_proba(f_test)

rf_probs = rf_probs[:, 1]
dt_probs = dt_probs[:, 1]
lr_probs = lr_probs[:, 1]
kn_probs = kn_probs[:, 1]
gb_probs = gb_probs[:, 1]
sv_probs = sv_probs[:, 1]

r_auc = roc_auc_score(l_test, r_probs)
rf_auc = roc_auc_score(l_test, rf_probs)
dt_auc = roc_auc_score(l_test, dt_probs)
lr_auc = roc_auc_score(l_test, lr_probs)
kn_auc = roc_auc_score(l_test, kn_probs)
gb_auc = roc_auc_score(l_test, gb_probs)
sv_auc = roc_auc_score(l_test, sv_probs)

print('Random (chance) Prediction: AUROC = %.3f' % (r_auc))
print('Random Forest: AUROC = %.3f' % (rf_auc))
print('Decision Tree: AUROC = %.3f' % (dt_auc))
print('Logistic Regression: AUROC = %.3f' % (lr_auc))
print('KNN: AUROC = %.3f' % (kn_auc))
print('Gradient Boosting: AUROC = %.3f' % (gb_auc))
print('SVC: AUROC = %.3f' % (sv_auc))

r_fpr, r_tpr, _ = roc_curve(l_test, r_probs)
rf_fpr, rf_tpr, _ = roc_curve(l_test, rf_probs)
dt_fpr, dt_tpr, _ = roc_curve(l_test, dt_probs)
lr_fpr, lr_tpr,_ = roc_curve(l_test, lr_probs)
kn_fpr, kn_tpr,_ = roc_curve(l_test, kn_probs)
gb_fpr, gb_tpr,_ = roc_curve(l_test, gb_probs)
sv_fpr, sv_tpr,_ = roc_curve(l_test, sv_probs)

plt.figure(figsize=(10, 10))
plt.plot(r_fpr, r_tpr, linestyle='--', label='Random prediction (AUROC = %0.3f)' % r_auc)
plt.plot(rf_fpr, rf_tpr, marker='.', label='Random Forest (AUROC = %0.3f)' % rf_auc)
plt.plot(dt_fpr, dt_tpr, marker='.', label='Decision Tree (AUROC = %0.3f)' % dt_auc)
plt.plot(lr_fpr, lr_tpr, marker='.', label='Logistic Regression (AUROC = %0.3f)' % lr_auc)
plt.plot(kn_fpr, kn_tpr, marker='.', label='KNN (AUROC = %0.3f)' % kn_auc)
plt.plot(gb_fpr, gb_tpr, marker='.', label='Gradient Boosting (AUROC = %0.3f)' % gb_auc)
plt.plot(sv_fpr, sv_tpr, marker='.', label='SV (AUROC = %0.3f)' % sv_auc)
# Title
plt.title('ROC Plot')
# Axis labels
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
# Show legend
plt.legend() # 
# Show plot
plt.show()

"""##K fold Cross-Validation (K=10, split= "Stratified")"""

def KFold_Validation(model,features,target):
    skfold = StratifiedKFold(n_splits = 10)
    results = cross_val_score(model,features,target,cv = skfold)
    #print("Accuracy for model {} is {} by using K-Fold cross-validation technique".format(model,results.mean()))
    return results.mean()

dict ={
       rf:'RandomForestClassifier(bootstrap= False,max_depth= None,max_features=sqrt,min_samples_leaf= 1,min_samples_split = 3,n_estimators = 125)',
       dt:'DecisionTreeClassifier(random_state=0)',
       lr:'LogisticRegression()',
       gb:'GradientBoostingClassifier(random_state=10)',
       kn:'KNeighborsClassifier(n_neighbors=3)',
       svm:'SVC(probability=True)'
      }
#list =[rf,dt,lr,gb,kn,svm]
list = [*dict]
kfoldModel_results=[]
model_results=[]
for l in list:
    val = KFold_Validation(l,f_train,l_train)
    value = l.score(f_test,l_test)
    model_results.append(value)
    kfoldModel_results.append(val)
# print(model_results)   
# print(kfoldModel_results)

names = ['RandomForestClassifier','DecisionTreeClassifier','LogisticRegression','GradientBoostingClassifier','KNeighborsClassifier','SupportVectorClassifier']

Final_Data = pd.DataFrame(np.column_stack([names,model_results,kfoldModel_results ,[*dict]]), 
                               columns=['Model_names', 'Model_results', 'Model_KfoldResults',"Parameters"])
Final_Data.index = np.arange(1, len(Final_Data) + 1)
Final_Data

import pickle
# open a file, where you ant to store the data
file = open('random_forest_regression_model.pkl', 'wb')

# dump information to that file
pickle.dump(rf_random, file)

!pip freeze > requirements.txt

