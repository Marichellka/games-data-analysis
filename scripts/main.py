from pickle import dump
from scripts.cleansing import cleanse_data
from scripts.config import ASSET_PATH_PREDICTIONS_DUMP, ASSET_PATH_REGRESSIONS_DUMP, \
DATA_PATH_VGSALES, ASSET_PATH_RECOMMENDATIONS
from scripts.utils.dataset_scaler import DatasetScaler
from scripts.helpers import split_list, read_dataset
from scripts.regressions.helpers import get_regressions
from scripts.correlation.helpers import print_coor_matrix
from scripts.utils.regressions_analyzer import RegressionsAnalyzer
from scripts.utils.recommendation_system import RecommendationSystem

#TODO: create web API

# regressions
delete_cols = ["Rank", "Name", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]

dataset = read_dataset(DATA_PATH_VGSALES)

print("Dataset before cleansing:\n", dataset.describe())

dataset = cleanse_data(
    dataset,
    mode_columns=["Year"],
    float_columns=["Year"],
    delete_columns=delete_cols,
    sort_column="Global_Sales")

print("Dataset after cleansing:\n", dataset.describe())

y_cols, x_cols = split_list(list(dataset.columns), ["Global_Sales"])

dataset_scaler = DatasetScaler(dataset, x_cols)

regressions = list(get_regressions())

analyzer = RegressionsAnalyzer(dataset_scaler, regressions, x_cols, y_cols)

analyzer.run()

analyzer.dump_scores(ASSET_PATH_REGRESSIONS_DUMP)
analyzer.dump_predictions(ASSET_PATH_PREDICTIONS_DUMP)

print_coor_matrix(dataset_scaler.scaled_dataset)


# recommendations
x_cols = ["Platform", "Genre", "Publisher"]
dataset_scaler = DatasetScaler(dataset, x_cols)

recommendation = RecommendationSystem(dataset_scaler.scaled_dataset)
recommendation.build_system(x_cols)

test = dataset.iloc[[100]]
print(test[["Name"]+x_cols], '\n')
recommendations = recommendation.recommend(test, dataset)
with open(ASSET_PATH_RECOMMENDATIONS, 'w') as f:
    f.writelines(str(test[["Name"]+x_cols]))
    f.write('\n')
    f.writelines(str(recommendations[["Name"]+x_cols]))

