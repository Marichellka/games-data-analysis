from itertools import combinations
from numpy import ravel

from scripts.regressions.helpers import test_regressions, train_test_dataset_split
from scripts.utils.dataset_scaler import DatasetScaler

class RegressionsAnalyzer:

    def __init__(
        self,
        scaler : DatasetScaler,
        regressions : list,
        x_cols : list,
        y_cols : list) -> None:
        self.__regressions = regressions
        self.__original_dataset = scaler.original_dataset
        self.__dataset = scaler.scaled_dataset
        self.__x_cols = x_cols
        self.__y_cols = y_cols


    @property
    def raw_scores(self) -> dict:
        return self.__regressions_scores


    @property
    def raw_tests(self) -> dict:
        return self.__regressions_tests


    @property
    def best_model(self) -> dict:
        return self.__best_model


    def run(self) -> None:
        x_cols_combinations = []
        for length in range(1, len(self.__x_cols) + 1):
            for combination in combinations(self.__x_cols, length):
                x_cols_combinations.append(list(combination))

        self.__x_cols_combinations = x_cols_combinations

        scores, tests = self.get_regressions_scores(self.__x_cols_combinations)

        self.__regressions_scores = scores
        self.__regressions_tests = tests

        best_score = 0
        best_columns = None
        best_regression = None

        for i, regressions_scores in enumerate(self.__regressions_scores):
            for j, score in enumerate(regressions_scores):
                if (score > best_score):
                    best_columns = self.__x_cols_combinations[i % len(self.__x_cols_combinations)]
                    best_regression = self.__regressions[j]
                    best_score = score
        
        x_train, y_train, _, _ = \
                train_test_dataset_split(self.__dataset, best_columns, self.__y_cols)

        self.__best_x_combination = best_columns
        self.__best_model = best_regression.fit(x_train, ravel(y_train))


    def get_regressions_scores(self, x_cols_list : list) -> dict:
        regressions_tests = []
        for x_cols in x_cols_list:
            x_train, y_train, x_test, y_test = \
                train_test_dataset_split(self.__dataset, x_cols, self.__y_cols)
        
            fit_regressions = [regression.fit(x_train, ravel(y_train)) \
                for regression in self.__regressions]

            regressions_tests += list(test_regressions(fit_regressions, x_test, y_test))

        beneficial_funcs = [
            lambda x: [max(x) - value for value in x], # mean squared error
            lambda x: [value + abs(min(map(lambda el : el - 1, x))) - 1 for value in x] # r2_score
        ]
        raw_regressions_scores = self.evaluate_regressions_tests(regressions_tests, beneficial_funcs)
        regressions_scores = []
        
        regressions_count = len(self.__regressions)
        for idx in range(0, len(x_cols_list)):
            regressions_scores.append(raw_regressions_scores[regressions_count*idx:regressions_count*idx+regressions_count])

        return regressions_scores, regressions_tests


    # beneficial_funcs is a list of functions used to convert corresponding values into beneficial ones.
    # it is expected that the return value will be >= 0.
    def evaluate_regressions_tests(self, regressions_tests : list, beneficial_funcs : list) -> dict:
        beneficial_criterions_lists = \
            [beneficial_funcs[idx](test_values) \
                for idx, test_values in enumerate(list(map(list, zip(*regressions_tests))))]
        max_criterions_list = \
            [max(criterions) \
                for criterions in beneficial_criterions_lists]
        # worst == 0, best == number of criterions in regressions_tests
        regressions_scores = \
            [sum([beneficial_criterions_lists[i][j] / max_criterions_list[i] for i, _ in enumerate(test)]) \
                for j, test in enumerate(regressions_tests)]
        return regressions_scores


    def dump_scores(self, filename : str) -> None:
        with open(filename, "w") as text_file:
            for i, regressions_scores in enumerate(self.__regressions_scores):
                for j, score in enumerate(regressions_scores):
                    text_file.write(f"Combination: {self.__x_cols_combinations[i % len(self.__x_cols_combinations)]}\n")
                    text_file.write(f"Regression: {self.__regressions[j]}\n")
                    text_file.write(f"Score: {score}\n")
                    text_file.write(f"Raw scores: {self.__regressions_tests[i * len(self.__regressions) + j]}\n")
                    text_file.write("***\n")


    def dump_predictions(self, filename : str):
        with open(filename, "w") as text_file:
            text_file.write(f"Predictions for {self.__best_model}:\n")
            _, _, x_test, y_test = train_test_dataset_split(self.__dataset, self.__best_x_combination, self.__y_cols)
            predicted  = self.__best_model.predict(x_test)
            for idx in range(len(y_test)):
                text_file.write(f"Actual value: {y_test.iloc[idx][self.__y_cols]}\n")
                text_file.write(f"Predicted value: {predicted[idx]}\n")
                text_file.write(f"***\n")
