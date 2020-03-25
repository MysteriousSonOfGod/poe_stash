# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/add_filter_info.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddFilterInfoDialog(object):
    def setupUi(self, AddFilterInfoDialog):
        AddFilterInfoDialog.setObjectName("AddFilterInfoDialog")
        AddFilterInfoDialog.resize(469, 397)
        self.formLayout = QtWidgets.QFormLayout(AddFilterInfoDialog)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(AddFilterInfoDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.comboBox_stat = QtWidgets.QComboBox(AddFilterInfoDialog)
        self.comboBox_stat.setObjectName("comboBox_stat")
        self.comboBox_stat.addItem("")
        self.comboBox_stat.addItem("")
        self.comboBox_stat.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_stat)
        self.label_2 = QtWidgets.QLabel(AddFilterInfoDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox_type = QtWidgets.QComboBox(AddFilterInfoDialog)
        self.comboBox_type.setObjectName("comboBox_type")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_type)
        self.label_4 = QtWidgets.QLabel(AddFilterInfoDialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.line_value = QtWidgets.QLineEdit(AddFilterInfoDialog)
        self.line_value.setObjectName("line_value")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.line_value)
        self.text_show_current_dict = QtWidgets.QTextBrowser(AddFilterInfoDialog)
        self.text_show_current_dict.setObjectName("text_show_current_dict")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.text_show_current_dict)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddFilterInfoDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.button_tool_plus = QtWidgets.QToolButton(AddFilterInfoDialog)
        self.button_tool_plus.setObjectName("button_tool_plus")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.button_tool_plus)

        self.retranslateUi(AddFilterInfoDialog)
        self.buttonBox.accepted.connect(AddFilterInfoDialog.accept)
        self.buttonBox.rejected.connect(AddFilterInfoDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddFilterInfoDialog)

    def retranslateUi(self, AddFilterInfoDialog):
        _translate = QtCore.QCoreApplication.translate
        AddFilterInfoDialog.setWindowTitle(_translate("AddFilterInfoDialog", "Dialog"))
        self.label.setText(_translate("AddFilterInfoDialog", "Stat"))
        self.comboBox_stat.setItemText(0, _translate("AddFilterInfoDialog", "mods"))
        self.comboBox_stat.setItemText(1, _translate("AddFilterInfoDialog", "props"))
        self.comboBox_stat.setItemText(2, _translate("AddFilterInfoDialog", "item_class"))
        self.label_2.setText(_translate("AddFilterInfoDialog", "Type"))
        self.label_4.setText(_translate("AddFilterInfoDialog", "Value"))
        self.button_tool_plus.setText(_translate("AddFilterInfoDialog", "+"))
