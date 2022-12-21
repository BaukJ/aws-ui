from .common import *

class ASGListView(ResourceListView):
    def __init__(self):
        self.asg = boto3.client('autoscaling', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        self.resources = self.asg.describe_auto_scaling_groups(Filters=self.filterList())["AutoScalingGroups"]

    def defaultFilters(self):
        return {
        }

    def getHeadings(self):
        #return super().getHeadings() + [
        return [
            {
                "title": "Name",
                "attribute": ["AutoScalingGroupName"],
            },
        ]

    def deleteAll(self, widget):
        for r in self.resources:
            r.delete()
            logging.warn(f"DELETING: {r.id}")
        self.updateView()

    def actionButtons(self):
        delete = u.Button("DELETE ALL")
        u.connect_signal(delete, 'click', self.deleteAll)
        return [
            u.Button("DUMMY"),
            delete,
        ]
    def actions(self):
        return {
            "delete": self.deleteAll,
        }
