from collections import Counter
from sklearn.metrics import cohen_kappa_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
from sklearn.feature_selection import RFE
from scipy import stats
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score
from joblib import dump, load
import datetime as d
from math import sqrt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import xgboost as xgb
from xgboost import XGBClassifier
from xgboost import plot_importance
from sklearn import preprocessing
from sklearn.metrics import hamming_loss, f1_score
from matplotlib import cm
from sklearn.tree import DecisionTreeClassifier
import glob
import os
import geopandas as gp
import fiona
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict


#####ReadData

col1 = ["DisCity","DisRoad","DisWater","DisBuildig","Commercral_100","Commercral_1000","Commercral_500","Company_100","Company_1000","Company_500","Pubic_100","Pubic_500","Pubic_1000","Factory_1000","Factory_100","Factory_500",
        "Govement_100","Govement_500","Govement_1000","Hotel_100","Hotel_500","Hotel_1000","School_100","School_1000","School_500","Finance_100","Finance_500","Finance_1000","Hoptal_500","Hoptal_100","Hoptal_1000",
        "Restaurant_1000","Restaurant_100","Restaurant_500","Subdnsion_100","Subdnsion_1000","Subdnsion_500","Transport_1000","Transport_100","Transport_500","Urban_vilage_100", "Urban_vilage_500", "Urban_vilage_1000",  #Group2
      "Height","AREA_GEO","PERIM_GEO","PNT_COUNT","Compact","CookeJC","Fractality",#Group3
        'SurfaceA','Compact3D','ShapeIndex','Volume','HeightCoef','ID',
        "classify"]
data1 = pd.read_csv('E:/ChinaBuildingType_New/landform/Altai_Mountains_and_Tacheng_Basin.csv')
data1 = data1[col1]
y1 = data1['classify']
x1 = data1.iloc[:, 0:55]
print(y1.count(),Counter(y1))

best_i = None
best_p = -1
for i in range(20):
    train_x1, test_x1, train_y1, test_y1 = train_test_split(x1, y1, test_size=0.3, random_state=i)
    ks_result = stats.ks_2samp(test_y1, train_y1)
    p_value = ks_result[1]
    print(f"Random State: {i}, p-value: {p_value:.4f}")
    if p_value > best_p:
        best_p = p_value
        best_i = i
print(f"\nBest Random State: {best_i}, Best p-value: {best_p:.4f}")
print(y1.count(),Counter(y1))

train_x, X_temp, train_y, y_temp = train_test_split(x1, y1, test_size=0.3, random_state=18)
val_x, test_x, val_y, test_y = train_test_split(X_temp, y_temp, test_size=0.5, random_state=18)

param_dist = {
    'n_estimators': [i for i in range(50, 200,50)],
    'max_depth': [i for i in range(3, 10,1)],
    'learning_rate': [i for i in(0.01, 0.3,0.05,0.1,0.15,0.2,0.25)],
    'subsample': [i for i in (0.4,0.8,0.5,0.6,0.7)],
    'colsample_bytree': [i for i in (0.4,0.8,0.5,0.6,0.7)],
}
random_search = GridSearchCV(
    estimator=XGBClassifier(),
    param_grid=param_dist,
    scoring='accuracy',
    n_jobs=-1,
    cv=3,
    verbose=2,
)
random_search.fit(train_x, train_y)

# Evaluate the final model using the optimal parameters
best_xgb_model = random_search.best_estimator_
y_pred_best = best_xgb_model.predict( test_x)
final_accuracy = accuracy_score(test_y.argmax(axis=1), y_pred_best.argmax(axis=1))
print(f'Final Test Accuracy: {final_accuracy}')
print("Best parameters found: ", random_search.best_params_)

XGB_classifier = XGBClassifier(
    learning_rate=0.05,
    n_estimators=100,
    max_depth=8,
    min_child_weight=1,
    gamma=0.1,
    subsample=0.6,
    colsample_bytree=0.7,
    objective='multi:softmax',
    num_class=7,
    scale_pos_weight=1,
    reg_alpha=0.15,
    random_state=17,
    eval_metric='mlogloss',
)

XGB_classifier.fit(
    train_x, train_y,
    eval_set=[(val_x, val_y)],
    early_stopping_rounds=10,
    verbose=False
)
train_y_pred= XGB_classifier.predict(train_x)
test_y_pred = XGB_classifier.predict(test_x)
test_y_pred = np.array(test_y_pred)
print("XGBoost OA：", accuracy_score(test_y, test_y_pred))
kappa2 = cohen_kappa_score(test_y, test_y_pred)
ham_distance = hamming_loss(test_y, test_y_pred)
print("XGBoost kappa：", kappa2)
f1 = f1_score(test_y, test_y_pred, average='weighted')
print("XGBoost F1-score：", f1)
XGB_classifier.fit(
    train_x, train_y,
    eval_set=[(X_temp, y_temp)],
    early_stopping_rounds=10,
    verbose=False
)

dump(XGB_classifier,"E:/ChinaBuildingType_New/landform/South3.pkl")
full_model_file_name = 'E:/ChinaBuildingType_new/Model/South1.pkl'
XGB_classifier=load(full_model_file_name)
col4 = ["DisCity","DisRoad","DisWater","DisBuildig","Commercial_100","Commercial_1000","Commercial_500","Public_100","Public_500","Public_1000","Factory_1000","Factory_100","Factory_500",
        "Government_100","Government_500","Government_1000","Hotel_100","Hotel_500","Hotel_1000","Education_100","Education_1000","Education_500","Finance_100","Finance_500","Finance_1000","Hoptal_500","Hoptal_100","Hoptal_1000",
        "Restaurant_1000","Restaurant_100","Restaurant_500","Residential_100","Residential_500","Residential_1000","Transport_1000","Transport_100","Transport_500",
      "Height","AREA_GEO","PERIM_GEO","PNT_COUNT","Compact","CookeJC","Fractality",#Group3
        'SurfaceA','Compact3D','ShapeIndex','Volume','HeightCoef',"ID"]
directory_path = 'E:\\ChinaBuildingType_New\\csv\\South\\'
for filename in os.listdir(directory_path):
    if filename.endswith('_1.csv'):
        file_path = os.path.join(directory_path, filename)
        print(f'processing：{file_path}')
        filename = filename.replace('.csv', '')
        data_pre1 = pd.read_csv(file_path, error_bad_lines = False)
        data_pre1 = data_pre1[col4]
        x1_pre = data_pre1.iloc[:, 0:55]
        y1_pred = XGB_classifier.predict(x1_pre)
        data_pre1['class_pred'] = y1_pred
        col5=['ID','class_pred',"AREA_GEO","Height"]
        result = data_pre1[col5]
        result['ID'] = result['ID'].round().astype(int)
        y = result["class_pred"]
        print(Counter(y))
        result.to_csv('E:\\ChinaBuildingType_New\\csv\\South\\'+filename+'_result.csv', sep=',', index_label='fid', encoding='utf_8_sig')

def merge_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    files = [f for f in os.listdir(input_folder) if f.endswith('_result.csv')]
    prefix_groups = defaultdict(list)
    for file in files:
        prefix = '_'.join(file.split('_')[:-1])
        if prefix[-1].isdigit():
            prefix = prefix.rstrip('1234')
        prefix_groups[prefix].append(file)
    for prefix, file_list in prefix_groups.items():
        combined_df = pd.DataFrame()
        for file in file_list:
            file_path = os.path.join(input_folder, file)
            df = pd.read_csv(file_path)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        output_file = os.path.join(output_folder, f"{prefix}_result.csv")
        combined_df.to_csv(output_file, index=False)
        print(f"Finish: {output_file}")
input_folder = r"E:\\ChinaBuildingType_New\\csv\\South"
output_folder = r"E:\\ChinaBuildingType_New\\csv\\Merged"
merge_files(input_folder, output_folder)


inputfile = r'E:\\ChinaBuildingType\\Polygon.gdb'
output_gdb = r'E:\\ChinaBuildingType\\ChinaAll.gdb'
output_csv_folder = r'E:\\ChinaBuildingType\\csv\\Merged\\'
gdb_layers = gp.io.file.fiona.listlayers(inputfile)
for layer_name in gdb_layers:
    csv_path = os.path.join(output_csv_folder, f'{layer_name}_result.csv')
    if os.path.exists(csv_path):
        print(f"CSV found: {csv_path}")
        shp = gp.read_file(inputfile, layer=layer_name)
        print(f"Successfully read layer: {layer_name}")
        shp = shp[['Height', 'ID', 'geometry']]
        Type = pd.read_csv(csv_path)
        Type = Type[['ID', 'class_pred']]
        shp_with_Category = shp.merge(Type, on='ID', how='left')
        shp_with_Category = shp_with_Category.to_crs('EPSG:4326')
        print(shp_with_Category['class_pred'].value_counts(dropna=False))
        shp_with_Category = shp_with_Category.dropna(subset=['class_pred'])
        output_layer_name = f"{layer_name}_result"
        shp_with_Category.to_file(output_gdb, layer=output_layer_name)
        print(f"Done processing layer: {layer_name}")
print("Processing complete!")


##Feature Importance
features = list(x1.columns)
importances =XGB_classifier.feature_importances_
indices = np.argsort(importances)[::-1]
num_features = len(importances)
color_map = {}
group1 = ["DisCity", "DisRoad", "DisWater", "DisBuildig"]
group2 = ["Commercral_100","Commercral_1000","Commercral_500","Company_100","Company_1000","Company_500","Pubic_100","Pubic_500","Pubic_1000","Factory_1000","Factory_100","Factory_500",
        "Govement_100","Govement_500","Govement_1000","Hotel_100","Hotel_500","Hotel_1000","School_100","School_1000","School_500","Finance_100","Finance_500","Finance_1000","Hoptal_500","Hoptal_100","Hoptal_1000",
        "Restaurant_1000","Restaurant_100","Restaurant_500","Subdnsion_100","Subdnsion_1000","Subdnsion_500","Transport_1000","Transport_100","Transport_500","Urban_vilage_100", "Urban_vilage_500", "Urban_vilage_1000",]
group3 = ["Height","AREA_GEO","PERIM_GEO","PNT_COUNT","Compact","CookeJC","Fractality",'SurfaceA','Compact3D','ShapeIndex','Volume','HeightCoef']
for feature in features:
    if feature in group1:
        color_map[feature] = '#FFA07A'
    elif feature in group2:
        color_map[feature] = '#6495ED'
    elif feature in group3:
        color_map[feature] = '#B0E0E6'
my_colors = [color_map[features[i]] for i in indices]
plt.rcParams['font.sans-serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 13
plt.figure(figsize=(5, 8))
plt.title("Feature importances of Northwest", fontsize=20)
plt.barh(range(num_features), importances[indices], color=my_colors, align="center")
for i, v in enumerate(importances[indices][0:3]):
    plt.text(v - 0.025, i - 0.3, '%.2f' % (v * 100) + '%', color='black', fontweight='bold', fontsize=12)
plt.yticks(range(num_features), [features[i] for i in indices])
_xtick_labels = [i / 100 for i in range(5, 20, 5)]
plt.xticks(_xtick_labels)
plt.ylim([-1, num_features])
plt.subplots_adjust(top=0.9, bottom=0.3)
plt.show()

print(XGB_classifier.classes_)
classes = XGB_classifier.classes_
confusion = confusion_matrix(y_pred=test_y_pred, y_true=test_y)
true_counts = [(test_y == c).sum() for c in classes]
pred_counts = [(test_y_pred == c).sum() for c in classes]
cm_normalized = confusion.astype('float') / confusion.sum(axis=1)[:, np.newaxis]
print(cm_normalized)
def plot_confusion_matrix(cm, title='Confusion Matrix'):
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.get_cmap('GnBu'))
    plt.title(title,
        fontdict={'family': 'Times New Roman', 'size': 16, 'color': 'black', 'weight': 'bold'}
    )
    # ---- xticks (predicted) ----
    xtick_labels = [f"{cls}\n(n={cnt})" for cls, cnt in zip(classes, pred_counts)]
    plt.xticks(np.arange(len(classes)), xtick_labels,
               fontdict={'family': 'Arial', 'size': 10, 'color': 'black'},
               rotation=90, ha='center')
    ytick_labels = [f"{cls}\n (n={cnt})" for cls, cnt in zip(classes, true_counts)]
    plt.yticks(np.arange(len(classes)), ytick_labels,
               fontdict={'family': 'Arial', 'size': 10, 'color': 'black'})
    plt.ylabel('True label',
               fontdict={'family': 'Times New Roman', 'size': 12, 'color': 'black', 'weight': 'bold'})
    plt.xlabel('Predicted label',
               fontdict={'family': 'Times New Roman', 'size': 12, 'color': 'black', 'weight': 'bold'})
plt.figure(figsize=(6, 7), dpi=400)
ind_array = np.arange(len(classes))
x, y = np.meshgrid(ind_array, ind_array)
for x_val, y_val in zip(x.flatten(), y.flatten()):
    c = cm_normalized[y_val][x_val] * 100
    if c > 50:
        color = 'white'
    else:
        color = 'black'
    plt.text(x_val, y_val,
             f"{c:.1f}%",
             fontdict={'family': 'Times New Roman', 'size': 13,
                       'color': color},
             va='center', ha='center')
plt.grid(False)
plt.gca().set_xticks([])
plt.gca().set_yticks([])
plt.xticks(np.arange(len(classes)))
plt.yticks(np.arange(len(classes)))
plot_confusion_matrix(cm_normalized, title='Normalized confusion matrix in America')
plt.gcf().subplots_adjust(bottom=0.22)
plt.show()

