import arrow
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

import slack
import skills
from utils import ArrowUtil, Skill, DataLoader


class Predictor(object):

    def __init__(self, n_neighbors=8):
        self.knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights='distance')

    def fit(self, data_x, data_y):
        self.knn.fit(data_x, data_y)

    def predict(self):
        data_loader = DataLoader()
        test_x = data_loader.make_X()

        predict = self.knn.predict(test_x)[0]
        confidence = max(self.knn.predict_proba(test_x)[0])
        description = " ".join(Skill.classes[predict])
        print(predict, confidence, description)

        if confidence >= 0.75:
            router = slack.MsgRouter()
            router.route(text=description)
        else:
            print("Skip. confidence is low.")
            functions = skills.Functions()
            functions.maxim_nietzsche()
