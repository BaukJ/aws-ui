from .common import *

class VolumeListView(ResourceListView):
    def __init__(self):
        self.ec2 = boto3.resource('ec2', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        self.resources = self.ec2.volumes.filter(Filters=self.filterList())

    def defaultFilters(self):
        return {
            "status": "available",
        }

    def getHeadings(self):
        return super().getHeadings() + [
            {
                "title": "Created",
                "attribute": [".create_time"],
            },
            {
                "title": "State",
                "attribute": [".state"],
            },
        ]

    def deleteAll(self, widget):
        for r in self.resources:
            r.delete()
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
