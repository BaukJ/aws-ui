class Session(object):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    def init(self):
        self.filters = {                   # Shared AWS filters accross all resources
            "tag:Name": "*",
        }
        self.resource_filters = {}         # Used to apply filters to resources (AWS side)
        self.resource_custom_filters = {}  # Used to apply extra filters that are not part of the available AWS filters (usually client side)
        self.region = "eu-west-2"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.init()
        return cls._instance

