# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WPSWidgetDockWidget
                                 A QGIS plugin
 WPS PLugin OpenGeoLabs
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-06-05
        git sha              : $Format:%H$
        copyright            : (C) 2021 by OpenGeoLabs
        email                : jan.ruzicka.vsb@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtGui
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *

import json

from .connect import *
from .wps_dialog import WpsDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'wps_plugin_ogl_dockwidget_base.ui'))


class WPSWidgetDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(WPSWidgetDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.iface = iface
        self.setupUi(self)
        self.first_start = True
        tree = self.treeWidgetServices
        tree.itemSelectionChanged.connect(self.handleSelected)
        self.pushButtonExecute.clicked.connect(self.execute_process)
        self.root = QTreeWidgetItem(tree)
        self.root.setText(0, 'WPS Services')
        self.loadServices(self.root)
        self.treeWidgetServices.customContextMenuRequested.connect(self.menuContextTree)

    def appendServiceToTree(self, parent, service_url):
        service = QTreeWidgetItem(parent)
        service.setText(0, service_url)
        service.setData(0, Qt.UserRole, service_url)

    def loadServices(self, parent):
        with open(os.path.join(os.path.dirname(__file__), 'services/list.json')) as f:
            self.services = json.load(f)
        for service_url in self.services:
            self.appendServiceToTree(parent, service_url)
#         process = QTreeWidgetItem(service)
#         process.setText(0, 'Process 1')

    def menuContextTree(self, point):
        # Infos about the node selected.
        index = self.treeWidgetServices.indexAt(point)

        if not index.isValid():
            return

        item = self.treeWidgetServices.itemAt(point)
        name = item.text(0)  # The text of the node.

        # We build the menu.
        menu = QtWidgets.QMenu()
#         action = menu.addAction("Souris au-dessus de")
#         action = menu.addAction(name)
#         menu.addSeparator()
        if item.parent() is None:
            action_new_connection = menu.addAction(self.tr("New Service"))
            action_new_connection.triggered.connect(self.new_service)
        else:
            if item.parent().parent() is None:
                action_delete_connection = menu.addAction(self.tr("Remove Service"))
                action_delete_connection.triggered.connect(self.remove_service)
            else:
                action_run_process = menu.addAction(self.tr("Execute"))
                action_run_process.triggered.connect(self.execute_process)

        menu.exec_(self.treeWidgetServices.mapToGlobal(point))

    def saveServices(self):
        with open(os.path.join(os.path.dirname(__file__), 'services/list.json'), 'w') as f:
            json.dump(self.services, f)

    def new_service(self):
        text, ok = QInputDialog.getText(self, self.tr('New Service'), self.tr('Enter url of the service'))
        if ok:
            if text in self.services:
                QMessageBox.information(
                            None, self.tr("INFO:"),
                            self.tr("The service is already registered"))
            else:
                self.services.append(text)
                self.appendServiceToTree(self.root, text)
                self.saveServices()

    def remove_service(self):
        reply = QMessageBox.question(
                        self,
                        self.tr("Remove service"),
                        "This will remove the service from the list. Are you sure?",
                        QMessageBox.Yes,
                        QMessageBox.No,
                    )

        if reply == QMessageBox.Yes:
            service = self.get_selected_item()
            service_data = service.data(0, Qt.UserRole)
            parent = service.parent()
            parent.removeChild(service)
            self.services.remove(service_data)
            self.saveServices()

    def execute_process(self):
        process = self.get_selected_item()
        process_data = process.data(0, Qt.UserRole)
        items = process_data.split('|')
        if self.first_start == True:
           self.first_start = False
           self.dlg = WpsDialog(self.iface)

        self.dlg.set_service_url(items[0])
        self.dlg.set_process_identifier(items[2])
        self.dlg.load_process()
        # show the dialog
        self.dlg.show()

    def handleSelected(self):
        self.pushButtonExecute.setEnabled(False)
        for item in self.treeWidgetServices.selectedItems():
            if item.data(0, Qt.UserRole) is not None:
                id = item.data(0, Qt.UserRole)
                if '|' not in id:
                    print('This is service')
                    print(id)
                    self.load_processes(id)
                else:
                    print('This is process')
                    print(id)
                    self.pushButtonExecute.setEnabled(True)
                    self.process_selected(id)

    def get_selected_item(self):
        for item in self.treeWidgetServices.selectedItems():
            return item

    def load_processes(self, url):
            self.setCursor(Qt.WaitCursor)
#             self.textEditLog.append(self.tr("Loading processes ..."))
            self.loadProcesses = GetProcesses()
            self.loadProcesses.setUrl(url)
            self.loadProcesses.statusChanged.connect(self.on_load_processes_response)
            self.loadProcesses.start()

    def on_load_processes_response(self, response):
        if response.status == 200:
            self.processes = response.data
            service = self.get_selected_item()
            for i in reversed(range(service.childCount())):
                service.removeChild(service.child(i))
            service_url = service.data(0, Qt.UserRole)
            id = 0
            for proc in self.processes:
                process = QTreeWidgetItem(service)
                process.setText(0, '[{}] {}'.format(proc.identifier, proc.title))
                process.setData(0, Qt.UserRole, service_url + '|' + str(id) + '|' + str(proc.identifier))
#                 print(proc.title)
                id += 1
            self.show_process_description(0)
#             self.textEditLog.append(self.tr("Processes loaded"))
        else:
            QMessageBox.information(None, self.tr("ERROR:"), self.tr("Error loading processes"))
#             self.textEditLog.append(self.tr("Error loading processes"))
        self.setCursor(Qt.ArrowCursor)

    def show_process_description(self, index):
        self.textEditProcessDescription.setText("[" + self.processes[index].identifier + "]: " + self.processes[index].abstract)

    def process_selected(self, id):
        current_index = int(id.split('|')[1])
        self.show_process_description(current_index)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
