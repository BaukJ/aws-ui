from .common import *
import datetime

class ImageListView(ResourceListView):
    def __init__(self):
        self.ec2 = boto3.resource('ec2', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        all_resources = self.ec2.images.filter(
            Filters=self.filterList(),
            Owners=["self"],
        )
        created = ""
        if len(self.custom_filters["created"]) > 0:
            created = self.custom_filters["created"][1:]
            created_comparison = self.custom_filters["created"][0]

        self.resources = []
        for resource in all_resources:
            creation_date = str(resource.creation_date)
            if created == "" \
            or (created_comparison == ">" and creation_date > created) \
            or (created_comparison == "<" and creation_date < created) \
            or (created_comparison == "=" and creation_date.startswith(created)):
                self.resources.append(resource)
        self.resources.sort(key=lambda r: r.creation_date)

    def customFilters(self):
        return {
            "created": {
                "default": f"={datetime.datetime.today().strftime('%Y-%m-%d')}"
            }
        }

    def defaultFilters(self):
        return {
        }

    def getHeadings(self):
        return super().getHeadings() + [
            {
                "title": "Created",
                "attribute": [".creation_date"],
                "size": 16,
            },
            {
                "title": "Public",
                "attribute": [".public"],
            },
            {
                "title": "Owner",
                "attribute": [".owner_id"],
            },
            {
                "title": "Description",
                "attribute": [".description"],
                "size": 30,
            },
        ]

    def deregisterAll(self, widget):
        pb = self.ProgressBar(self)

        for r in self.resources:
            try:
                r.deregister()
            except botocore.exceptions.ClientError as e:
                self.showError(str(e))
                pb.incrementErrors()
            pb.incrementCount()
        self.updateView()
        pb.insertCompletion()

    def deleteAll(self, widget):
        return
        # TODO: Also delete snapshots
        pb = self.ProgressBar(self)

        for r in self.resources:
            try:
                r.deregister()
            except botocore.exceptions.ClientError as e:
                self.showError(str(e))
                pb.incrementErrors()
            pb.incrementCount()
        self.updateView()
        pb.insertCompletion()

    def actions(self):
        return {
            "deregister": self.deregisterAll,
            "delete": self.deleteAll,
        }
