import pytz
from datetime import datetime

def get_latest_model_timestamp(project_key):
    """
    :param project_key: Datastore key object
    :return: Datetime object
    """
    return datetime.utcnow().replace(tzinfo=pytz.utc)

def get_model(project_key):
    """
    :param project_key: Datastore key object
    :return: Model object
    """

    class MockModel:
        def __init__(self):
            self.timestamp = datetime.utcnow().replace(tzinfo=pytz.utc)

        def predict(self, img):
            """
            :param img: PIL Image, RGB
            :return: ordered list of predictions
            """
            return [
                {'name': 'dog', 'value': 0.8},
                {'name': 'cat', 'value': 0.5},
                {'name': 'car', 'value': 0.1},
            ]

    return MockModel()
