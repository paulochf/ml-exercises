
import pandas as pd
import numpy as np
import argparse
import helpers
from sklearn import cross_validation
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

# Block parse script args
ap = argparse.ArgumentParser()
ap.add_argument('--seed', help='random seed', default=11, type=int)
ap.add_argument('--summary', help='show data summaries', action='store_true')
ap.add_argument('--tuning', help='do algorithm tuning', action='store_true')
args = vars(ap.parse_args())
seed = args['seed']

# Block: seed numpy random generator
np.random.seed(seed)

# Block: get data
df, Xtrn, Xval, Ytrn, Yval = helpers.get_train_data(seed=seed)
_, Xtest = helpers.get_test_data()

# Block: some descriptive statistics
# Correlation matrix, looks like the majority of variables are not significantly correlated.
if args['summary']:
    corr = df.corr()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(corr, vmin=-1, vmax=1, interpolation='none')
    fig.colorbar(cax)
    plt.suptitle('Correlation matrix')
    plt.savefig('tmp-correlation-matrix.png')

    # Block: data types - all integers
    print(df.dtypes)

    # Classification count - 2160 of each
    print(df.groupby('Cover_Type').size())

# Block: Spot-checking ensemble methods
scoring = 'accuracy'
names = []
results = []
estimators = []
scaler = ('Scaler', StandardScaler())
models = [
    ('LogisticRegression', LogisticRegression()),
    ('LinearDiscriminantAnalysis', LinearDiscriminantAnalysis()),
    ('KNeighborsClassifier', KNeighborsClassifier()),
    ('DecisionTreeClassifier', DecisionTreeClassifier()),
    ('GaussianNB', GaussianNB()),
    ('SVC', SVC()),
    ('AdaBoost', AdaBoostClassifier()),
    ('GradientBoosting', GradientBoostingClassifier()),
    ('RandomForest', RandomForestClassifier()),
    ('ExtraTrees', ExtraTreesClassifier())
]
pipelines = []
for name, model in models:
    pipelines.append(('Scaled' + name, Pipeline([scaler, (name, model)])))

for name, pipeline in pipelines:
    kfold = cross_validation.KFold(n=len(Xtrn),n_folds=10)
    cvres = cross_validation.cross_val_score(pipeline,Xtrn,Ytrn,cv=kfold,scoring=scoring)
    results.append(cvres)
    names.append(name)
    estimators.append(pipeline)
    print("%s: %f, %f" % (name, cvres.mean(), cvres.std()))

# Block: Evaluate holdout data with each of the ensembles
for name, estimator in zip(names, estimators):
    estimator.fit(Xtrn,Ytrn)
    predictions = estimator.predict(Xtest)
    fname = 'tmp-submission-' + name + '.csv'
    print("Saving predictions to %s" % (fname))
    helpers.create_submission(predictions, submissionfname=fname)
