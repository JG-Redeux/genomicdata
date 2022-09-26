from PyQt5 import QtCore, QtWidgets, QtGui
import pandas as pd

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self.reorderID()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Orientation.Horizontal:
            try:
                return str(self._df.columns[section])
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Orientation.Vertical:
            try:
                # return self.df.index.tolist()
                return str(self._df.index[section])
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            if role == QtCore.Qt.ForegroundRole:
                try:
                    value = float(self._df.iloc[index.row(), index.column()])
                except BaseException:
                    return QtCore.QVariant()
                else:
                    if value < 0:
                        return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.red))

            if role == QtCore.Qt.TextAlignmentRole:
                try:
                    value = float(self._df.iloc[index.row(), index.column()])
                except BaseException:
                    return QtCore.QVariant(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                else:
                    return QtCore.QVariant(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignVCenter)

            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            try:
                value = float(self._df.iloc[index.row(), index.column()])
            except BaseException:
                return QtCore.QVariant(str(self._df.iloc[index.row(), index.column()]))
            else:
                if list(self._df.dtypes)[index.column()] == "dtype('int64')":
                    return QtCore.QVariant(format(self._df.iloc[index.row(), index.column()], '<d'))
                elif list(self._df.dtypes)[index.column()] == "dtype('O')":
                    return QtCore.QVariant(self._df.iloc[index.row(), index.column()])
                else:
                    return QtCore.QVariant(format(self._df.iloc[index.row(), index.column()]))

    # return QtCore.QVariant(str(self._df.iloc[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        self.reorderID()
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.reorderID()
        self.layoutChanged.emit()

    def reorderID(self):
        id_col = self._df.pop("ID")
        self._df.insert(0, "ID", id_col)

    def get_value(self, row, col):
        """[get value from dataframe[row,col]]

        Args:
            row ([int]): [row number]
            col ([int]): [col number]

        Returns:
            [object]: [value from dataframe[row,col]]
        """
        return self._df.iloc[row, col]

def FormatView(view, columnCount=0):
    view.setSortingEnabled(True)
    view.verticalHeader().setHidden(False)
    view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    #view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    # if columnCount != 0:
    # view.horizontalHeader().setSectionResizeMode(columnCount-1, QtWidgets.QHeaderView.Stretch)
    view.resizeColumnsToContents()
    view.setAlternatingRowColors(True)
    view.horizontalHeader().setStyleSheet("QHeaderView::section {background-color:lightblue;color: black;padding-left: 4px;border: 1px solid #6c6c6c;font: bold;}")
    # view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    view.horizontalHeader().setSectionsMovable(True)


def addActionColumn(tableView, model, tableName, func):
    columnPos = model.columnCount() - 1
    tableView.setColumnHidden(columnPos, False)

    rowCount = model.rowCount()
    for row in range(rowCount):
        iconDelete = QtGui.QIcon()
        iconDelete.addFile('logo/delete1.png')
        btnDelete = QtWidgets.QPushButton('')
        btnDelete.setIcon(iconDelete)
        btnDelete.clicked.connect(lambda: func(model))
        # SymbolCode = model.itemData(model.index(row,0))[0]
        btnDelete.setProperty("row", row)
        tableView.setIndexWidget(model.index(row, columnPos), btnDelete)


def load_table(tableView, model, df):
    # db = sqlite3.connect('AMS.db')
    # query = "select * from " + tableName + condition
    # df = pd.read_sql(query, con = db)
    rowCount = df.shape[0]
    columnCount = df.shape[1]
    model.setRowCount = rowCount
    model.setColumnCount = columnCount + 1
    headName = list(df)
    headName.append('Action')
    model.setHorizontalHeaderLabels(headName)
    for row in range(rowCount):
        for column in range(columnCount):
            item = QtGui.QStandardItem()
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

            itemValue = df.iloc[row, column]
            if type(itemValue).__name__ == 'int64':
                itemValue = int(itemValue)
            if type(itemValue).__name__ == 'float64':
                itemValue = float(itemValue)
                if itemValue < 0:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                itemValue = '{:.2f}'.format(itemValue)

            '''
            try:
                itemValue = float(df.iloc[row,column])
            except BaseException:
                itemValue = df.iloc[row,column]
            else:
                itemValue = QVariant('%.2f'%df.iloc[row,column])
                if itemValue < 0:
                    item.setForeground(QBrush(QColor(255, 0, 0)))
            '''
            item.setData(itemValue, QtCore.Qt.DisplayRole)
            # item.setEditable(False)
            model.setItem(row, column, item)

    tableView.setModel(model)

    tableView.setColumnHidden(columnCount, True)
    tableView.verticalHeader().setHidden(True)
    tableView.setSortingEnabled(True)
    tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    tableView.resizeColumnsToContents()
    tableView.horizontalHeader().setStyleSheet("QHeaderView::section {background-color:lightblue;color: black;padding-left: 4px;border: 1px solid #6c6c6c;font: bold;}")