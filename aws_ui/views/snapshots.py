from .common import *

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
        age = ""
        if len(self.custom_filters["age"]) > 0:
            age = self.custom_filters["age"][1:]
            age_comparison = self.custom_filters["age"][0]

        self.resources = []
        for resource in all_resources:
            start_time = str(resource.start_time)
            if age == "" \
            or (age_comparison == ">" and start_time > age) \
            or (age_comparison == "<" and start_time < age) \
            or (age_comparison == "=" and start_time.startsWith(age)):
                self.resources.append(resource)
        self.resources.sort(key=lambda r: r.start_time)

    def customFilters(self):
        return {
            "age": {
                "default": ">2022"
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
            snapshot.delete()
            pb.incrementCount()
        self.updateView()
        pb.insertCompletion()

    def actions(self):
        return {
            "delete": self.deleteAll,
        }
