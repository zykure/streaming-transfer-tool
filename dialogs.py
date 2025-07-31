from PyQt6.QtWidgets import QDialog, QWidget, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout

#############################################################################

class MessageDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, msg: str):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        
        # text label with links
        self.textLabel = QLabel(msg)
        self.textLabel.openExternalLinks()
    
        # buttons
        QBtn = QDialogButtonBox.StandardButton.Ok
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        
        # layout 
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textLabel)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)
        
#############################################################################

class InputDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, msg: str, hint: str = ""):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        
        # text label with links
        self.textLabel = QLabel(msg)
        self.textLabel.openExternalLinks()
        
        # input field
        self.textInput = QLineEdit()
        self.textInput.setPlaceholderText(hint)
    
        # buttons
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # layout 
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textLabel)
        self.layout.addWidget(self.textInput)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)
        
    def textValue(self):
        return self.textInput.text()
        