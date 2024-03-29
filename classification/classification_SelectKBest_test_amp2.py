import time
import os
import numpy as np
import pandas as pd
import problexity as px
from tabulate import tabulate
from scipy.stats import ttest_rel
from itertools import combinations
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.multiclass import OneVsOneClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


start_time = time.time()
print("")
# main_folder = 'dataset_features/amp2_2_wavdec/'
main_folder = 'dataset_features/amp2_wavdec/'
filename = "features_WL_ZC_VAR_MAV_SSC.csv"

filenames = os.listdir(main_folder)
classes = [1,2,3,4,5,6]
number_of_classes = len(classes)

list_combinations_classes = list()
for n in range(2, len(classes) + 1):
    list_combinations_classes += list(combinations(classes, n))
list_combinations_classes = list_combinations_classes[::-1] # reverse tuple

file_object = open(f'{main_folder}results_Select_K_Best.txt', 'w')
file_object.write(f'Class combination;Number of classes;K worst features rejected;Mean Accuracy;Worst features labels')  
target_accuracy = 0.6
size = 16 * 4 * 5 # 16 signals * 4 decomposition levels * 5 feature extraction methods = 320

model = RandomForestClassifier(random_state=11) 
scaler = MinMaxScaler()

scores = []
mean_scores = []

dataset = pd.read_csv(f"{main_folder}{filename}", sep=",", decimal=".", header=0)
X_df = dataset.iloc[:, 0:-1]
y_df = dataset.iloc[:, -1]
X_scaled = scaler.fit_transform(X_df)
X_df = pd.DataFrame(X_scaled, columns=dataset.columns[:-1])
dataset = pd.concat([X_df, y_df], axis=1)

fig = plt.figure(figsize=(7,7))

for idx, class_combination in enumerate(list_combinations_classes):
    for k in range(0, size):
        print(f"K: {k}")
        method_val = []
        mean_method_val = []

        subdataset = dataset[dataset.iloc[:, -1].isin(class_combination)]

        X = subdataset.iloc[:, 0:-1].values
        y = subdataset.iloc[:, -1].values.astype(int)

        # remove k worst features
        X_new = SelectKBest()
        new_X = X_new.fit_transform(X, y)
        indexes_list = np.argpartition(X_new.scores_, k)
        worst_features_indexes = indexes_list[:k]
        worst_features_labels = subdataset.columns[worst_features_indexes].to_list()
        X = np.delete(X, worst_features_indexes,1)  # after removing worst features

        # Begin problexity
        strategy = "ova"
        cc = px.ComplexityCalculator(multiclass_strategy=strategy)

        # Fit model with data
        cc.fit(X,y)
        print(f"Report: \n{cc.report()}\n")
        cc.plot(fig, (1,1,1))

        plt.tight_layout()
        plt.savefig(f"problexity_results/problexity_{strategy}_({','.join(map(str, class_combination))})_k={k}.png")

        # End problexity

        kfold = RepeatedStratifiedKFold(n_splits=2, n_repeats=5,random_state=11)
        splits = kfold.split(X,y)

        ova = OneVsRestClassifier(model)

        balanced_accuraccy_array = []
        for n,(train_index,test_index) in enumerate(splits):
            x_train_fold, x_test_fold = X[train_index], X[test_index]
            y_train_fold, y_test_fold = y[train_index], y[test_index]
            ova.fit(x_train_fold, y_train_fold)
            predict = ova.predict(x_test_fold)

            ###Evaluating Prediction Accuracy
            if round(metrics.balanced_accuracy_score(y_test_fold, predict),2) < target_accuracy:
                print("RFC Acc: ",round(metrics.balanced_accuracy_score(y_test_fold, predict),2))
                # file_object.write(f'\n{str(class_combination)};{len(class_combination)};{k};{target_accuracy};{" ".join(worst_features_labels)}')
                break
            print("RFC Acc: ",round(metrics.balanced_accuracy_score(y_test_fold, predict),2))
            balanced_accuraccy_array.append(round(metrics.balanced_accuracy_score(y_test_fold, predict),2))
        if len(balanced_accuraccy_array) > 0:
            file_object.write(f'\n{str(class_combination)};{len(class_combination)};{k};{round(np.mean(balanced_accuraccy_array),2)};{" ".join(worst_features_labels)}')  
    # break #just for first combination (all classes)

end_time = time.time()
print(f"Execution time: {round((end_time-start_time)/60,2)} minutes")
file_object.close()
exit()

alfa = .05
# print(f'test: {scores[0]}')

for k in range(0,16):
    file_object.write(f'\n\n############ k = {16-k}\n')
    score = scores[k]
    t_statistic = np.zeros((len(filenames), len(filenames)))
    p_value = np.zeros((len(filenames), len(filenames)))

    for i in range(len(filenames)):
        for j in range(len(filenames)):
            t_statistic[i, j], p_value[i, j] = ttest_rel(score[i], score[j])
    # print("\n\nt-statistic for k = {k}\n", t_statistic, "\n\np-value:\n", p_value)
    # file_object.write(f'\n\nt-statistic for k = {k}\n{t_statistic}\n\np-value:\n {p_value}')

    headers = ["MAV", "SSC", "VAR", "WL", "ZC"]
    names_column = np.array([["MAV"], ["SSC"], ["VAR"], ["WL"], ["ZC"]])
    t_statistic_table = np.concatenate((names_column, t_statistic), axis=1)
    t_statistic_table = tabulate(t_statistic_table, headers, floatfmt=".2f")
    p_value_table = np.concatenate((names_column, p_value), axis=1)
    p_value_table = tabulate(p_value_table, headers, floatfmt=".2f")
    # print("t-statistic:\n", t_statistic_table, "\n\np-value:\n", p_value_table)
    # file_object.write(f't-statistic:\n{t_statistic_table}\n\np-value:\n{p_value_table}')

    advantage = np.zeros((len(filenames), len(filenames)))
    advantage[t_statistic > 0] = 1
    advantage_table = tabulate(np.concatenate(
        (names_column, advantage), axis=1), headers)
    # print("\n\nAdvantage:\n", advantage_table)
    # file_object.write(f'\n\nAdvantage:\n{advantage_table}\n')

    significance = np.zeros((len(filenames), len(filenames)))
    significance[p_value <= alfa] = 1
    significance_table = tabulate(np.concatenate(
        (names_column, significance), axis=1), headers)
    # print("Statistical significance (alpha = 0.05):\n", significance_table)
    # file_object.write(f'\n\nStatistical significance (alpha = 0.05):\n{significance_table}\n')

    stat_better = significance * advantage
    stat_better_table = tabulate(np.concatenate(
        (names_column, stat_better), axis=1), headers)
    # print("Statistically significantly better:\n", stat_better_table)
    file_object.write(f'\n\nStatistically significantly better:\n{stat_better_table}\n')
file_object.close()
