#!/usr/bin/env python3
import sys
import re
import datetime
import os
# External
import boto3
import click
import urwid as u
import aws_ui.views
from aws_ui.session import Session

class NavBar(u.WidgetWrap):
    def __init__(self, menu, options, optionsCrumb=[]):
        self.menu = menu
        self.crumb = optionsCrumb
        self.parent_choice = [[None] + optionsCrumb][-1]
        self.choice = ""
        if 'AWS_PROFILE' in os.environ:
            profile = os.environ['AWS_PROFILE']
        else:
            profile = "*default*"
        self.walker = u.SimpleFocusListWalker([
            u.Divider(),
            u.AttrMap(u.Text(f" PROFILE: {profile}"), "header", "header"),
            u.Divider(),
        ])
        lb = u.ListBox(self.walker)
        for title, option in options.items():
            button = u.Button(title)
            u.connect_signal(button, 'click', self.clickMenuItem)
            self.walker.append(u.AttrMap(button, "menu_item", "menu_item_selected"))
        self.navbar = lb
        super().__init__(lb)

    def clickMenuItem(self, widget):
        self.choice = widget.label
        self.menu.open(self.crumb + [widget.label])

    def collapse(self):
        button = u.Button(self.choice)
        def action(widget):
            self.expand()
            #self.menu.open(self.crumb)
        u.connect_signal(button, "click", action)
        self._w = u.LineBox(u.Filler(u.AttrWrap(button, None, "menu_item_selected"), "top"))

    def expand(self):
        self._w = self.navbar

class Menu(u.Columns):
    def __init__(self, options):
        self.breadcrumb = []
        self.navbars = []
        self.details = None
        self.navbar = NavBar(self, options)
        self.menu_options = options
        super().__init__([
        ], dividechars=0)
        self.open()

    def open(self, crumb = []):
        for i in range(len(crumb), len(self.contents)):
            self.contents.pop()

        opts = self.menu_options
        for key in crumb:
            opts = opts[key]
        if isinstance(opts, dict):
            item = (NavBar(self, opts, crumb), self.options('weight', 10))
        else:
            item = (opts(), self.options('weight', 100))
        self.contents.append(item)
        self.focus_position = len(crumb)
        self.collapseAllButFocus()

    def collapseAllButFocus(self):
        focus = self.focus_position
        for i in range(0, len(self.contents)):
            if isinstance(self.contents[i][0], NavBar):
                if i == self.focus_position:
                    self.contents[i][0].expand()
                    self.contents[i] = (self.contents[i][0], self.options("weight", 50))
                else:
                    self.contents[i][0].collapse()
                    self.contents[i] = (self.contents[i][0], self.options("given", 3))

    def keypress(self, size, key):
        still_unused = super().keypress(size, key)
        # We catch all left and right arrows that have been processed to open up the correct menu
        if (key == "left" or key == "right") and not still_unused:
            self.collapseAllButFocus()
            return
        else:
            return still_unused

class App(object):
    def __init__(self):
        self.palette = {
            ("bg",                 "black",       "white"),
            ("menu_item",          "black",       "white"),
            ("menu_item_selected", "black",       "yellow"),
            ("row",                "",            ""),
            ("row_selected",       "bold",        ""),
            ("header",             "white, bold", "dark green"),
            ("sub_header",         "white", "dark green"),
            ("title",              "white, bold", "dark green"),
            ("footer",             "white, bold", "dark red"),
            ("pb",                 "white, bold", "dark red"),
            ("pb_smooth",          "white, bold", "brown"),
            ("pb_complete",        "white, bold", "dark green"),
        }

        self.menu = Menu({
            "Resources": {
                "Instances": aws_ui.views.InstanceListView,
                "Volumes": aws_ui.views.VolumeListView,
                "Snapshots": aws_ui.views.SnapshotListView,
                "Images": aws_ui.views.ImageListView,
                "Autoscaling Groups": aws_ui.views.ASGListView,
                "S3": aws_ui.views.S3ListView,
            },
        })
        frame = self.menu
        self.loop = u.MainLoop(frame, self.palette, unhandled_input=self.unhandled_input)

    def unhandled_input(self, key):
        if key in ('q',):
            raise u.ExitMainLoop()

    def start(self):
        Session.instance().loop = self.loop
        self.loop.run()

@click.command()
@click.option('--profile', '-p', help='AWS Profile to use')
def main(profile=None):
    if profile:
        os.environ['AWS_PROFILE'] = profile
    app = App()
    app.start()
