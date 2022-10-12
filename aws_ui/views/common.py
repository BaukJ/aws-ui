import boto3
import urwid as u
from aws_ui.session import Session

class ResourceFilterView(u.ListBox):
    def __init__(self, parent, filters={}):
        self.parent = parent
        self.filters = filters
        self.lw = u.SimpleFocusListWalker([])
        self.lw.append(u.Text("Filters")) # TODO: AttrMap colour
        self.lw.append(u.Divider())
        self.filterEdits = {}
        self.sessionFilterEdits = {}
        self.session = Session.instance()

        self.lw.append(u.Text("Resource specific Filters:"))
        for name, value in sorted(filters.items()):
            edit = u.Edit(name + ": ", value)
            self.filterEdits[name] = edit
            self.lw.append(edit)
        self.lw.append(u.Divider())

        self.lw.append(u.Text("Session Filters:"))
        for name, value in sorted(self.session.filters.items()):
            edit = u.Edit(name + ": ", value)
            self.sessionFilterEdits[name] = edit
            self.lw.append(edit)
        super().__init__(self.lw)

    def keypress(self, size, key):
        if key == "enter":
            for name, edit in self.filterEdits.items():
                self.filters[name] = edit.edit_text
            for name, edit in self.sessionFilterEdits.items():
                self.session.filters[name] = edit.edit_text
            self.parent.openResouceList()
        else:
            return super().keypress(size, key)

class ResourceListView(u.LineBox):
    def __init__(self):
        region = "eu-west-2"
        self.ec2 = boto3.resource('ec2', region)
        self.s3  = boto3.resource('s3', region)
        self.asg = boto3.client('autoscaling', region)
        self.session = Session.instance()
        self.resource_name = type(self).__name__
        if not self.resource_name in self.session.resource_filters:
            self.session.resource_filters[self.resource_name] = self.defaultFilters()
        self.filters = self.session.resource_filters[self.resource_name]
        self.lw = u.SimpleFocusListWalker([])
        super().__init__(u.ListBox(self.lw))
        self.updateView()

    def keypress(self, size, key):
        # Have to invert this logic so that the downstream edits can get all the keystrokes first
        if not super().keypress(size, key):
            return
        if key == "r":
            self.updateView()
        elif key == "f":
            self.openFilterEdit()
        else:
            return key

    def openFilterEdit(self):
        self.list_view = self._w
        self.lw.clear()
        self._w = ResourceFilterView(self, self.filters)

    def openResouceList(self):
        self._w = self.list_view
        self.updateView()

    def filterList(self):
        filters = []
        for name, value in self.filters.items():
            if value:
                filters.append({"Name": name, "Values": value.split(",")})
        for name, value in Session.instance().filters.items():
            if value:
                filters.append({"Name": name, "Values": value.split(",")})
        return filters

    def updateView(self, fetch = True):
        self.lw.clear()
        if fetch:
            self.fetchResources()
        count = 0
        headings = self.getHeadings()
        table = u.Columns([])

        # TODO: Make a nice table for it
        #for header in headings:
        #    table.contents.append((u.Filler(u.Text(header), "top"), table.options("weight", 1)))
        #self.lw.append(u.BoxAdapter(table, 100))
        for resource in self.resources:
            self.lw.append(u.Button("|".join(self.getRow(resource, headings))))
            self.lw.append(u.Button(str(resource)))
            count += 1
        self.lw.append(u.Divider())
        self.lw.append(u.Text(f"TOTAL: {count}"))
        self.lw.append(u.Divider())
        #for action in self.actionButtons():
        #    self.lw.append(action)
        self.actionEdit = u.Edit(f"Action [{'/'.join(self.actions().keys())}]: ")
        self.lw.append(self.actionEdit)
        self.actionButton = u.Button("CONFIRM")
        u.connect_signal(self.actionButton, 'click', self.confirmAction)
        self.lw.append(u.AttrWrap(self.actionButton, None, "menu_item_selected"))
        #for action in self.actions():
        #    self.lw.append(action)

    def confirmAction(self, widget):
        action = self.actionEdit.edit_text
        self.updateView(fetch=False)
        if action in self.actions():
            confirm = u.Button(f"Click to confirm the following action: {action}")
            u.connect_signal(confirm, 'click', self.actions()[action])
            self.lw.append(u.AttrWrap(confirm, None, "menu_item_selected"))
        else:
            self.lw.append(u.AttrWrap(u.Text(f"INVALID ACTION: {action}"), None, "menu_item_selected"))
            

    def actionButtons(self):
        return []

    def actions(self):
        return {}

    def getHeadings(self):
        return [
            {
                "title": "ID",
                "attribute": [".id"],
            },
            {
                "title": "Name",
                "attribute": [".tags", "#Name"],
                "size": 30,
            },
        ]

    def getRow(self, resource, headings):
        row = []
        for h in headings:
            item = resource
            for a in h["attribute"]:
                if not item:
                    pass
                elif isinstance(a, str):
                    if a.startswith("."):
                        item = getattr(item, a[1:])
                    elif a.startswith("#"):
                        item = list(map(lambda i: i["Value"], filter(lambda i: i["Key"] == a[1:], item)))
                        item = ",".join(item)
                    else:
                        item = item[a]
                elif isinstance(a, int):
                    item = item[a]
                else:
                    item = a(item)
            item = str(item)
            if "size" in h:
                item = item[:h["size"]].ljust(h["size"])
            row.append(item)
        return row

    def fetchResources(self):
        raise NotImplementedError("Needs to be replaced")

    def defaultFilters(self):
        return {}
