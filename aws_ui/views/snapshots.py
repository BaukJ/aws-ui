from .common import *

class SnapshotListView(ResourceListView):
    def __init__(self):
        super().__init__()

    def fetchResources(self):
        self.resources = self.ec2.snapshots.filter(
            Filters=self.filterList(),
            OwnerIds=["self"],
        )

    def defaultFilters(self):
        return {
        }

    def getHeadings(self):
        return super().getHeadings() + [
            {
                "title": "Status",
                "attribute": [".state"],
            },
            {
                "title": "Start Time",
                "attribute": [".start_time"],
                "size": 10,
            },
            {
                "title": "Description",
                "attribute": [".description"],
                "size": 50,
            },
        ]

    def deleteAll(self, widget):
        for snapshot in self.resources:
            snapshot.delete()
        self.updateView()

    def actions(self):
        return {
            "delete": self.deleteAll,
        }
