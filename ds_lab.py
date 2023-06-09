# -*- coding: utf-8 -*-
"""DS_lab.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Iq54AQgpo6oi2g3h4dYY7RkKddYum50-
"""

!git clone https://github.com/BorealisAI/private-data-generation

!sh ./private-data-generation/data/download_datasets.sh nhanes

!python ./private-data-generation/preprocessing/preprocess_nhanes.py

"""# **Classification on the Churn dataset**"""

import pandas as pd
df=pd.read_csv("churn.csv")

df.head()

import pandas as pd
df_telco=pd.read_csv("churn.csv")

df_telco['TotalCharges'] = pd.to_numeric(df_telco['TotalCharges'], errors='coerce')

df_telco.dropna(inplace=True)

df_telco.drop(columns='customerID', inplace=True)

df_telco['PaymentMethod'] = df_telco['PaymentMethod'].str.replace(' (automatic)', '', regex=False)

df_telco_transformed = df_telco.copy()

# label encoding (binary variables)
label_encoding_columns = ['gender', 'Partner', 'Dependents', 'PaperlessBilling', 'PhoneService', 'Churn']

# encode categorical binary features using label encoding
for column in label_encoding_columns:
    if column == 'gender':
        df_telco_transformed[column] = df_telco_transformed[column].map({'Female': 1, 'Male': 0})
    else: 
        df_telco_transformed[column] = df_telco_transformed[column].map({'Yes': 1, 'No': 0})

one_hot_encoding_columns = ['MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 
                            'TechSupport', 'StreamingTV',  'StreamingMovies', 'Contract', 'PaymentMethod']

# encode categorical variables with more than two levels using one-hot encoding
df_telco_transformed = pd.get_dummies(df_telco_transformed, columns = one_hot_encoding_columns)

min_max_columns = ['tenure', 'MonthlyCharges', 'TotalCharges']

# scale numerical variables using min max scaler
for column in min_max_columns:
        # minimum value of the column
        min_column = df_telco_transformed[column].min()
        # maximum value of the column
        max_column = df_telco_transformed[column].max()
        # min max scaler
        df_telco_transformed[column] = (df_telco_transformed[column] - min_column) / (max_column - min_column)

# select independent variables
X = df_telco_transformed.drop(columns='Churn')

# select dependent variables
y = df_telco_transformed.loc[:, 'Churn']

# prove that the variables were selected correctly
print(X.columns)

# prove that the variables were selected correctly
print(y.name)

from scipy.stats import chi2_contingency
import numpy as np




def cramers_V(var1,var2) :
  crosstab =np.array(pd.crosstab(var1,var2, rownames=None, colnames=None)) # Cross table building
  stat = chi2_contingency(crosstab)[0] # Keeping of the test statistic of the Chi2 test
  obs = np.sum(crosstab) # Number of observations
  mini = min(crosstab.shape)-1 # Take the minimum value between the columns and the rows of the cross table
  return (stat/(obs*mini))

rows= []

for var1 in df_telco_transformed:
  col = []
  for var2 in df_telco_transformed :
    cramers =cramers_V(df_telco_transformed[var1], df_telco_transformed[var2]) # Cramer's V test
    col.append(round(cramers,2)) # Keeping of the rounded value of the Cramer's V  
  rows.append(col)
  
cramers_results = np.array(rows)
df = pd.DataFrame(cramers_results, columns = df_telco_transformed.columns, index =df_telco_transformed.columns)

import numpy as np
corrMatrix = df_telco_transformed.corr()


a_norm = np.linalg.norm(corrMatrix)

print(a_norm)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25,
                                                    random_state=40, shuffle=True)

from sklearn import metrics

# instantiate the model (using the default parameters)
logreg = LogisticRegression()
# Instantiate model with 1000 decision trees


# fit the model with data
logreg.fit(X_train,y_train)
pred_prob1 = logreg.predict_proba(X_test)

from sklearn.metrics import roc_auc_score

# auc scores
auc_score1 = roc_auc_score(y_test, pred_prob1[:,1])



print(auc_score1)

"""***RANDOM FOREST on Churn dataset.***"""

# Import the model we are using
from sklearn.ensemble import RandomForestClassifier
rf_model = RandomForestClassifier(n_estimators=50, max_features="auto", random_state=44)
# Train the model on training data
rf_model.fit(X_train, y_train);

predictions = rf_model.predict(X_test)

pred_prob2 = rf_model.predict_proba(X_test)

# auc scores
auc_score2 = roc_auc_score(y_test, pred_prob2[:,1])
print(auc_score2)

"""**NN**"""

from sklearn.neural_network import MLPClassifier

clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                     hidden_layer_sizes=(5, 2), random_state=1)

clf.fit(X_train,y_train)

pred_prob3 = clf.predict_proba(X_test)

auc_score3 = roc_auc_score(y_test, pred_prob3[:,1])
print(auc_score3)

"""# **Class on genretad Churn data**"""

!python ./private-data-generation/preprocessing/preprocess_churn.py

!python /content/private-data-generation/evaluate.py --target-variable='Churn' --train-data-path=./churn_processed_train.csv --test-data-path=./churn_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.01 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')
corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='Churn' --train-data-path=./churn_processed_train.csv --test-data-path=./churn_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.1 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='Churn' --train-data-path=./churn_processed_train.csv --test-data-path=./churn_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.25 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='Churn' --train-data-path=./churn_processed_train.csv --test-data-path=./churn_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.5  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='Churn' --train-data-path=./churn_processed_train.csv --test-data-path=./churn_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.75  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='Churn' --train-data-path=./churn_processed_train.csv --test-data-path=./churn_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=1  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

"""# **Classification on the Nhanes Real dataset**



"""

import pandas as pd
import numpy as np

train_set = pd.read_csv('/content/processed_train.csv')
test_set=pd.read_csv('/content/processed_test.csv')

nhanes_dataset=pd.concat([train_set,test_set])

nhanes_dataset=nhanes_dataset.dropna(axis=0)

feature_cols = ['DMDEDUC2_2.0', 'DMDEDUC2_3.0', 'DMDEDUC2_4.0', 'DMDEDUC2_5.0',
       'DMDEDUC2_7.0', 'DMDEDUC2_9.0', 'DMDEDUC2_nan', 'INDHHINC_2.0',
       'INDHHINC_3.0', 'INDHHINC_4.0', 'INDHHINC_5.0', 'INDHHINC_6.0',
       'INDHHINC_7.0', 'INDHHINC_8.0', 'INDHHINC_9.0', 'INDHHINC_10.0',
       'INDHHINC_11.0', 'INDHHINC_12.0', 'INDHHINC_13.0', 'INDHHINC_77.0',
       'INDHHINC_99.0', 'INDHHINC_nan', 'PAQ180_2.0', 'PAQ180_3.0',
       'PAQ180_4.0', 'PAQ180_9.0', 'PAQ180_nan', 'BPQ020_2.0', 'BPQ020_9.0',
       'BPQ020_nan', 'MCQ250A_2.0', 'MCQ250A_9.0', 'MCQ250A_nan',
       'RIAGENDR_2.0', 'RIAGENDR_nan', 'RIDRETH1_2.0', 'RIDRETH1_3.0',
       'RIDRETH1_4.0', 'RIDRETH1_5.0', 'RIDRETH1_nan', 'ALQ120Q', 'BMXBMI',
       'BMXHT', 'BMXWAIST', 'BMXWT', 'RIDAGEYR', 'SMD030']
X = nhanes_dataset[feature_cols] # Features
y = nhanes_dataset.status # Target variable

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25,random_state=0)
from sklearn.linear_model import LogisticRegression

from sklearn import metrics

# instantiate the model (using the default parameters)
logreg = LogisticRegression()
# Instantiate model with 1000 decision trees


# fit the model with data
logreg.fit(X_train,y_train)
pred_prob1 = logreg.predict_proba(X_test)

from sklearn.metrics import roc_curve

# roc curve for models
fpr1, tpr1, thresh1 = roc_curve(y_test, pred_prob1[:,1], pos_label=1)



# roc curve for tpr = fpr 
random_probs = [0 for i in range(len(y_test))]
p_fpr, p_tpr, _ = roc_curve(y_test, random_probs, pos_label=1)

from sklearn.metrics import roc_auc_score

# auc scores
auc_score1 = roc_auc_score(y_test, pred_prob1[:,1])



print(auc_score1)

"""**Random Forest**"""

from sklearn.ensemble import RandomForestClassifier
rf_model = RandomForestClassifier(n_estimators=50, max_features="auto", random_state=44)
# Train the model on training data
rf_model.fit(X_train, y_train);

predictions = rf_model.predict(X_test)

pred_prob2 = rf_model.predict_proba(X_test)
# auc scores
auc_score2 = roc_auc_score(y_test, pred_prob2[:,1])
print(auc_score2)

"""**NN**"""

from sklearn.neural_network import MLPClassifier

clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                     hidden_layer_sizes=(5, 2), random_state=1)
clf.fit(X_train,y_train)
pred_prob3 = clf.predict_proba(X_test)
auc_score3 = roc_auc_score(y_test, pred_prob3[:,1])
print(auc_score3)

import matplotlib.pyplot as plt
plt.style.use('seaborn')

# plot roc curves
plt.plot(fpr1, tpr1, linestyle='--',color='orange', label='Logistic Regression')

plt.plot(p_fpr, p_tpr, linestyle='--', color='blue')
# title
plt.title('ROC curve')
# x label
plt.xlabel('False Positive Rate')
# y label
plt.ylabel('True Positive rate')

plt.legend(loc='best')
plt.savefig('ROC',dpi=300)
plt.show();

"""# **Classification on Generated Dataset**

# **The main parametr is adding noise e. In that case we evaluate 7 epsilon value: 0.01, 0.1, 0.25,0.5,0.75,1,1.25**
"""

!python /content/private-data-generation/evaluate.py --target-variable='status' --train-data-path=./diabetes_data_train.csv --test-data-path=./diabetes_data_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.01 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='status' --train-data-path=./diabetes_data_train.csv --test-data-path=./diabetes_data_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.1 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='status' --train-data-path=./diabetes_data_train.csv --test-data-path=./diabetes_data_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.25 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='status' --train-data-path=./diabetes_data_train.csv --test-data-path=./diabetes_data_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.5  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='status' --train-data-path=./diabetes_data_train.csv --test-data-path=./diabetes_data_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.75  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python /content/private-data-generation/evaluate.py --target-variable='status' --train-data-path=./diabetes_data_train.csv --test-data-path=./diabetes_data_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=1  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/preprocessing/preprocess_adult.py

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

"""# **GiveSomeCredit Dataset- Real dataset**"""

!python ./private-data-generation/preprocessing/preprocess_givemesomecredit.py

import pandas as pd
train_set = pd.read_csv('/content/processed_train.csv')
test_set=pd.read_csv('/content/processed_test.csv')
nhanes_dataset=pd.concat([train_set,test_set])

nhanes_dataset.columns

feature_cols = ['RevolvingUtilizationOfUnsecuredLines', 'age',
       'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome',
       'NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate',
       'NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse',
       'NumberOfDependents']
X = nhanes_dataset[feature_cols] # Features
y = nhanes_dataset.SeriousDlqin2yrs # Target variable
from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25,random_state=0)
from sklearn.linear_model import LogisticRegression

from sklearn import metrics

# instantiate the model (using the default parameters)
logreg = LogisticRegression()
# Instantiate model with 1000 decision trees


# fit the model with data
logreg.fit(X_train,y_train)
pred_prob1 = logreg.predict_proba(X_test)

from sklearn.metrics import roc_curve

# roc curve for models
fpr1, tpr1, thresh1 = roc_curve(y_test, pred_prob1[:,1], pos_label=1)



# roc curve for tpr = fpr 
random_probs = [0 for i in range(len(y_test))]
p_fpr, p_tpr, _ = roc_curve(y_test, random_probs, pos_label=1)

from sklearn.metrics import roc_auc_score

# auc scores
auc_score1 = roc_auc_score(y_test, pred_prob1[:,1])



print(auc_score1)

"""**Random Forest**"""

from sklearn.ensemble import RandomForestClassifier
rf_model = RandomForestClassifier(n_estimators=50, max_features="auto", random_state=44)
# Train the model on training data
rf_model.fit(X_train, y_train);

predictions = rf_model.predict(X_test)

pred_prob2 = rf_model.predict_proba(X_test)
# auc scores
auc_score2 = roc_auc_score(y_test, pred_prob2[:,1])
print(auc_score2)

"""**NN**"""

from sklearn.neural_network import MLPClassifier

clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                     hidden_layer_sizes=(5, 2), random_state=1)
clf.fit(X_train,y_train)
pred_prob3 = clf.predict_proba(X_test)
auc_score3 = roc_auc_score(y_test, pred_prob3[:,1])
print(auc_score3)

corrMatrix = nhanes_dataset.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

"""# **GiveMe SomeCredit**"""

!python ./private-data-generation/evaluate.py --target-variable='SeriousDlqin2yrs' --train-data-path=./processed_train.csv --test-data-path=./processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.01  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='SeriousDlqin2yrs' --train-data-path=./processed_train.csv --test-data-path=./processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.1 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='SeriousDlqin2yrs' --train-data-path=./processed_train.csv --test-data-path=./processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.25 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='SeriousDlqin2yrs' --train-data-path=./processed_train.csv --test-data-path=./processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.5 --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='SeriousDlqin2yrs' --train-data-path=./processed_train.csv --test-data-path=./processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.75  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='SeriousDlqin2yrs' --train-data-path=./processed_train.csv --test-data-path=./processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=1  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

"""# **Logistic regression on Adult real dataset**"""

from sklearn.linear_model import LogisticRegression
# Import scikit_learn module to split the dataset into train.test sub-datasets
from sklearn.model_selection import train_test_split 
# Import scikit_learn module for k-fold cross validation
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
# import the metrics class
from sklearn import metrics
# import stats for accuracy 
import statsmodels.api as sm
import pandas as pd
import numpy as np

df=pd.read_csv("adult.csv")

salary_map = {'<=50K': 1, '>50K': 0}


df['native-country'] = df['native-country'].replace('?', np.nan)
df['workclass'] = df['workclass'].replace('?', np.nan)
df['occupation'] = df['occupation'].replace('?', np.nan)
df.dropna(how='any', inplace=True)

df.loc[df['native-country'] != 'United-States', 'native-country'] = 'Non-US'
df.loc[df['native-country'] == 'United-States', 'native-country'] = 'US'
df['native-country'] = df['native-country'].map({'US': 1, 'Non-US': 0}).astype(int)

df['marital-status'] = df['marital-status'].replace(['Divorced', 'Married-spouse-absent', 'Never-married', 'Separated',
                                                     'Widowed'], 'Single')
df['marital-status'] = df['marital-status'].replace(['Married-AF-spouse', 'Married-civ-spouse'], 'Couple')
df['marital-status'] = df['marital-status'].map({'Couple': 0, 'Single': 1})
rel_map = {'Unmarried': 0, 'Wife': 1, 'Husband': 2, 'Not-in-family': 3, 'Own-child': 4, 'Other-relative': 5}
df['relationship'] = df['relationship'].map(rel_map)

df['race'] = df['race'].map({'White': 0, 'Amer-Indian-Eskimo': 1, 'Asian-Pac-Islander': 2, 'Black': 3, 'Other': 4})


def f(x):
    if x['workclass'] == 'Federal-gov' or x['workclass'] == 'Local-gov' or x['workclass'] == 'State-gov':
        return 'govt'
    elif x['workclass'] == 'Private':
        return 'private'
    elif x['workclass'] == 'Self-emp-inc' or x['workclass'] == 'Self-emp-not-inc':
        return 'self_employed'
    else:
        return 'without_pay'


df['employment_type'] = df.apply(f, axis=1)
employment_map = {'govt': 0, 'private': 1, 'self_employed': 2, 'without_pay': 3}
df['employment_type'] = df['employment_type'].map(employment_map)
df.drop(labels=['workclass', 'education', 'occupation'], axis=1, inplace=True)

df.loc[(df['capital-gain'] > 0), 'capital-gain'] = 1
df.loc[(df['capital-gain'] == 0, 'capital-gain')] = 0
df.loc[(df['capital-loss'] > 0), 'capital-loss'] = 1
df.loc[(df['capital-loss'] == 0, 'capital-loss')] = 0

df.drop(['fnlwgt'], axis=1, inplace=True)

df.columns

feature_cols = ['age', 'educational-num', 'marital-status', 'relationship', 'race',
        'capital-gain', 'capital-loss', 'hours-per-week',
       'native-country', 'employment_type']
X = df[feature_cols] # Features
y = df.income # Target variable
from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25,random_state=0)
from sklearn.linear_model import LogisticRegression

from sklearn import metrics

# instantiate the model (using the default parameters)
logreg = LogisticRegression()
# Instantiate model with 1000 decision trees


# fit the model with data
logreg.fit(X_train,y_train)
pred_prob1 = logreg.predict_proba(X_test)

from sklearn.metrics import roc_curve





# roc curve for tpr = fpr 
random_probs = [0 for i in range(len(y_test))]
p_fpr, p_tpr, _ = roc_curve(y_test, random_probs, pos_label=1)

from sklearn.metrics import roc_auc_score

# auc scores
auc_score1 = roc_auc_score(y_test, pred_prob1[:,1])



print(auc_score1)

"""**Random Forest**"""

from sklearn.ensemble import RandomForestClassifier
rf_model = RandomForestClassifier(n_estimators=50, max_features="auto", random_state=44)
# Train the model on training data
rf_model.fit(X_train, y_train);

predictions = rf_model.predict(X_test)
pred_prob2 = rf_model.predict_proba(X_test)

auc_score2 = roc_auc_score(y_test, pred_prob2[:,1])
print(auc_score2)

"""**NN**"""

from sklearn.neural_network import MLPClassifier

clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                     hidden_layer_sizes=(5, 2), random_state=1)
clf.fit(X_train,y_train)
pred_prob3 = clf.predict_proba(X_test)
auc_score3 = roc_auc_score(y_test, pred_prob3[:,1])
print(auc_score3)

corrMatrix = df.corr()
a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

"""**Classification on the Generated Adult dataset**"""

!python ./private-data-generation/preprocessing/preprocess_adult.py

!python ./private-data-generation/evaluate.py --target-variable='income' --train-data-path=./adult_processed_train.csv --test-data-path=./adult_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.01  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='income' --train-data-path=./adult_processed_train.csv --test-data-path=./adult_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.1  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='income' --train-data-path=./adult_processed_train.csv --test-data-path=./adult_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.25  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='income' --train-data-path=./adult_processed_train.csv --test-data-path=./adult_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.5  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='income' --train-data-path=./adult_processed_train.csv --test-data-path=./adult_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=0.75  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

!python ./private-data-generation/evaluate.py --target-variable='income' --train-data-path=./adult_processed_train.csv --test-data-path=./adult_processed_test.csv --normalize-data dp-wgan --enable-privacy --sigma=0.8 --target-epsilon=1  --save-synthetic --output-data-path=/content/private-data-generation/data

data_encoded=pd.read_csv('/content/private-data-generation/data/synthetic_data.csv')

corrMatrix = data_encoded.corr()

a_norm = np.linalg.norm(corrMatrix)
print(a_norm)

"""# **DataSynthesizer Usage**"""

from DataSynthesizer.DataDescriber import DataDescriber
from DataSynthesizer.DataGenerator import DataGenerator
from DataSynthesizer.ModelInspector import ModelInspector
from DataSynthesizer.lib.utils import read_json_file, display_bayesian_network

import pandas as pd

!pip install DataSynthesizer

# input dataset
input_data = '/content/churn.csv'
# location of two output files
mode = 'correlated_attribute_mode'
description_file = '/content/description.json'
synthetic_data = '/content/sythetic_data.csv'

# An attribute is categorical if its domain size is less than this threshold.
# Here modify the threshold to adapt to the domain size of "education" (which is 14 in input dataset).
threshold_value = 20

# specify categorical attributes
categorical_attributes = {'education': True}

# specify which attributes are candidate keys of input dataset.
candidate_keys = {'ssn': True}

# A parameter in Differential Privacy. It roughly means that removing a row in the input dataset will not 
# change the probability of getting the same output more than a multiplicative difference of exp(epsilon).
# Increase epsilon value to reduce the injected noises. Set epsilon=0 to turn off differential privacy.
epsilon = 1

# The maximum number of parents in Bayesian network, i.e., the maximum number of incoming edges.
degree_of_bayesian_network = 2

# Number of tuples generated in synthetic dataset.
num_tuples_to_generate = 1000 # Here 32561 is the same as input dataset, but it can be set to another number.

describer = DataDescriber(category_threshold=threshold_value)
describer.describe_dataset_in_correlated_attribute_mode(dataset_file=input_data, 
                                                        epsilon=epsilon, 
                                                        k=degree_of_bayesian_network,
                                                        attribute_to_is_categorical=categorical_attributes,
                                                        attribute_to_is_candidate_key=candidate_keys)
describer.save_dataset_description_to_file(description_file)

display_bayesian_network(describer.bayesian_network)

generator = DataGenerator()
generator.generate_dataset_in_correlated_attribute_mode(num_tuples_to_generate, description_file)
generator.save_synthetic_data(synthetic_data)

# Read both datasets using Pandas.
input_df = pd.read_csv(input_data, skipinitialspace=True)
synthetic_df = pd.read_csv(synthetic_data)
# Read attribute description from the dataset description file.
attribute_description = read_json_file(description_file)['attribute_description']

inspector = ModelInspector(input_df, synthetic_df, attribute_description)

for attribute in synthetic_df.columns:
    inspector.compare_histograms(attribute)

inspector.mutual_information_heatmap()

# input dataset
input_data = '/content/adult.csv'
mode = 'correlated_attribute_mode'
description_file = '/content/description.json'
synthetic_data = '/content/sythetic_data.csv'

describer = DataDescriber(category_threshold=threshold_value)
describer.describe_dataset_in_correlated_attribute_mode(dataset_file=input_data, 
                                                        epsilon=epsilon, 
                                                        k=degree_of_bayesian_network,
                                                        attribute_to_is_categorical=categorical_attributes,
                                                        attribute_to_is_candidate_key=candidate_keys)
describer.save_dataset_description_to_file(description_file)

generator = DataGenerator()
generator.generate_dataset_in_correlated_attribute_mode(num_tuples_to_generate, description_file)
generator.save_synthetic_data(synthetic_data)

# Read both datasets using Pandas.
input_df = pd.read_csv(input_data, skipinitialspace=True)
synthetic_df = pd.read_csv(synthetic_data)
# Read attribute description from the dataset description file.
attribute_description = read_json_file(description_file)['attribute_description']

inspector = ModelInspector(input_df, synthetic_df, attribute_description)

for attribute in synthetic_df.columns:
    inspector.compare_histograms(attribute)

inspector.mutual_information_heatmap()

