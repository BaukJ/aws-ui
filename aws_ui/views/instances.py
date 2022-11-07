from .common import *

class InstanceListView(ResourceListView):
    def __init__(self):
        self.ec2 = boto3.resource('ec2', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        self.resources = self.ec2.instances.filter(Filters=self.filterList())

    def defaultFilters(self):
        return {
            "instance-state-name": "stopped",
        }

    def getHeadings(self):
        return super().getHeadings() + [
            {
                "title": "State",
                "attribute": [".state", "Name"],
            },
        ]

    def terminateAll(self, widget):
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
