import sys
import serial   # for Arduino Python communication
import serial.tools.list_ports
import cv2      # for real-time camera feed using OpenCV
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QLCDNumber, QFileDialog
from drone import Ui_DroneDashboard
# from receiver import battery_voltage


class SerialThread(QThread):
    #data_received = pyqtSignal(str)
    data_received = pyqtSignal(dict)
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
        try:
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
        except serial.SerialException as e:
            print(f"Serial exception: {e}")
            self.running = False  # Graceful handling of permission errors

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

from PyQt5.QtWidgets import QLCDNumber

class MainWindow(QMainWindow, Ui_DroneDashboard):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_thread = None
        self.camera_thread = None

        print("MainWindow initialized")

        self.initialize_lcd_numbers()

        self.populate_com_ports()
        self.comboBoxPort.currentIndexChanged.connect(self.start_serial_thread)
        # self.Disconnect.clicked.connect(self.disconnect_serial)
        self.CaptureButton.clicked.connect(self.capture_image)
        
        self.camera_thread = CameraThread()
        self.camera_thread.frame_received.connect(self.update_camera_feed)
        self.camera_thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = None
        self.timer_started = False

        self.CloseButton.clicked.connect(self.close)  # Connect CloseButton to close method

    def initialize_lcd_numbers(self):
        self.lcdNumber = self.findChild(QLCDNumber, 'lcdNumber')
        self.lcdNumber_2 = self.findChild(QLCDNumber, 'lcdNumber_2')
        self.lcdNumber_3 = self.findChild(QLCDNumber, 'lcdNumber_3')
        self.lcdNumber_4 = self.findChild(QLCDNumber, 'lcdNumber_4')
        self.lcdNumber_5 = self.findChild(QLCDNumber, 'lcdNumber_5')
        self.lcdNumber_6 = self.findChild(QLCDNumber, 'lcdNumber_6')
        self.lcdNumber_7 = self.findChild(QLCDNumber, 'lcdNumber_7')
        self.lcdNumber_8 = self.findChild(QLCDNumber, 'lcdNumber_8')
        self.lcdNumber_9 = self.findChild(QLCDNumber, 'lcdNumber_9')
        self.lcdNumber_10 = self.findChild(QLCDNumber, 'lcdNumber_10')
        self.lcdNumber_11 = self.findChild(QLCDNumber, 'lcdNumber_11')
        self.lcdNumber_12 = self.findChild(QLCDNumber, 'lcdNumber_12')
        self.lcdNumber_13 = self.findChild(QLCDNumber, 'lcdNumber_13')
        self.lcdNumber_14 = self.findChild(QLCDNumber, 'lcdNumber_14')
        self.lcdNumber_15 = self.findChild(QLCDNumber, 'lcdNumber_15')

        print(f'lcdNumber_13: {self.lcdNumber_13}')
        print(f'lcdNumber_14: {self.lcdNumber_14}')

    def populate_com_ports(self):
        ports = serial.tools.list_ports.comports()
        print("Available COM ports:", [port.device for port in ports])
        for port in ports:
            self.comboBoxPort.addItem(port.device)

    def start_serial_thread(self):
        selected_port = self.comboBoxPort.currentText()
        print(f"Selected COM port: {selected_port}")
        if selected_port:
            if self.serial_thread:
                self.serial_thread.stop()
            self.serial_thread = SerialThread(selected_port)
            self.serial_thread.data_received.connect(self.update_telemetry_data)
            self.serial_thread.start()

    # def disconnect_serial(self):
    #     print("Disconnect button clicked")
    #     if self.serial_thread:
    #         self.serial_thread.stop()
    #         self.serial_thread = None 
    #         print("SerialThread disconnected")

    def update_telemetry_data(self, data):
        print(data, "telemetry_data")
        print("update_telemetry_data called")
        print("self:", self)
        print("data:", data)

        for key, value in data.items():
            print(f"Updating key: {key} with value: {value}")
            if key == 'Battery Voltage':
                if self.battery_status:
                    # self.battery_status.display(float(value))
                    self.battery_status.setText(f"{float(value):.2f}") 
                    
                else:
                    print("battery status is not initialized")
            elif key == 'Roll':
                if self.lcdNumber_4:
                    self.lcdNumber_4.display(float(value))
                else:
                    print("lcdNumber_4 is not initialized")
            elif key == 'Pitch':
                if self.lcdNumber_5:
                    self.lcdNumber_5.display(float(value))
                else:
                    print("lcdNumber_5 is not initialized")
            elif key == 'Heading':
                if self.lcdNumber_6:
                    self.lcdNumber_6.display(float(value))
                else:
                    print("lcdNumber_6 is not initialized")
            elif key == 'Number of Satellites':
                if self.lcdNumber_7:
                    self.lcdNumber_7.display(int(value))
                else:
                    print("lcdNumber_7 is not initialized")
            elif key == 'Main Mode':
                if self.mainmode_status:
                    self.mainmode_status.display(str(value))
                else:
                    print("mainmode status is not initialized")
            elif key == 'Sub Mode':
                if self.submode_status:
                    self.submode_status.display(str(value))
                else:
                    print("submode status is not initialized")
            elif key == 'Error':
                if self.error_status:
                    # self.error_status.display(int(value))
                      self.error_status.setText(f"{float(value):.2f}") 
                else:
                    print("error status is not initialized")
            elif key == 'GPS Status':
                if self.gps_status_status:
                    # self.error_status.display(int(value))
                      self.gps_status.setText(f"{float(value):.2f}") 
                else:
                    print("error status is not initialized")
            elif key == 'Latitude':
                if self.lcdNumber:
                    self.lcdNumber.display(float(value))
                else:
                    print("lcdNumber is not initialized")
            elif key == 'Longitude':
                if self.lcdNumber_3:
                    self.lcdNumber_3.display(float(value))
                else:
                    print("lcdNumber_3 is not initialized")
            elif key == 'Altitude':
                if self.lcdNumber_2:
                    self.lcdNumber_2.display(float(value))
                else:
                    print("lcdNumber_2 is not initialized")
            elif key == 'Distance Right':
                if self.lcdNumber_9:
                    self.lcdNumber_9.display(int(value))
                else:
                    print("lcdNumber_9 is not initialized")
            elif key == 'Distance Left':
                if self.lcdNumber_10:
                    self.lcdNumber_10.display(int(value))
                else:
                    print("lcdNumber_10 is not initialized")
            elif key == 'Distance Upper':
                if self.lcdNumber_12:
                    self.lcdNumber_12.display(int(value))
                else:
                    print("lcdNumber_12 is not initialized")
            elif key == 'Armed or Not':
                if self.armed_status:
                    self.armed_status.setText(str(value))
                else:
                    print("armed status is not initialized")
                if value.lower() == 'yes' and not self.timer_started:
                    self.timer_started = True
                    self.start_timer()

    def update_camera_feed(self, image):
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
            pixmap = self.labelCameraFeed.pixmap()
            if pixmap and not pixmap.isNull():
                pixmap.save(file_path)

    def showEvent(self, event):
        self.showFullScreen()

    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
        if self.camera_thread:
            self.camera_thread.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())