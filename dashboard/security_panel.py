from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

    # Defines the SecurityPanel class, inheriting from QWidget to make it a UI component
class SecurityPanel(QWidget):

    def __init__(self, parent=None):   # Constructor method that runs when the panel is created
        super().__init__(parent)       # Initalize the parent QWidget class
        self.init_ui()                 # Call the method to build the user interface elements

    def init_ui(self):                 # sets up the main vertical layout for this panel
        layout = QVBoxLayout(self)

        self.table = QTableWidget()    # Creates a grid table widget
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(   # Defines the number of columns (Timestamp, severity, etc.)
            ["Timestamp", "Severity", "Threat Type", "Description", "ML Confidence"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Set column headers
        self.table.setEditriggers(QTableWidget.EditTrigger.NoEditTriggers)          # Ensure clicking selects the whole row
        self.table.itemSelectionChanged.connect(self.on_row_selected)               # Make cells read only
        layout.addWidget(self.table)                                                # Trigger function when a row is clicked

        details_group = QGroupBox("Incident Details")   # Incident details group box setup
        details_layout = QVBoxLayout()                  # Creates a boxed container group for details
        self.details_label = QLabel(                    # Creates a vertical layout for the box
            "Select an event from the table to view details."   
        )

        self.details_label.setWordWrap(True)            # Label showing selected info
        details_layout.addWidget(self.details_label)    # Allow text to wrap to multiple lines automatically
        details_group.setLayout(details_layout)         # Apply layout to the group box
        layout.addWidget(self.table)                    # Add group box to the main layout

    def update_events(self, events):                    # Method to refresh the table with a new list
        self.table.setRowCount(len(events))             
        for row, event in enumerate(events):            # Resize table row count to match event list length
            self.table.setItem(row, 0, QTableWidgetItem(event.get("timestamp", "")))

            severity_item = QTableWidgetItem(event.get("severity", "LOW"))  # Creates item for severity level in column 1
            self.set_severity_color(severity_item, event.get("severity", "LOW")) 
            self.table.setItem(row, 1, severity_item)

            self.table.setItem(
                row, 2, QTableWidgetItem(event.get("threat_type", ""))
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(event.get("description", ""))
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(str(event.get("confidence", "")))
            )

        def set_severity_color(self, item, severity):   # Helper dictionary mapping severity strings to background QColors
            colors = {
                "CRITICAL": QColor(255, 100, 100),
                "HIGH": QColor(255, 165, 0),
                "MEDIUM": QColor(255, 255, 100),
                "LOW": QColor(100, 255, 100),
            }
            if severity in colors:
                item.setBackground(colors[severity])    # Apply the background color to cell

        def on_row_selected(self):                      # Triggered automatically when an operator clicks a table row
            selected_rows = self.table.selectionModel().selectedRows()  
            if selected_rows:      
                row = selected_rows[0].row()
                desc = self.table.item(row, 3).text()
                ts = self.table.item(row, 0).text()
                sev = self.table.item(row, 1).text()
                self.details_label.setText(
                    f"[{ts}] Severity: {sev}\nDescription: {desc}"
                )