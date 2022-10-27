from .common import *

class S3ListView(ResourceListView):
    def __init__(self):
        self.s3 = boto3.resource('s3', Session.instance().region)
        super().__init__()

    def fetchResources(self):
        # Although this filter function does exist, it does not actually do any filtering
        #self.resources = self.s3.buckets.filter(Filters=self.filterList())
        self.resources = self.s3.buckets.all()

    def defaultFilters(self):
        return {}

    def getHeadings(self):
        return [
            {
                "title": "Name",
                "attribute": [".name"],
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
