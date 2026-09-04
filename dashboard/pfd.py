from PyQt6.QtCore import Qt     # imports core non-GUI utilities
from PyQt6.QtGui import QColor, QFont, QPainter     # Imports graphics classes for color managmnet
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget    # imports core graphical components used for layout managment

class AttitudeIndicator(QWidget):   # Defines a custom widget class serving as the canvas for the artificial horizon instrument
    """Renders a dynamic artifical horizon with a pitch ladder and roll rotation"""

    def __init__(self, parent=None):    # Constructor initializing the widget and setting baseline roll and pitch values to zero
        super().__init__(parent)        # calls the initalization constructor of the parent class
        self.roll = 0.0
        self.pitch = 0.0

    def set_attitude(self, roll, pitch):    # Updates the orientation state variables and calls
        self.roll = roll
        self.pitch = pitch
        self.update()

    def paintEvent(self, event):    # A built-in Qt event handler automatically invoked when the widget is exposed or refreshed
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    def paintEvent(self, event):   
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.roll)
        painter.translate(0, self.pitch * 5)  # Pitch translation factor

        # Sky-and-ground color scheme
        painter.setBrush(QColor(65, 155, 225))  # Sky
        painter.drawRect(-width, -height * 2, width * 2, height * 2)
        painter.setBrush(QColor(120, 70, 40))  # Ground
        painter.drawRect(-width, 0, width * 2, height * 2)

        painter.restore()

        # Fixed central aircraft symbol
        painter.setPen(QColor(255, 255, 0))
        painter.drawLine(
            int(center_x - 30), int(center_y), int(center_x - 10), int(center_y)
        )
        painter.drawLine(
            int(center_x + 10), int(center_y), int(center_x + 30), int(center_y)
        )
        painter.drawLine(
            int(center_x), int(center_y), int(center_x), int(center_y + 12)
        )

class PrimaryFlightDisplay(QFrame):     # Defines the high level container frame that groups the PFD compoents together
    """Container frame for the Phase 5 ground station PFD instruments"""

    def __init__(self, parent=None):    
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.attitude_indicator = AttitudeIndicator(self)
        layout.addWidget(self.attitude_indicator)

        # Real-time textual readouts formatted in a monospaced font[cite: 2]
        self.readouts_label = QLabel(
            "ALT: 0 ft | IAS: 0 kts | VS: 0 fpm | HDG: 0° | G: 1.0 | FUEL: 0 kg",
            self,
        )
        self.readouts_label.setFont(QFont("Monospace", 10))
        layout.addWidget(self.readouts_label)

# Public method designed to ingest real-time flight data parameters, update the horizon graphic, and format the text readout string
    def update_metrics(
        self, altitude, airspeed, vertical_speed, heading, g_load, fuel, roll, pitch
    ):  
        self.attitude_indicator.set_attitude(roll, pitch)
        text = (
            f"ALT: {altitude:.1f} ft | IAS: {airspeed:.1f} kts | "
            f"VS: {vertical_speed:.1f} fpm | HDG: {heading:.1f}° | "
            f"G: {g_load:.1f} | FUEL: {fuel:.1f} kg"
        )
        self.readouts_label.setText(text)