from .common import *

class InstanceListView(ResourceListView):
    def __init__(self):
        self.ec2 = boto3.resource('ec2', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        self.resources = self.ec2.instances.filter(Filters=self.filterList())

    def defaultFilters(self):
        return {
            "instance-state-name": "stopped,running",
            "launch-time": f"{datetime.datetime.today().strftime('%Y-%m-%d')}T*",
        }

    def getHeadings(self):
        return super().getHeadings() + [
            {
                "title": "State",
                "attribute": [".state", "Name"],
            },
            {
                "title": "Image",
                "attribute": [".image_id"],
            },
            {
                "title": "Launched",
                "attribute": [".launch_time"],
                "size": 16,
            },
        ]

    def terminateAll(self, widget):
        for r in self.resources:
            logging.warn(f"MASS DELETING: {r.id}")
        logging.warn("MASS DELETING THE ABOVE...")
        self.resources.terminate()
        self.updateView()

    def stopAll(self, widget):
        self.resources.stop()
        self.updateView()

    def actions(self):
        return {
            "delete": self.terminateAll,
            "stop": self.stopAll,
        }
