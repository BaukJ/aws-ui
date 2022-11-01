from .common import *
import datetime
import time

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
        total = 0
        for snapshot in self.resources:
            total += 1
        count = 0
        start_time = time.perf_counter()
        description = u.Text(f"{count}/{total} [0]")
        pb = u.ProgressBar('pb', 'pb_complete', count, total)

        self.lw.insert(-1, u.AttrWrap(u.Padding(description, "center", "pack"), "pb_complete"))
        self.lw.insert(-1, pb)

        for snapshot in self.resources:
            snapshot.delete()
            count += 1
            pb.set_completion(count)
            self.session.loop.draw_screen()
            time_taken = datetime.timedelta(seconds=(time.perf_counter() - start_time))
            description.set_text(f"Deleted {count}/{total} [{time_taken}]")
        self.updateView()
        self.lw.insert(0, u.AttrWrap(u.Padding(description, "center", "pack"), "pb_complete"))

    def actions(self):
        return {
            "delete": self.deleteAll,
        }
