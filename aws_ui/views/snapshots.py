from .common import *
import botocore
import datetime

class SnapshotListView(ResourceListView):
    def __init__(self):
        self.ec2 = boto3.resource('ec2', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        filters = self.filterList()
        all_resources = self.ec2.snapshots.filter(
            Filters=filters,
            OwnerIds=["self"],
        )
        created = ""
        if len(self.custom_filters["created"]) > 0:
            created = self.custom_filters["created"][1:]
            created_comparison = self.custom_filters["created"][0]

        self.resources = []
        for resource in all_resources:
            start_time = str(resource.start_time)
            if created == "" \
            or (created_comparison == ">" and start_time > created) \
            or (created_comparison == "<" and start_time < created) \
            or (created_comparison == "=" and start_time.startswith(created)):
                self.resources.append(resource)
        self.resources.sort(key=lambda r: r.start_time)

    def customFilters(self):
        return {
            "created": {
                "default": f"={datetime.datetime.today().strftime('%Y-%m-%d')}"
            }
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
                "size": 16,
            },
            {
                "title": "Description",
                "attribute": [".description"],
                "size": 50,
            },
        ]

    def deleteAll(self, widget):
        pb = self.ProgressBar(self)

        for snapshot in self.resources:
            try:
                snapshot.delete()
            except botocore.exceptions.ClientError as e:
                self.showError(str(e))
                pb.incrementErrors()
            pb.incrementCount()
        self.updateView()
        pb.insertCompletion()

    def actions(self):
        return {
            "delete": self.deleteAll,
        }
