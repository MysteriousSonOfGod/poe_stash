import sys, json
import collections

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from loguru import logger
from gui.stash_design import Ui_MainWindow
from gui.create_filter_dialog import Ui_CreateFilterDialog
from gui.add_filter_info import Ui_AddFilterInfoDialog
import stash
import item_treatment
import filter


# TODO: Habilitar criação de filtro com OR
from gui.worker_qt import Worker


class StashDesign(QMainWindow, Ui_MainWindow):
    FilterLoaded = pyqtSignal()
    FilterValuedUpdated = pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self)

    def setupUi(self, MainWindow):
        super(StashDesign, self).setupUi(MainWindow)
        self.poesessid_text = ''
        self.poetabs_text = ''
        self.json_text = ''
        self.filters = {}
        self.create_filter_window = CreateFilterDialog()
        self.GetStashButton.clicked.connect(self.stash_worker)
        self.ImportFiltersButton.clicked.connect(self.filter_worker)
        self.FilterLoaded.connect(self.load_filters_combobox)
        self.SelectFilterCombo.activated.connect(self.change_filter_description)
        self.CreateFiltersButton.clicked.connect(self.create_filter_dialog)
        self.create_filter_window.FilterFinished.connect(self.save_filter)
        self.FilterValuedUpdated.connect(self.clear_create_filter_values)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    @property
    def stash_tabs(self):
        return self._stash_tabs

    @stash_tabs.setter
    def stash_tabs(self, value):
        self._stash_tabs = value

    @property
    def stash_items(self):
        return self._stash_tabs

    @stash_items.setter
    def stash_items(self, value):
        self._stash_items = value

    def progress_fn(self, n):
        print("%d%% done" % n)

    def stash_execute_fn(self, progress_callback):
        return self.get_text_inputs()

    def filter_execute_fn(self, progress_callback):
        return self.get_filters()

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def filter_worker(self):
        # Pass the function to execute
        # Any other args, kwargs are passed to the run function
        worker = Worker(self.filter_execute_fn)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

    def stash_worker(self):
        # Pass the function to execute
        worker = Worker(self.stash_execute_fn)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)
        self.stackedWidget.setCurrentIndex(1)

    def recurring_timer(self):
        self.counter += 1
        self.l.setText("Counter: %d" % self.counter)

    def get_text_inputs(self):
        self.poesessid_text = self.input_poesessid.toPlainText()
        logger.debug(self.poesessid_text)
        self.poetabs_text = self.input_poetabs.toPlainText()
        self.poetabs_text = self.poetabs_text.split(',')
        logger.debug(self.poetabs_text)
        logger.debug('Downloading stash')
        self.stash_tabs = stash.get_account_tabs(self.poesessid_text, self.poetabs_text)
        logger.debug('Stash tabs downloaded')
        logger.debug('Reading items')
        self.stash_items = item_treatment.get_items_from_all_tabs(self.stash_tabs)

    def get_filters(self):
        # filename, _ = QFileDialog.getOpenFileName(self, 'Open file', '../')
        self.filters = filter.open_filters_files('../filters.json')
        logger.debug(self.filters)
        self.FilterLoaded.emit()

    def load_filters_combobox(self):
        logger.debug('Loading filters combobox')
        self.SelectFilterCombo.clear()
        for filter_name in self.filters.keys():
            logger.debug(filter_name)
            self.SelectFilterCombo.addItem(filter_name)

    def change_filter_description(self, value):
        filter_name = self.SelectFilterCombo.currentText()
        self.ShowFilterStatsText.setText(json.dumps(self.filters[filter_name], indent=4))

    def create_filter_dialog(self):
        self.create_filter_window.exec_()

    def save_filter(self, value):
        logger.debug(f'Saving filter: {value}')
        self.filters = {**self.filters, **value}
        filter.save_filter_model(self.filters)
        logger.debug(self.filters)
        self.FilterValuedUpdated.emit()
        self.FilterLoaded.emit()

    def clear_create_filter_values(self):
        self.create_filter_window.filter = collections.defaultdict(dict)
        self.create_filter_window.textBrowser.setText('')


class CreateFilterDialog(QDialog, Ui_CreateFilterDialog):
    ValuedUpdated = pyqtSignal()
    FilterFinished = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(CreateFilterDialog, self).__init__(parent)
        self.setupUi(self)
        self_dict_name = ''
        self.or_dicts = []
        self.button_filter_info.clicked.connect(self.open_add_filter_info_window)
        self.add_and_filter_window = AddFilterInfoDialog()
        self.add_or_filter_window = AddFilterInfoDialog()
        self.add_and_filter_window.FinishedDict.connect(self.append_and_dict)
        self.add_or_filter_window.FinishedDict.connect(self.append_or_dict)
        self.filter = collections.defaultdict(dict)
        self.combbox_filter_or.activated.connect(self.deal_with_or_filters)
        self.ValuedUpdated.connect(self.clear_and_or_filter)
        self.buttonBox.accepted.connect(self.send_filter)

    def clear_and_or_filter(self):
        self.add_and_filter_window.filter = collections.defaultdict(dict)
        self.add_and_filter_window.text_show_current_dict.setText('')
        self.add_or_filter_window.filter = collections.defaultdict(dict)
        self.add_or_filter_window.text_show_current_dict.setText('')

    def open_add_filter_info_window(self):
        self.add_and_filter_window.exec_()

    def open_or_filter_info_window(self):
        self.add_or_filter_window.exec_()

    def deal_with_or_filters(self, value):
        if value == 0:
            self.open_or_filter_info_window()
        else:
            self.add_or_filter_window.filter = self.filter[list(self.filter.keys())[0]]['OR'].pop(value - 1)
            self.open_or_filter_info_window()

    @pyqtSlot(dict)
    def append_and_dict(self, value):
        and_dict = value
        self.filter['dict_name']['AND'] = and_dict
        logger.debug(self.filter)
        self.change_filter_description()
        self.ValuedUpdated.emit()

    @pyqtSlot(dict)
    def append_or_dict(self, value):
        self.or_dicts.append(value)
        self.filter['dict_name']['OR'] = self.or_dicts
        logger.debug(self.filter)
        self.change_filter_description()
        self.combbox_filter_or.addItem(str(len(self.or_dicts)))
        self.ValuedUpdated.emit()

    def change_filter_description(self):
        self.textBrowser.setText(json.dumps(self.filter, indent=4))

    def send_filter(self):
        logger.debug('Sending filter')
        filter_name = self.edit_name.text()
        filter = dict(self.filter)
        filter[filter_name] = filter.pop('dict_name')
        self.FilterFinished.emit(filter)


class AddFilterInfoDialog(QDialog, Ui_AddFilterInfoDialog):
    FinishedDict = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(AddFilterInfoDialog, self).__init__(parent)
        self.setupUi(self)
        self.filter = collections.defaultdict(dict)
        self.button_tool_plus.clicked.connect(self.tool_button_add_to_dict)
        with open('../data/modtypes.json', 'r') as f:
            self.mod_types = json.load(f)
        self.comboBox_stat.activated.connect(self.populate_type_values)
        self.buttonBox.accepted.connect(self.send_dict)

    def populate_type_values(self, value):
        self.comboBox_type.clear()
        if value == 0:
            for type in self.mod_types:
                self.comboBox_type.addItem(type)
        if value == 1:
            props_types = ['Dps', 'Physical Dps', 'Elemental Dps', 'Attacks Per Second',
                           'Armour', 'Evasion Rating', 'Energy Shield', 'Physical Damage', 'Elemental Damage']
            for type in props_types:
                self.comboBox_type.addItem(type)

    def tool_button_add_to_dict(self):
        stat = self.comboBox_stat.currentText()
        type = self.comboBox_type.currentText()
        value = self.line_value.text()
        if stat == 'item_class':
            self.filter['item_class'] = value
        else:
            self.filter[stat][type] = value
        self.line_value.clear()
        self.text_show_current_dict.setText(json.dumps(self.filter, indent=4))
        logger.debug(self.filter)

    def send_dict(self):
        self.FinishedDict.emit(self.filter)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = StashDesign()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
