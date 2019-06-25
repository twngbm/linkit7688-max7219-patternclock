import json
from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class ui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.events_name = ["Medicine", "Exercise", "Turn Over", "Chest Care", "Food"]
        self.do_layout()
        self.but_open.clicked.connect(self.openfile)
        self.but_add.clicked.connect(self.additem)
        self.but_save.clicked.connect(self.savefile)
        self.table.itemSelectionChanged.connect(self.itemselect)
        self.but_remove.clicked.connect(self.itemremove)

    def do_open_file(self):
        self.doc = QtWidgets.QFileDialog.getOpenFileName()
        self.setWindowTitle(str(self.doc[0]))
        if self.doc[0] == "":
            return -2
        try:
            with open(self.doc[0], mode='r') as file:
                self.data = json.loads(file.read())
            file.close()
            return 0
        except:
            return -1

    def do_parsing_data(self):
        for key in self.data:
            if key.isalnum():
                for inner_key in self.data[key]:
                    if inner_key not in ["hour", "minute", "events"]:
                        return -1
            else:
                return -1
            if self.data[key]["hour"] < 0 and self.data[key]["hour"] > 23 and self.data[key]["minute"] not in [0, 15, 30, 45]:
                return -1
            event = str(self.data[key]["events"])
            if len(event) == 11 and event[0] == "1" and event[5] == "2":
                time_bitmask = event[1:5]
                event_bitmask = event[6:]
                for i in time_bitmask:
                    if i != "0" and i != "1":
                        return -1
                for i in event_bitmask:
                    if i != "0" and i != "1":
                        return -1
                if time_bitmask.find("1")*15 != self.data[key]["minute"]:
                    return -1
        return 0

    def do_item_remove(self, idx):
        for key in self.data:
            if str(self.data[key]["hour"]) == self.table.item(idx, 0).text() and str(self.data[key]["minute"]) == self.table.item(idx, 1).text():
                del_key = key
        self.data.pop(del_key)

    def do_pop_up(self, message, message_type="Warning"):
        pop_up = QtWidgets.QMessageBox.question(
            self, message_type, message, QtWidgets.QMessageBox.Ok)

    def do_pop_up_confirm(self, message, message_type="Warning"):
        pop_up = QtWidgets.QMessageBox.question(
            self, message_type, message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if pop_up == QtWidgets.QMessageBox.Yes:
            return 1
        else:
            return 0

    def do_add_item(self):
        hour_chosen = self.combo_hour.currentIndex()
        minute_chosen = self.combo_minute.currentIndex()
        medicine_chosen = self.chkbx_medicine.checkState()
        exercise_chosen = self.chkbx_exercise.checkState()
        wake_chosen = self.chkbx_wake.checkState()
        hand_chosen = self.chkbx_hand.checkState()
        eat_chosen = self.chkbx_eat.checkState()

        for idx, key in enumerate(self.data):
            if hour_chosen == self.data[key]["hour"] and minute_chosen*15 == self.data[key]["minute"]:
                self.do_pop_up(
                    "Insert time already exist in current schedul,please remove old one.")
                return
        name_counter = 0
        key_list = [key for key in self.data]
        while True:
            if str(name_counter) in key_list:
                name_counter += 1
            else:
                break
        time_bitmask = "0"*(minute_chosen)+"1"+"0"*(3-minute_chosen)
        event_bitmask = [0, 0, 0, 0, 0]
        if medicine_chosen == QtCore.Qt.Checked:
            event_bitmask[0] = 1
        if exercise_chosen == QtCore.Qt.Checked:
            event_bitmask[1] = 1
        if wake_chosen == QtCore.Qt.Checked:
            event_bitmask[2] = 1
        if hand_chosen == QtCore.Qt.Checked:
            event_bitmask[3] = 1
        if eat_chosen == QtCore.Qt.Checked:
            event_bitmask[4] = 1
        event_bitmask = str(event_bitmask[0])+str(event_bitmask[1])+str(
            event_bitmask[2])+str(event_bitmask[3])+str(event_bitmask[4])
        events = "1"+time_bitmask+"2"+event_bitmask
        self.data[str(name_counter)] = {
            "hour": hour_chosen, "minute": minute_chosen*15, "events": events}

    def do_clear(self):
        t_rc = self.table.rowCount()
        for r in range(t_rc):
            self.table.removeRow(0)

    def do_output(self,name):
        output_data = {}
        for idx, key in enumerate(self.data):
            output_data[str(idx)] = self.data[key]
        
        if ".json" not in name[0]:
            with open(name[0]+".json", "w") as output_file:
                json.dump(output_data, output_file)
                output_file.close()
        else:
            with open(name[0], "w") as output_file:
                json.dump(output_data, output_file)
                output_file.close()
    def do_draw_table(self):
        self.do_clear()
        data_list = [self.data[key] for key in self.data]
        data_list = sorted(data_list, key=lambda i: (i["hour"], i["minute"]))

        for idx, key in enumerate(data_list):
            self.table.insertRow(self.table.rowCount())
            hour_context = QtWidgets.QTableWidgetItem(
                str(data_list[idx]["hour"]))
            minute_context = QtWidgets.QTableWidgetItem(
                str(data_list[idx]["minute"]))
            event_list = ""
            event = str(data_list[idx]["events"])[6:]
            for key, event_byte in enumerate(event):
                if event_byte == "1":
                    event_list += str(self.events_name[key])+","
            events_context = QtWidgets.QTableWidgetItem(event_list)
            hour_context.setTextAlignment(QtCore.Qt.AlignCenter)
            hour_context.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)
            minute_context.setTextAlignment(QtCore.Qt.AlignCenter)
            minute_context.setFlags(QtCore.Qt.ItemIsSelectable |
                                    QtCore.Qt.ItemIsEnabled)
            events_context.setTextAlignment(QtCore.Qt.AlignCenter)
            events_context.setFlags(QtCore.Qt.ItemIsSelectable |
                                    QtCore.Qt.ItemIsEnabled)
            self.table.setItem(idx, 0, hour_context)
            self.table.setItem(idx, 1, minute_context)
            self.table.setItem(idx, 2, events_context)
        self.table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()

    def openfile(self):
        self.error_code = self.do_open_file()
        if self.error_code == -1:
            self.do_pop_up("File format no match.")
            return
        elif self.error_code == -2:
            return
        self.error_code = self.do_parsing_data()
        if self.error_code != 0:
            self.do_pop_up("File content no match, may be corrupted.")
            return
        self.do_draw_table()

    def savefile(self):
        dialog=QtWidgets.QFileDialog()
        name=dialog.getSaveFileName(self,"Save File","Schedule.json")
        if name[0]=="":
            return
        try:
            self.data
        except:
            self.data = {"0": {"hour": 1, "minute": 0, "events": 11000200000}}
        if len(self.data) == 0:
            self.data = {"0": {"hour": 1, "minute": 0, "events": 11000200000}}
        self.do_output(name)
        self.do_pop_up(
            "    File output susscessfully into the Folder.  Please do the following steps to update the new schedule:\n\
            1. Put Schedule.json into USB device.\n\
            2. Plug the USB device to the clock.\n\
            3. Wait at least 10 seconds, then plug out the USB device.\n\
            4. Wait for the clock to reset.", "Information")

    def additem(self):
        try:
            self.data
        except:
            self.data = {}
        self.do_add_item()
        self.do_draw_table()

    def itemselect(self):
        self.but_remove.setEnabled(True)

    def itemremove(self):

        idx = self.table.selectionModel().selectedRows()[0].row()
        confirm = self.do_pop_up_confirm(
            "Are you Sure You want to remove event at:\n\
    Hour:"+self.table.item(idx, 0).text()+"\n\
    Minute:"+self.table.item(idx, 1).text()+"\n\
WARNING:THIS CAN NOT BE UNDO!")
        if confirm == 0:
            return
        self.do_item_remove(idx)
        self.do_draw_table()
        self.but_remove.setEnabled(False)

    def do_layout(self):
        hour = [str(i) for i in range(24)]
        minute = ["0", "15", "30", "45"]
        self.table = QtWidgets.QTableWidget(0, 3)
        self.format = QtGui.QFont()
        self.format.setPointSize(18)
        self.table.setFont(self.format)
        self.table.setHorizontalHeaderLabels(
            ["Hour", "Minute", "Things to do"])
        self.but_add = QtWidgets.QPushButton("Add")
        self.format = self.but_add.font()
        self.format.setPointSize(18)
        self.but_add.setFont(self.format)
        self.but_remove = QtWidgets.QPushButton("Remove")
        self.but_remove.setFont(self.format)
        self.but_save = QtWidgets.QPushButton("Save")
        self.but_save.setFont(self.format)
        self.but_open = QtWidgets.QPushButton("Open")
        self.but_open.setFont(self.format)
        self.chkbx_medicine = QtWidgets.QCheckBox("Medicine")
        self.chkbx_medicine.setFont(self.format)
        self.chkbx_exercise = QtWidgets.QCheckBox("Exercise")
        self.chkbx_exercise.setFont(self.format)
        self.chkbx_wake = QtWidgets.QCheckBox("Turn Over")
        self.chkbx_wake.setFont(self.format)
        self.chkbx_hand = QtWidgets.QCheckBox("Chest Care")
        self.chkbx_hand.setFont(self.format)
        self.chkbx_eat = QtWidgets.QCheckBox("Food")
        self.chkbx_eat.setFont(self.format)
        self.combo_hour = QtWidgets.QComboBox()
        self.combo_hour.addItems(hour)
        self.combo_hour.setFont(self.format)
        self.combo_minute = QtWidgets.QComboBox()
        self.combo_minute.addItems(minute)
        self.combo_minute.setFont(self.format)
        self.lb_hour = QtWidgets.QLabel("Hour")
        self.lb_hour.setFont(self.format)
        self.lb_minute = QtWidgets.QLabel("Minute")
        self.lb_minute.setFont(self.format)
        self.lb_events = QtWidgets.QLabel("Things to do:")
        self.lb_events.setFont(self.format)
        button_layer = QtWidgets.QHBoxLayout()
        button_layer.addWidget(self.but_open)
        button_layer.addWidget(self.but_save)
        button_layer.addWidget(self.but_add)
        button_layer.addWidget(self.but_remove)
        show_layer = QtWidgets.QVBoxLayout()
        show_layer.addWidget(self.table)
        show_layer.addLayout(button_layer)
        event_setup_layer = QtWidgets.QVBoxLayout()
        event_setup_layer.addWidget(self.lb_hour)
        event_setup_layer.addWidget(self.combo_hour)
        event_setup_layer.addWidget(self.lb_hour)
        event_setup_layer.addWidget(self.combo_minute)
        event_setup_layer.addWidget(self.lb_events)
        event_setup_layer.addWidget(self.chkbx_medicine)
        event_setup_layer.addWidget(self.chkbx_exercise)
        event_setup_layer.addWidget(self.chkbx_wake)
        event_setup_layer.addWidget(self.chkbx_hand)
        event_setup_layer.addWidget(self.chkbx_eat)
        main_layer = QtWidgets.QHBoxLayout()
        main_layer.addLayout(show_layer)
        main_layer.addLayout(event_setup_layer)
        self.setLayout(main_layer)
        self.setWindowTitle("Event Editor")
        try:
            self.setWindowIcon(QtGui.QIcon("icon.png"))
        except:
            pass
        self.table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.but_remove.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main_windows = ui()
    main_windows.resize(800, 320)
    main_windows.show()
    sys.exit(app.exec_())
