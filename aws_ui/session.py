class Session(object):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    def init(self):
        self.filters = {
            "tag:Name": "*",
        }
        self.resource_filters = {}
        self.region = "eu-west-2"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.init()
        return cls._instance

