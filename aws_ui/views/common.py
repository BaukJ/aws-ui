import boto3
import urwid as u
from aws_ui.session import Session

class ResourceDetailsView(u.ListBox):
    def __init__(self, parent, resource):
        self.parent = parent
        self.resource = resource

        self.lw = u.SimpleFocusListWalker([])
        self.lw.append(u.Text("Resource Details")) # TODO: AttrMap colour
        self.lw.append(u.Divider())
        self.lw.append(u.Text("Tags:"))
        for tag in resource.tags:
            self.lw.append(u.Text(f"{tag['Key'].rjust(20)} = {tag['Value']}"))
        self.lw.append(u.Divider())
        self.lw.append(u.AttrWrap(u.Text("Hit Enter to return to the list"), "footer"))
        super().__init__(self.lw)

    def keypress(self, size, key):
        if not super().keypress(size, key):
            return
        if key == "enter":
            self.parent.openResouceList(refresh=False)
        else:
            return key

class ResourceFilterView(u.ListBox):
    def __init__(self, parent):
        self.parent = parent
        self.session = Session.instance()
        self.resource_name = parent.resource_name

        self.filterEdits = {}
        self.customFilterEdits = {}
        self.sessionFilterEdits = {}

        self.lw = u.SimpleFocusListWalker([])
        self.lw.append(u.Padding(u.AttrWrap(u.Text(" Filters "), "title"), "center", "pack"))
        self.lw.append(u.Divider())

        if self.session.resource_custom_filters.get(self.resource_name):
            self.lw.append(u.Text("Custom Resource Filters:"))
            for name, value in sorted(self.session.resource_custom_filters[self.resource_name].items()):
                edit = u.Edit(name + ": ", value)
                self.customFilterEdits[name] = edit
                self.lw.append(edit)
            self.lw.append(u.Divider())

        if self.session.resource_filters.get(self.resource_name):
            self.lw.append(u.Text("Resource specific Filters:"))
            for name, value in sorted(self.session.resource_filters[self.resource_name].items()):
                edit = u.Edit(name + ": ", value)
                self.filterEdits[name] = edit
                self.lw.append(edit)
            self.lw.append(u.Divider())

        self.lw.append(u.Text("Session Filters:"))
        for name, value in sorted(self.session.filters.items()):
            edit = u.Edit(name + ": ", value)
            self.sessionFilterEdits[name] = edit
            self.lw.append(edit)

        self.addFilterEdit = u.Edit("Add filter: ", "tag:")
        self.addFilterEditWrap = u.AttrWrap(self.addFilterEdit, "menu_item", "menu_item")
        self.lw.append(self.addFilterEditWrap)
        self.lw.append(u.Divider())
        self.lw.append(u.AttrWrap(u.Text("Any filters with an empty value will be ignored"), "footer"))
        self.lw.append(u.AttrWrap(u.Text("Hit Enter to return to apply the filers and return to the list"), "footer"))
        super().__init__(self.lw)

    def keypress(self, size, key):
        if not super().keypress(size, key):
            return
        if key == "a":
            pass
        elif key == "enter":
            if self.addFilterEditWrap in self.get_focus_widgets():
                key = self.addFilterEdit.edit_text
                edit = u.Edit(key+": ", "")
                self.sessionFilterEdits[key] = edit
                self.lw.insert(-4, edit)
                self.addFilterEdit.edit_text = "tag:"
            else:
                for name, edit in self.customFilterEdits.items():
                    self.session.resource_custom_filters[self.resource_name][name] = edit.edit_text
                for name, edit in self.filterEdits.items():
                    self.session.resource_filters[self.resource_name][name] = edit.edit_text
                for name, edit in self.sessionFilterEdits.items():
                    self.session.filters[name] = edit.edit_text
                self.parent.openResouceList()
        else:
            return key


class ResourceRowButton(u.Button):
    def __init__(self, resource, message):
        self.resource = resource
        super().__init__(message)

class ResourceRow(u.AttrWrap):
    def __init__(self, list_view, resource, headings):
        self.button = ResourceRowButton(resource, self.getMessage(resource, headings))
        super().__init__(self.button, "row", "row_selected")
        u.connect_signal(self.button, 'click', list_view.openResouceDetails)

    def getMessage(self, resource, headings):
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
        return "|".join(row)

class ResourceListView(u.LineBox):
    def __init__(self):
        self.session = Session.instance()
        self.resource_name = type(self).__name__
        if not self.resource_name in self.session.resource_filters:
            self.session.resource_filters[self.resource_name] = self.defaultFilters()
        if not self.resource_name in self.session.resource_custom_filters:
            self.session.resource_custom_filters[self.resource_name] = {}
            for k, v in self.customFilters().items():
                self.session.resource_custom_filters[self.resource_name][k] = v.get("default", "")
        self.filters = self.session.resource_filters[self.resource_name]
        self.custom_filters = self.session.resource_custom_filters[self.resource_name]
        self.lw = u.SimpleFocusListWalker([])
        super().__init__(u.ListBox(self.lw))
        self.list_view = self._w
        self.openResouceList()

    def keypress(self, size, key):
        # Have to invert this logic so that the downstream edits can get all the keystrokes first
        if not super().keypress(size, key):
            return
        if key == "r":
            self.updateView()
        elif key == "f" or key == "/":
            self.openFilterEdit()
        else:
            return key

    def openFilterEdit(self):
        self._w = u.LineBox(ResourceFilterView(self))

    def openResouceDetails(self, widget):
        self._w = u.LineBox(ResourceDetailsView(self, widget.resource))

    def openResouceList(self, refresh=True):
        if refresh:
            self.updateView()
        self._w = self.list_view

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
            self.lw.append(ResourceRow(self, resource, headings))
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
                "size": 40,
            },
        ]

    def fetchResources(self):
        raise NotImplementedError("Needs to be replaced")

    def defaultFilters(self):
        return {}

    def customFilters(self):
        return {}
        # e.g:
        # {
        #   date: {
        #     default: "",  # optional
        #   }
        # }
