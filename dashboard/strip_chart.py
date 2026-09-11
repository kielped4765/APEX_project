from pyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel    # Imports the base widget, vertical layout manager, and text label components from PyQt6
import pyqtgrapgh as pg     # imports the pyqtgraph module under the standard pg for rendering trelemetry plots

pg.setConfigOption('background', (10, 15, 28))  # sets the global background color for all pyqtgraph widgets
pg.setConfigOption('foreground', (100, 200, 255))   # sets the global foreground color for all pyqtgraph widgets

CHANNELS = {
   'altitude_m': {'color': '#5DADE2', 'label': 'Altitude (m)'},
    'airspeed_mps': {'color': '#58D68D', 'label': 'Airspeed (m/s)'},
    'vertical_speed': {'color': '#F39C12', 'label': 'Vert Speed (m/s)'},
    'g_load': {'color': '#E74C3C', 'label': 'G-Load'} 
}   # defines the configuration dictionary mappying internal channel keys

class TelemetryStripChart(QWidget):     # Declares custom class inheriting from PyQt's
    def __init__(self):                 # constructor method is instantiated 
        super().__init__()              # initalizes the underlying QWidget parent class
        layout = QVBoxLayout(self)      # Creates a vertical box layout to stack child elements 
        title = QLabel("TELEMETRY STRIP CHART")
        title.setStyleSheet('color:#5DAE2;font-size:10px;font-weight:bold;')
        layout.addWidget(title)

        self.curves = {}    # Initializes an empty dictionary to keep track of indivdual plot curve references
        for ch, cfg in CHANNELS.items():    # Iterates over each telemetry channel defined in the CHANNELS dictionary
            pw = pg.PlotWidget(title=cfg['label'])  # Creates a pyqtgraph instance labeled with the channels description
            pw.setMaximumHeight(155)                # Constrains the height of the individual plot to 155 pixels to fit multiple charts
            pw.showGrid(x=True, y=True, alpha=0.3)
            pw.getAxis('left').setWidth(60)
            self.curves[ch] = pw.plot(pen=pg.mkPen(cfg['color'], width=2))
            layout.addWidget(pw)

    def update_series(self, records: list):     # Defines the public method to feed new data records into the charts
        for ch, curve in self.curves.items():   # loops through ever channel and its matching graph curve
            y = [r.get(ch, 0.0) or 0.0 for r in records]    # extracts a list of data points for the specific channel from the inputs records
            curve.setData(y=y)                              # pushes the newly parsed y-values to the graph curve