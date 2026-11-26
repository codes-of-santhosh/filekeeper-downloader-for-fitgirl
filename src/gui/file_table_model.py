from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from ..models import ResolvedFile

class FileTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files: list[ResolvedFile] = []
        self.headers = ["Check", "Filename", "Size", "Status", "Progress"]
        self.checked_states = []
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.files)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        file_item = self.files[row]
        
        if role == Qt.DisplayRole:
            if col == 1:
                return file_item.filename
            elif col == 2:
                return file_item.size
            elif col == 3:
                return file_item.status
            elif col == 4:
                return f"{file_item.progress:.1f}%"
                
        elif role == Qt.CheckStateRole and col == 0:
            return Qt.Checked if self.checked_states[row] else Qt.Unchecked
            
        elif role == Qt.TextAlignmentRole:
            if col in (2, 4):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        return None
        
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
            
        if role == Qt.CheckStateRole and index.column() == 0:
            self.checked_states[index.row()] = (value == Qt.Checked.value)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
            
        return False
        
    def flags(self, index):
        flags = super().flags(index)
        flags |= Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        return flags
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def set_files(self, files: list[ResolvedFile]):
        self.beginResetModel()
        self.files = files
        self.checked_states = [True for _ in files]
        self.endResetModel()

    def update_file_progress(self, row: int, status: str, progress: float):
        if 0 <= row < len(self.files):
            self.files[row].status = status
            self.files[row].progress = progress
            idx = self.index(row, 0)
            self.dataChanged.emit(self.index(row, 3), self.index(row, 4), [Qt.DisplayRole])
            
    def get_selected_files(self) -> list[tuple[int, ResolvedFile]]:
        return [(i, f) for i, (f, checked) in enumerate(zip(self.files, self.checked_states)) if checked]
        
    def set_all_checked(self, checked: bool):
        for i in range(len(self.checked_states)):
            self.checked_states[i] = checked
        if self.rowCount() > 0:
            self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, 0), [Qt.CheckStateRole])
        
    def invert_selection(self):
        for i in range(len(self.checked_states)):
            self.checked_states[i] = not self.checked_states[i]
        if self.rowCount() > 0:
            self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, 0), [Qt.CheckStateRole])

    def set_rows_checked(self, rows: list[int], checked: bool):
        if not rows:
            return
        for r in rows:
            if 0 <= r < len(self.checked_states):
                self.checked_states[r] = checked
                idx = self.index(r, 0)
                self.dataChanged.emit(idx, idx, [Qt.CheckStateRole])
