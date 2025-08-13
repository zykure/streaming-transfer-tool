from PyQt6.QtWidgets import *

#############################################################################

class AppInfoWidget(QWidget):
    def __init__(self, name: str):
        super().__init__()
        
        self.name = name
        self.app = None
        
        label1 = QLabel(f"Service {self.name}:")
        self.wAppNameLabel = QLabel()
       
        label1.setStyleSheet("QLabel {font-size: 16pt; }")
        self.wAppNameLabel.setStyleSheet("QLabel {font-size: 16pt; }")
        
        label2 = QLabel("User ID:")
        self.wUserIdLabel = QLabel()
        
        label3 = QLabel("Display Name:")
        self.wDisplayNameLabel = QLabel()

        label4 = QLabel("Client ID:")
        self.wClientIdLabel = QLabel()
        
        label5 = QLabel("Client Secret:")
        self.wClientSecretLabel = QLabel()

        # layout
        self.wLayout = QGridLayout()
        self.wLayout.setRowStretch(0, 1)
        self.wLayout.addWidget(label1, 1, 0, 1, 1)
        self.wLayout.addWidget(label2, 2, 0, 1, 1)
        self.wLayout.addWidget(label3, 3, 0, 1, 1)
        self.wLayout.addWidget(label4, 4, 0, 1, 1)
        self.wLayout.addWidget(label5, 5, 0, 1, 1)
        self.wLayout.addWidget(self.wAppNameLabel, 1, 1, 1, 1)
        self.wLayout.addWidget(self.wUserIdLabel, 2, 1, 1, 1)
        self.wLayout.addWidget(self.wDisplayNameLabel, 3, 1, 1, 1)
        self.wLayout.addWidget(self.wClientIdLabel, 4, 1, 1, 1)
        self.wLayout.addWidget(self.wClientSecretLabel, 5, 1, 1, 1)
        self.wLayout.setRowStretch(6, 1)
        
        self.setLayout(self.wLayout)  # override default layout
        
    def setApp(self, app):
        self.app = app
        
        self.wAppNameLabel.setText(f"<b>{self.app.name}</b>")

        hidden_secret = ""
        if self.app.client_secret:
            hidden_secret = self.app.client_secret[:-8] + "********"  # partially hide secret

        self.wUserIdLabel.setText(f"{self.app.uid}")
        self.wDisplayNameLabel.setText(f"{self.app.display_name}")
        self.wClientIdLabel.setText(f"{self.app.client_id}")
        self.wClientSecretLabel.setText(hidden_secret)
        
        self.update()
