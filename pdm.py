from PyQt5 import QtCore
import pandas as pd

class DataFrameModel(QtCore.QAbstractTableModel):
    """[Class which interfaces QT and Pandas dataframes]

    Args:
        QtCore ([QtCore]): [Inherits QAbstractTableModel from QtCore]

    Returns:
        [dataframe]: [dataframe outputed into QTableView]
    """
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        """[init the instance]

        Args:
            df ([dataframe], optional): [dataframe to act as model]. Defaults to pd.DataFrame().
            parent ([object], optional): [parent object]. Defaults to None.
        """
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        """[set dataframe as the model]

        Args:
            dataframe ([dataframe]): [dataframe to be set as model]
        """
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        """[method to output the class dataframe]

        Returns:
            [dataframe]: [returns the dataframe]
        """
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        """[get header data from dataframe]

        Args:
            section (int): [column index]
            orientation (QtCore.Qt.Orientation): [orientation from Qt5]
            role (int, optional): [role from Qt5]. Defaults to QtCore.Qt.DisplayRole.

        Returns:
            [QtCore.QVariant]: [Qt5 construct]
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """[get model row count]

        Args:
            parent ([object], optional): [object to inherit]. Defaults to QtCore.QModelIndex().

        Returns:
            [int]: [row count]
        """
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """[get model column count]

        Args:
            parent ([object], optional): [object to inherit]. Defaults to QtCore.QModelIndex().

        Returns:
            [int]: [columns size (count)]
        """
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """[define model data]

        Args:
            index ([int]): [dataframe index number]
            role (int, optional): [role from Qt5]. Defaults to QtCore.Qt.DisplayRole.

        Returns:
            [objects]: [dataframe objects]
        """
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        """[get role names]

        Returns:
            [dict]: [dict with roles]
        """
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles

    def sort(self, column):
        """[sort dataframe by column]

        Args:
            column ([string]): [column to sort by to]
        """
        colname = self._dataframe.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._dataframe.sort_values(colname, ascending=QtCore.Qt.AscendingOrder, inplace=True)
        #self._dataframe.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

    def get_value(self, row, col):
        """[get value from dataframe[row,col]]

        Args:
            row ([int]): [row number]
            col ([int]): [col number]

        Returns:
            [object]: [value from dataframe[row,col]]
        """
        return self._dataframe.iloc[row, col]

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and QtCore.Qt.Orientation == QtCore.Qt.Horizontal:
            return self._dataframe.columns[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)
