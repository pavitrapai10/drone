import sys
import serial   # for Arduino Python communication
import serial.tools.list_ports
import cv2      # for real-time camera feed using OpenCV
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel
from drone import Ui_DroneDashboard
# from receiver import battery_voltage


class SerialThread(QThread):
    data_received = pyqtSignal(str)
#
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        print(f"SerialThread initialised with port : {self.port}")

    # def run(self):
    #     with serial.Serial(self.port, 9600, timeout=1) as ser:
    #         while self.running:
    #             data = ser.readline().decode().strip()
    #             if data:
    #                 self.data_received.emit(data)

    def run(self):
        print("SerialThread started")
        with serial.Serial(self.port, 9600, timeout=1) as ser:
            while self.running:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(f"Received line: {line}")
                    key_value = line.split(':')
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        print(f"Parsed key: {key}, value: {value}")
                        self.data_received.emit({key: value})

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class CameraThread(QThread):
    frame_received = pyqtSignal(QImage)

    def __init__(self, camera_port=0):
        super().__init__()
        self.camera_port = camera_port
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.camera_port)
        while self.running:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_received.emit(qt_image)

    def stop(self):
        self.running = False
        print("CameraThread stopping")
        self.quit()
        self.wait()

class MainWindow(QMainWindow, Ui_DroneDashboard):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_thread = None
        self.camera_thread = None

        print("MainWindow initialized")

        self.populate_com_ports()
        self.comboBoxPort.currentIndexChanged.connect(self.start_serial_thread)
        self.Disconnect.clicked.connect(self.disconnect_serial)
        self.CaptureButton.clicked.connect(self.capture_image)
        self.lcdNumber = self.findChild(QLabel, 'lcdNumber')

        self.camera_thread = CameraThread()
        self.camera_thread.frame_received.connect(self.update_camera_feed)
        self.camera_thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = None
        self.timer_started = False #<-------------------------------------

        self.CloseButton.clicked.connect(self.close)  # Connect CloseButton to close method

        # Call start_timer to start the timer when the application starts
        #self.start_timer()


    def populate_com_ports(self):
        ports = serial.tools.list_ports.comports()
        print("Available COM ports:", [port.device for port in ports])
        for port in ports:
            self.comboBoxPort.addItem(port.device)

    def start_serial_thread(self):
        selected_port = self.comboBoxPort.currentText()
        print(f"Selected COM port")
        if selected_port:
            if self.serial_thread:
                self.serial_thread.stop()
            self.serial_thread = SerialThread(selected_port)
            self.serial_thread.data_received.connect(self.update_telemetry_data)
            self.serial_thread.start()

    def disconnect_serial(self):
        print("Disconnect button clicked")
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None 
            print("SerialThread disconnected") # Clear the serial thread instance
            # Optionally clear UI or update status for disconnected state

    def update_telemetry_data(self, data):
        print(data, "telemetry_data")
         # Print self and data
        print("update_telemetry_data called")
        print("self:", self)
        print("data:", data)

         # Parse the data dictionary and update telemetry fields accordingly
        for key, value in data.items():
            print(f"Updating key: {key} with value: {value}")
            if key == 'Battery Voltage':
                self.lcdNumber.display(float(value))
            elif key == 'Roll':
                self.lcdNumber_2.display(float(value))
            elif key == 'Pitch':
                self.lcdNumber_3.display(float(value))
            elif key == 'Heading':
                self.lcdNumber_4.display(float(value))
            elif key == 'Number of Satellites':
                self.lcdNumber_5.display(int(value))
            elif key == 'Mode':
                self.lcdNumber_6.display(int(value))
            elif key == 'Error':
                self.lcdNumber_7.display(int(value))
            elif key == 'Latitude':
                self.lcdNumber_8.display(float(value))
            elif key == 'Longitude':
                self.lcdNumber_9.display(float(value))
            elif key == 'Altitude':
                self.lcdNumber_10.display(float(value))
            elif key == 'Distance Right':
                self.lcdNumber_11.display(int(value))
            elif key == 'Distance Left':
                self.lcdNumber_12.display(int(value))
            elif key == 'Distance Upper':
                self.lcdNumber_13.display(int(value))
            elif key == 'Temperature':
                self.lcdNumber_14.display(float(value))  # Adjust if needed
            elif key == 'Armed or Not':
                self.lcdNumber_15.display(value)  # Adjust if needed
                if value.lower() == 'yes' and not self.timer_started: #<--------------------------
                    self.timer_started = True
                    self.start_timer()

        # fields = data.split(',')
        # if len(fields) >= 12:
        #     self.lcdNumber.display(fields[0])  # Assuming field 0 is latitude
        #     self.lcdNumber_2.display(fields[1])
        #     self.lcdNumber_3.display(fields[2])
        #     self.lcdNumber_4.display(fields[3])
        #     self.lcdNumber_5.display(fields[4])
        #     self.lcdNumber_6.display(fields[5])
        #     self.lcdNumber_7.display(fields[6])
        #     self.lcdNumber_8.display(fields[7])
        #     self.lcdNumber_9.display(fields[8])
        #     self.lcdNumber_10.display(fields[9])
        #     self.lcdNumber_11.display(fields[10])
        #     self.lcdNumber_12.display(fields[11])
    # #check for armed status and start the timer
    # for field in fields:
    #     key_value=field.split(':')
    #     if len(key_value) == 2:
    #         key=key_value[0].strip()
    #         value=key_value[1].strip()
    #         if key == 'Armed or Not' and value.lower()=='Yes' and not self.timer_started:
    #             self.timer_started = True
    #             self.start_timer()

    def update_camera_feed(self, image):
        print("update_camera_feed called")
        self.labelCameraFeed.setPixmap(QPixmap.fromImage(image))

    def start_timer(self):
        print("Timer started")
        self.start_time = time.time()
        self.timer.start(1000)

    def update_timer(self):
        elapsed_time = time.time() - self.start_time
        print(f"Elapsed time: {elapsed_time}")
        self.LabelTimer.setText(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

    def capture_image(self):
        print("Capture button clicked")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter("Images (*.png *.jpg *.bmp)")

        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            print(f"Saving captured image to :{file_path}")
            # Save the captured image
            pixmap = self.labelCameraFeed.pixmap()
            if pixmap and not pixmap.isNull():
                pixmap.save(file_path)

    def showEvent(self, event):
        self.showFullScreen()  # Set window to fullscreen when shown

    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
        if self.camera_thread:
            self.camera_thread.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
