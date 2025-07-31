from threading import Thread
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import *

from item_models import _ModelTemplate

#############################################################################

class _WidgetTemplate(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # middle buttons
        self.wButtonLoadA = QPushButton('🡄 Load')
        self.wButtonLoadB = QPushButton('Load 🡆')
        self.wButtonTransfer = QPushButton('─ Transfer →')
        self.wButtonRevTransfer = QPushButton('← Transfer ─')
        self.wButtonSubmitA = QPushButton('🡄 SUBMIT')
        self.wButtonSubmitB = QPushButton('SUBMIT 🡆')
        
        self.wButtonLoadA.setStyleSheet("QPushButton {width: 100px; height: 32px; }")
        self.wButtonLoadB.setStyleSheet("QPushButton {width: 100px; height: 32px; }")
        self.wButtonTransfer.setStyleSheet("QPushButton {width: 150px; height: 32px; }")
        self.wButtonRevTransfer.setStyleSheet("QPushButton {width: 150px; height: 32px; }")
        self.wButtonSubmitA.setStyleSheet("QPushButton {width: 100px; height: 32px; }")
        self.wButtonSubmitB.setStyleSheet("QPushButton {width: 100px; height: 32px; }")

        self.wButtonLayout = QGridLayout()
        self.wButtonLayout.setContentsMargins(20, 100, 20, 100);
        self.wButtonLayout.setRowStretch(0, 1)
        self.wButtonLayout.addWidget(self.wButtonLoadA, 1, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.wButtonLayout.addWidget(self.wButtonLoadB, 1, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.wButtonLayout.addWidget(self.wButtonTransfer, 3, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonRevTransfer, 4, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonSubmitA, 5, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonSubmitB, 5, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.setRowStretch(6, 1)

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
        self.wTableViewA.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

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
        self.wTableViewB.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

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

        t = Thread(self._loadData(self.parent.appA, self.wTableViewA))
        t.start()

    def loadBData(self):
        """Load B table."""
        
        t = Thread(self._loadData(self.parent.appB, self.wTableViewB))
        t.start()

    def transferAToB(self):
        """Transfer items from A to B."""

        if self.parent.is_busy:
            return

        t = Thread(self._transferData(self.parent.appA, self.wTableViewA,
                                      self.parent.appB, self.wTableViewB))
        t.start()

    def transferBToA(self):
        """Transfer items from B to A."""

        if self.parent.is_busy:
            return

        t = Thread(self._transferData(self.parent.appB, self.wTableViewB,
                                      self.parent.appA, self.wTableViewA))
        t.start()

    def submitA(self) -> None:
        """Submit changed items in A."""

        if self.parent.is_busy:
            return

        t = Thread(self._submitData(self.parent.appA, self.wTableViewA))
        t.start()

    def submitB(self):
        """Submit changed items in B."""

        if self.parent.is_busy:
            return

        t = Thread(self._submitData(self.parent.appB, self.wTableViewB))
        t.start()

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
