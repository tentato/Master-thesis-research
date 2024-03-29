from sklearn import metrics
from sklearn.multiclass import OneVsOneClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.svm import SVC
import numpy as np
from scipy.stats import ttest_rel
from tabulate import tabulate
print("")

# main_folder = 'results/KrzysztofJ_all/'
main_folder = 'results/MK/'

clfs = {
'GNB': GaussianNB(),
'SVM': SVC(),
'kNN': KNeighborsClassifier(),
}

filenames = ["features_MAV.csv","features_SSC.csv","features_VAR.csv","features_WL.csv","features_ZC.csv"]

file_object = open('results_ovo_kNN_MK.txt', 'w')

scores = []

for filename in filenames:
    file_object.write(f'{filename}\n')
    dataset = pd.read_csv(main_folder+filename, sep=",", decimal=".", header=None)
    X = dataset.iloc[:, 0:-1].values
    y = dataset.iloc[:, -1].values.astype(int)
    kfold = RepeatedStratifiedKFold(n_splits=5, n_repeats=2,random_state=11)
    splits = kfold.split(X,y)

    model = clfs['kNN']
    ovo = OneVsOneClassifier(model)

    mean_arr = []

    for n,(train_index,test_index) in enumerate(splits):
        x_train_fold, x_test_fold = X[train_index], X[test_index]
        y_train_fold, y_test_fold = y[train_index], y[test_index]
        ovo.fit(x_train_fold, y_train_fold)
        predict = ovo.predict(x_test_fold)
        mean_arr.append(metrics.accuracy_score(y_test_fold, predict))
    file_object.write(f'Score = {round(np.mean(mean_arr),2)}\n')

    scores.append(mean_arr)

print(scores)
file_object.write(f'{scores[0]}\n')
file_object.write(f'{scores[1]}\n')
file_object.write(f'{scores[2]}\n')

alfa = .05
t_statistic = np.zeros((len(filenames), len(filenames)))
p_value = np.zeros((len(filenames), len(filenames)))

for i in range(len(filenames)):
    for j in range(len(filenames)):
        t_statistic[i, j], p_value[i, j] = ttest_rel(scores[i], scores[j])
print("t-statistic:\n", t_statistic, "\n\np-value:\n", p_value)
file_object.write(f't-statistic:\n{t_statistic}\n\np-value:\n{p_value}')

headers = ["MAV", "SSC", "VAR", "WL", "ZC"]
names_column = np.array([["MAV"], ["SSC"], ["VAR"], ["WL"], ["ZC"]])
t_statistic_table = np.concatenate((names_column, t_statistic), axis=1)
t_statistic_table = tabulate(t_statistic_table, headers, floatfmt=".2f")
p_value_table = np.concatenate((names_column, p_value), axis=1)
p_value_table = tabulate(p_value_table, headers, floatfmt=".2f")
print("t-statistic:\n", t_statistic_table, "\n\np-value:\n", p_value_table)
file_object.write(f't-statistic:\n{t_statistic_table}\n\np-value:\n{p_value_table}')

advantage = np.zeros((len(filenames), len(filenames)))
advantage[t_statistic > 0] = 1
advantage_table = tabulate(np.concatenate(
    (names_column, advantage), axis=1), headers)
print("\n\nAdvantage:\n", advantage_table)
file_object.write(f'\n\nAdvantage:\n{advantage_table}\n')

significance = np.zeros((len(filenames), len(filenames)))
significance[p_value <= alfa] = 1
significance_table = tabulate(np.concatenate(
    (names_column, significance), axis=1), headers)
print("Statistical significance (alpha = 0.05):\n", significance_table)
file_object.write(f'\n\nStatistical significance (alpha = 0.05):\n{significance_table}\n')

stat_better = significance * advantage
stat_better_table = tabulate(np.concatenate(
    (names_column, stat_better), axis=1), headers)
print("Statistically significantly better:\n", stat_better_table)
file_object.write(f'\n\nStatistically significantly better:\n{stat_better_table}\n')

file_object.close()