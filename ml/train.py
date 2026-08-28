import pandas as pd, numpy as np        # Imports pandas for handling tabular dataset structures and numpy for numerial array 
from sklearn.ensemble import RandomForestClassifier     # imports the Random Forest algorithm utilized for classifying security threat
from sklearn.model_selection import train_test_split, cross_val_score   # imports tools to split the data for training/testing and perform cross-validation.
from sklearn.metrics import classification_report       # imports metrics reporting tools to evaluate precision
from sklearn.preprocessing import StandardScaler        # imports the standard scaler to normalize feature values to zero mean
import joblib

FEATURES = ['altitude_m','airspeed_mps','vertical_speed','pitch_rad','roll_rad',
    'engine_rpm','thrust_n','fuel_flow_kgps','g_load',
    'thrust_speed_ratio','climb_thrust_ratio','seq_delta','fuel_per_thrust']
CLASSES = ['CLEAN','SPOOF','REPLAY','CORRUPT','DRIFT']      # Defines the 13 feature columns matching those generated 

df = pd.read_csv('ml/training_data.csv')    # loads the generated training dataset CSV file into pandas DataFrame
print(f'{len(df)} rows label distribution:\n{df["label"].value_counts()}')      # prints out the total row count and the distribution breakdown of labels to inspect data balance.

scaler = StandardScaler()   # initalizes the feature scaling utility
x = scaler.fit_transform(df[FEATURES].values)   # extracts the target ground-truth labels array.
y = df['label'].values

Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)    # splits the dataset into an 80% training set and a 20% testing set while preserving the class distribution

clf = RandomForestClassifier(
    n_estimators=300, max_depth=12, min_samples_leaf=2,
    class_weight='balanced',  # handles class imbalance
    n_jobs=-1, random_state=42)     # sets balanced class weights and utilizes all available CPU cores
clf.fit(Xtr, ytr)   # trains the Random Forest model using the training feature subset and labels.

print(classification_report(yte, clf.predict(Xte), target_names=CLASSES))   # outputs a detailed precision, recall, and F1-score evaluation report
cv = cross_val_score(clf, X, y, cv=5, scoring='f1_macro')       # performs a 5-fold cross validation using the macro F1 scoring metric
print(f'5-fold CV F1: {cv.mean():.3f} +/- {cv.std():.3f}')      # prints the mean and standard deviation of the cross validation F1 scores.

joblib.dump(clf,    'ml/classifier.pkl')    # serializes and saves the trained types of functions to specific file locations.
joblib.dump(scaler, 'ml/scaler.pkl')
print('Saved classifier.pkl and scaler.pkl')