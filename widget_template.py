from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import *

from item_models import _ModelTemplate

#############################################################################

class _WidgetTemplate(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # middle buttons
        self.wButtonLoadA = QPushButton('< Load')
        self.wButtonLoadB = QPushButton('Load >')
        self.wButtonTransfer = QPushButton('>> Transfer >>')
        self.wButtonRevTransfer = QPushButton('<< Transfer <<')
        self.wButtonSubmitA = QPushButton('< SUBMIT')
        self.wButtonSubmitB = QPushButton('SUBMIT >')

        self.wButtonLayout = QGridLayout()
        self.wButtonLayout.setContentsMargins(20, 100, 20, 100);
        self.wButtonLayout.addWidget(self.wButtonLoadA, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.wButtonLayout.addWidget(self.wButtonLoadB, 3, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.wButtonLayout.addWidget(self.wButtonTransfer, 5, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonRevTransfer, 6, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonSubmitA, 8, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonSubmitB, 8, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)

        # left table
        self.wButtonLoadA.clicked.connect(self.loadAData)
        self.wButtonLoadB.clicked.connect(self.loadBData)
        self.wButtonTransfer.clicked.connect(self.transferAToB)
        self.wButtonRevTransfer.clicked.connect(self.transferBToA)
        self.wButtonSubmitA.clicked.connect(self.submitA)
        self.wButtonSubmitB.clicked.connect(self.submitB)

        self.wTableModelA = _ModelTemplate()
        self.wTableViewA = QTableView()
        self.wTableViewA.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewA.verticalHeader().hide()
        self.wTableViewA.setModel(self.wTableModelA)

        self.wLabelA = QLabel()
        self.wLabelA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wLabelA.setStyleSheet("QLabel {font-size: 20pt; font-weight: bold; text-align: center}")

        self.wLayoutA = QVBoxLayout()
        self.wLayoutA.addWidget(self.wLabelA)
        self.wLayoutA.addWidget(self.wTableViewA)

        # right table
        self.wTableModelB = _ModelTemplate()
        self.wTableViewB = QTableView()
        self.wTableViewB.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewB.verticalHeader().hide()
        self.wTableViewB.setModel(self.wTableModelB)

        self.wLabelB = QLabel()
        self.wLabelB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wLabelB.setStyleSheet("QLabel {font-size: 20pt; font-weight: bold; text-align: center}")

        self.wLayoutB = QVBoxLayout()
        self.wLayoutB.addWidget(self.wLabelB)
        self.wLayoutB.addWidget(self.wTableViewB)

        # signals
        self.wTableViewA.verticalScrollBar().valueChanged.connect(self.scrollTableA)
        self.wTableViewB.verticalScrollBar().valueChanged.connect(self.scrollTableB)

    def reset(self):
        """Clear table data and reset widgets."""

        self.wTableModelA.clear()
        self.wTableModelB.clear()

        if self.parent.appA:
            self.wLabelA.setText(self.parent.appA.name)
        if self.parent.appB:
            self.wLabelB.setText(self.parent.appB.name)

    def scrollTableA(self):
        """Synchronize B with A scroll bar."""

        self._scrollTable(self.wTableViewA, self.wTableViewB)

    def scrollTableB(self):
        """Synchronize A with B scroll bar."""

        self._scrollTable(self.wTableViewB, self.wTableViewA)

    def loadAData(self):
        """Load A table."""

        self._loadData(self.parent.appA, self.wTableViewA)

    def loadBData(self):
        """Load B table."""

        self._loadData(self.parent.appB, self.wTableViewB)

    def transferAToB(self):
        """Transfer items from A to B."""

        self._transferData(self.parent.appA, self.wTableViewA,
                           self.parent.appB, self.wTableViewB)

    def transferBToA(self):
        """Transfer items from B to A."""

        self._transferData(self.parent.appB, self.wTableViewB,
                           self.parent.appA, self.wTableViewA)

    def submitA(self) -> None:
        """Submit changed items in A."""

        self._submitData(self.parent.appA, self.wTableViewA)

    def submitB(self):
        """Submit changed items in B."""

        self._submitData(self.parent.appB, self.wTableViewB)

    def _scrollTable(self, viewA: QTableView, viewB: QTableView):

        modelA = viewA.model()
        modelB = viewB.model()

        a_row = viewA.indexAt(QPoint(0, 0)).row()  # top row
        if a_row:
            name = modelA.names[a_row]
            if name in modelB.names:
                b_row = modelB.names.index(name)
                if b_row:
                    viewB.scrollTo(modelB.createIndex(b_row, 0))
                    viewB.update()

    def _loadData(self, app, view: QTableView):
        return

    def _transferData(self, appA, viewA: QTableView, appB, viewB: QTableView):
        return

    def _submitData(self, app, view: QTableView):
        return
