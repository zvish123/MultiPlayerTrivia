from PyQt5.QtWidgets import QStyledItemDelegate

class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, perant, option, index):
        print("create_editor fire")
        return