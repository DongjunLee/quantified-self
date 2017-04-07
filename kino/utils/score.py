
class Score(object):

    def __init__(self):
        pass

    def percent(self, point, max_point, threshold):
        if point >= threshold:
            score = max_point
        else:
            score = (max_point * (point / threshold))
        return score
