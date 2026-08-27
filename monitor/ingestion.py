import socket                   # Pythons built in networking data structures, logging utilites and project config
import queue
import threading
import logging
import config

class TelemetryIngestion:       # Defines Object oriented class to manage network ingestion
    def __init__(self, packet_queue: queue.Queue):
            self.packet_queue = packet_queue            # Initalizes internal instance variables to track state (the other variable for tracking data)
            self.running = False
            self.socket  = None
            self.thread  = None

    def start(self):        # Defines the method for initalizing network resources
          """Binds the UDP socket and starts the background ingestion thread."""
          self.socket = socket.socket(socket.AF.INET, socket.SOCK_DGRAM)    # Creates new network socket using IPv4 & UDP
          self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1014)  # Modifies socket options to increase the operating system's receive buffer
          self.socket.bind((config.LISTEN_IP, config.LISTEN_PORT))                  # Binds the UDP socket to a specific local IP address and port
          self.socket.settimeout(1.0)                                               # Sets a 1 second timeout on the socket receive function

          self.running = True                                                       # Set the control to true
          self.thread  = threading.Thread(target=self._listen_loop, daemon=True)    # Creates a background thread pointing to the _listen_loop method
          self.thread.start()
          logging.info(f"Ingestion started on {config.LISTEN_IP}:{config.LISTEN_PORT}")

    def _listen_loop(self):     # Defines the continuous loop running on the background thread
          """Continously pulls raw bytes from the network socket into the queue."""
          while self.running:   # Keep running as long as the self.running remains true
            try:                # Wraps the network call in a try/except block to catch timeouts and loops back to start
                raw_packet, addr = self.socket.recvfrom(4096)  # Blocks briefly to pull up to 4096 bytes of raw incoming UDP packet data 
                try:
                    self.packet_queue.put_nowait(raw_packet)   # Attempts to instantly place the raw packet into the shared queue
                except queue.Full:
                     logging.warning("Packet queue full! Dropping incoming telemetry frame.")
            except socket.timeout:
                 continue
            except Exception as e:
                 if self.running:
                      logging.error(f"Socket error during ingestion:v {e}")

    def stop(self):     # Defines the cleanup method
         """Stops the ingestion loop and cleans up network resources."""
         self.running = False       # Sets the loop control flag to false
         if self.thread:            
              self.thread.join(timeout=2.0)     # Waits up to 2 seconds for the background thread to finish its current cycle and shut down safely
        if self.socket:                         
            self.socket.close()                 # Closes the network socket and releases the port back to the operating system
        logging.info("Telemetry ingestion stopped.")