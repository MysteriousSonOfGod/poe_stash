# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/create_filter_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CreateFilterDialog(object):
    def setupUi(self, CreateFilterDialog):
        CreateFilterDialog.setObjectName("CreateFilterDialog")
        CreateFilterDialog.resize(400, 300)
        self.formLayout = QtWidgets.QFormLayout(CreateFilterDialog)
        self.formLayout.setObjectName("formLayout")
        self.label_filter_name = QtWidgets.QLabel(CreateFilterDialog)
        self.label_filter_name.setObjectName("label_filter_name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_filter_name)
        self.label_filter_and = QtWidgets.QLabel(CreateFilterDialog)
        self.label_filter_and.setObjectName("label_filter_and")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_filter_and)
        self.label_filter_or = QtWidgets.QLabel(CreateFilterDialog)
        self.label_filter_or.setObjectName("label_filter_or")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_filter_or)
        self.edit_name = QtWidgets.QLineEdit(CreateFilterDialog)
        self.edit_name.setObjectName("edit_name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.edit_name)
        self.combbox_filter_or = QtWidgets.QComboBox(CreateFilterDialog)
        self.combbox_filter_or.setObjectName("combbox_filter_or")
        self.combbox_filter_or.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.combbox_filter_or)
        self.button_filter_info = QtWidgets.QPushButton(CreateFilterDialog)
        self.button_filter_info.setObjectName("button_filter_info")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.button_filter_info)
        self.buttonBox = QtWidgets.QDialogButtonBox(CreateFilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.textBrowser = QtWidgets.QTextBrowser(CreateFilterDialog)
        self.textBrowser.setObjectName("textBrowser")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.textBrowser)

        self.retranslateUi(CreateFilterDialog)
        self.buttonBox.rejected.connect(CreateFilterDialog.reject)
        self.buttonBox.accepted.connect(CreateFilterDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(CreateFilterDialog)

    def retranslateUi(self, CreateFilterDialog):
        _translate = QtCore.QCoreApplication.translate
        CreateFilterDialog.setWindowTitle(_translate("CreateFilterDialog", "Dialog"))
        self.label_filter_name.setText(_translate("CreateFilterDialog", "Filter Name"))
        self.label_filter_and.setText(_translate("CreateFilterDialog", "Filter AND"))
        self.label_filter_or.setText(_translate("CreateFilterDialog", "Filter OR"))
        self.combbox_filter_or.setItemText(0, _translate("CreateFilterDialog", "<Add Filter Info>"))
        self.button_filter_info.setText(_translate("CreateFilterDialog", "Add Filter Info"))
