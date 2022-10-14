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
        total = 0
        for snapshot in self.resources:
            total += 1
        count = 0
        pb = u.ProgressBar('pb', 'pb_complete', count, total)
        self.lw.append(pb)
        for snapshot in self.resources:
            snapshot.delete()
            count += 1
            pb.set_completion(count)
            self.session.loop.draw_screen()
        self.updateView()

    def actions(self):
        return {
            "delete": self.deleteAll,
        }
