from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import QMainWindow,QMessageBox,QLineEdit,QButtonGroup
from PyQt5.QtCore import QMutex
from PyQt5.QtCore import QTimer
import sys
import pyperclip
sys.path.append("..")
from ui.ui import Ui_Dialog
import inspect
from scripts._serail import _Serail
from crc import CrcCalculator, Configuration
import source.icon.inste

class UserUI(QtWidgets.QDialog, QIntValidator,Ui_Dialog, _Serail):
    def __init__(self):
        super(UserUI, self).__init__()
        _Serail.__init__(self)
        self.setupUi(self)
        self.dis_serial_list()
        self.setCrcCalculator()
        self.pushButton_9.clicked.connect(self.close_serial_port) #断开
        self.pushButton_4.clicked.connect(self.open_serial_port) #连接
        self.pushButton_6.clicked.connect(self.read_addr_and_baud) #地址读取
        self.pushButton_3.clicked.connect(self.broadcast_config) #广播配置
        self.pushButton_5.clicked.connect(self.normal_config) #配置
        self.pushButton_2.clicked.connect(self.read_data) #读取数据
        self.pushButton_7.clicked.connect(self.copy_to_clipboard) #复制
        self.pushButton_8.clicked.connect(self.clear_debug_data) #清除

        self.lineEdit.textChanged.connect(self.check_lineEdit_valid) #通讯地址
        self.lineEdit_3.textChanged.connect(self.check_lineEdit_3_valid) #通讯地址

        self.mutex_ = QMutex()
        self.collection_timer_ = QTimer()
        self.collection_timer_.timeout.connect(self.continuous_acquisition)

        self.lineEdit.setText('1') #通讯地址
        self.lineEdit_3.setText('1') #配置地址
        self.radioButton_2.setEnabled(False)

        self.comboBox_3.addItem('1200')#通讯波特率
        self.comboBox_3.addItem('2400')
        self.comboBox_3.addItem('4800')
        self.comboBox_3.addItem('9600')
        self.comboBox_3.addItem('19200')
        self.comboBox_3.setCurrentText('9600')

        self.comboBox_2.addItem('1200')#配置波特率
        self.comboBox_2.addItem('2400')
        self.comboBox_2.addItem('4800')
        self.comboBox_2.addItem('9600')
        self.comboBox_2.addItem('19200')
        self.comboBox_2.setCurrentText('2400')
        #self.comboBox.activated.connect(self.dis_serial_list)
        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "th10s"))
        Dialog.setWindowIcon(QIcon(':/inste.ico'))
        self.groupBox.setTitle(_translate("Dialog", "设置"))
        self.groupBox_3.setTitle(_translate("Dialog", "通讯连接"))
        self.label_5.setText(_translate("Dialog", "地址："))
        self.label_3.setText(_translate("Dialog", "串口号："))
        self.label_4.setText(_translate("Dialog", "波特率："))
        self.pushButton_4.setText(_translate("Dialog", "连接"))
        self.pushButton_9.setText(_translate("Dialog", "断开"))
        self.groupBox_4.setTitle(_translate("Dialog", "配置参数"))
        self.label_14.setText(_translate("Dialog", "地址："))
        self.label_15.setText(_translate("Dialog", "波特率："))
        self.radioButton_2.setText(_translate("Dialog", "配置波特率"))
        self.pushButton_6.setText(_translate("Dialog", "读取"))
        self.pushButton_5.setText(_translate("Dialog", "配置"))
        self.pushButton_3.setText(_translate("Dialog", "广播配置"))
        self.groupBox1.setTitle(_translate("Dialog", "数据"))
        self.label_2.setText(_translate("Dialog", "温度"))
        self.label_10.setText(_translate("Dialog", "℃"))
        self.label_12.setText(_translate("Dialog", "湿度"))
        self.label_13.setText(_translate("Dialog", "rh%"))
        self.pushButton_2.setText(_translate("Dialog", "读取"))
        self.radioButton.setText(_translate("Dialog", "连续采集"))
        self.groupBox_2.setTitle(_translate("Dialog", "调试"))
        self.pushButton_7.setText(_translate("Dialog", "复制"))
        self.pushButton_8.setText(_translate("Dialog", "清除"))  
        
    def setCrcCalculator(self):
        width = 16
        poly = 0x8005
        init_value=0xFFFF
        final_xor_value=0x0000
        reverse_input=True
        reverse_output=True
        configuration = Configuration(width, poly, init_value, final_xor_value, reverse_input, reverse_output)
        use_table = True
        self.crc_calculator = CrcCalculator(configuration, use_table)

    def calc_crc(self, bytes_data):
        checksum = self.crc_calculator.calculate_checksum(bytes_data)
        checksum = int(checksum/(0xff+1)) + ((checksum%(0xff + 1)) << 8)
        return checksum

    def phase_baud_addr(self, recv_bytes):
        addr_bytes = recv_bytes[3:5]
        addr = (int.from_bytes(addr_bytes, "big"))
        self.lineEdit_3.setText(str(addr))
        baud_bytes = recv_bytes[5:7]
        baud = (int.from_bytes(baud_bytes, 'big'))
        if baud == 0:
            self.comboBox_2.setCurrentText('1200')
        elif baud == 1:
            self.comboBox_2.setCurrentText('2400')
        elif baud == 2:
            self.comboBox_2.setCurrentText('4800')
        elif baud == 3:
            self.comboBox_2.setCurrentText('9600')
        elif baud == 4:
            self.comboBox_2.setCurrentText('19200')

    def bytes_to_strs(self, bytes_value):
        arry = ''.join(['%02x '% b for b in bytes_value])
        return (arry.upper())

    def read_addr_and_baud(self):
        if self._is_active() != None:
            cmd = self.filling_get_baud_addr()
            recv_bytes = self.rs485_newsletter(cmd)
            if len(recv_bytes) == 9:
                if self.calc_crc(recv_bytes) == 0:
                    self.phase_baud_addr(recv_bytes)

    def filling_config_addr(self, addr):
        send_bytes = (addr).to_bytes(1, byteorder='big')
        send_bytes += (6).to_bytes(1, byteorder='big')
        send_bytes += (100).to_bytes(2, byteorder='big')
        send_bytes += (int(self.lineEdit_3.text())).to_bytes(2, byteorder='big')
        if self.radioButton_2.isChecked() == True:
            baud_ = int(self.comboBox_2.currentText())
            baud_value = int()
            if baud_ == 1200:
                baud_value = 0
            elif baud_ == 2400:
                baud_value = 1
            elif baud_ == 4800:
                baud_value = 2
            elif baud_ == 9600:
                baud_value = 3
            elif baud_ == 19200:
                baud_value = 4
            send_bytes += (baud_value).to_bytes(2, byteorder='big')
        send_bytes += (self.calc_crc(send_bytes)).to_bytes(2, byteorder='big')
        return send_bytes

    def filling_get_humid_thermo(self):
        send_bytes = (int(self.lineEdit.text())).to_bytes(1, byteorder='big')
        send_bytes += (3).to_bytes(1, byteorder='big')
        send_bytes += (0).to_bytes(2, byteorder='big')
        send_bytes += (2).to_bytes(2, byteorder='big')
        send_bytes += (self.calc_crc(send_bytes)).to_bytes(2, byteorder='big')
        return send_bytes

    def filling_get_baud_addr(self):
        send_bytes = (int(self.lineEdit.text())).to_bytes(1, byteorder='big')
        send_bytes += (3).to_bytes(1, byteorder='big')
        send_bytes += (100).to_bytes(2, byteorder='big')
        send_bytes += (2).to_bytes(2, byteorder='big')
        send_bytes += (self.calc_crc(send_bytes)).to_bytes(2, byteorder='big')
        return send_bytes


    def broadcast_config(self):
        if self._is_active() == None:
            QMessageBox.warning(self, "WARNING", "")
            return

        cmd = self.filling_config_addr(0xff)
        self.rs485_newsletter(cmd)

    def rs485_newsletter(self, cmd):
        if self._is_active() == None:
            QMessageBox.warning(self, "WARNING", "serial port not open.")

        self.mutex_.lock()
        self._write(cmd)
        self.textBrowser.append("TX:" + self.bytes_to_strs(cmd))
        recv_bytes = self._read()
        if len(recv_bytes) != 0:
            self.textBrowser.append("RX:" + self.bytes_to_strs(recv_bytes))
        self.mutex_.unlock()
        return recv_bytes

    def normal_config(self):
        if self._is_active() == None:
            QMessageBox.warning(self, "WARNING", "")
            return

        cmd = self.filling_config_addr(int(self.lineEdit.text()))
        self.rs485_newsletter(cmd)

    def phase_humid_thermo(self, recv_bytes):
        thermo_bytes = recv_bytes[3:5]
        thermo = (int.from_bytes(thermo_bytes, "big")) * 0.1
        self.lineEdit_4.setText("%.1f"%thermo)
        humid_bytes = recv_bytes[5:7]
        humid = (int.from_bytes(humid_bytes, 'big')) * 0.1
        self.lineEdit_5.setText("%.1f"%humid)

    def continuous_acquisition(self):
        if self.pushButton_2.text() == "停止":
            if  self._is_active() == None:
                self.collection_timer_.stop()
                return
            cmd = self.filling_get_humid_thermo()
            recv_bytes = self.rs485_newsletter(cmd)
            if len(recv_bytes) == 9 and self.calc_crc(recv_bytes) == 0:
                self.phase_humid_thermo(recv_bytes)
            else:
                QMessageBox.warning(self, "WARNING", "read data err")

    def read_data(self):
        if self.pushButton_2.text() == "读取":
            if self.radioButton.isChecked() == True:
                self.pushButton_2.setText("停止")
                self.radioButton.setEnabled(False)
                self.collection_timer_.start(500)
            else:
                if self._is_active() != None:
                    cmd = self.filling_get_humid_thermo()
                    recv_bytes = self.rs485_newsletter(cmd)
                    if self.calc_crc(recv_bytes) != 0:
                        QMessageBox.warning(self, "WARNING", " ")
                    else:
                        self.phase_humid_thermo(recv_bytes)
        elif self.pushButton_2.text() == "停止":
            self.pushButton_2.setText("读取")
            self.radioButton.setEnabled(True)

    def copy_to_clipboard(self):
        pyperclip.copy(self.textBrowser.toPlainText())
        pass

    def clear_debug_data(self):
        self.textBrowser.clear()
        pass

    def check_lineEdit_valid(self):
        str_value = self.lineEdit.text()
        try:
            value = int(str_value)
            if value < 1 or value > 247:
                QMessageBox.warning(self, "WARNING", "th10s 地址在1~247之间")
                self.lineEdit.setText('1')
        except Exception :
            if str_value != '':
                QMessageBox.warning(self, "WARNING", "请设置整数")

    def check_lineEdit_3_valid(self):
        str_value = self.lineEdit_3.text()
        try:
            value = int(str_value)
            if value < 1 or value > 247:
                QMessageBox.warning(self, "WARNING", "th10s 地址在1~247之间")
                self.lineEdit_3.setText('1')
        except Exception :
            if str_value != '':
                QMessageBox.warning(self, "WARNING", "请设置整数")

    def get_func_name(self):
        return inspect.stack()[1][3]

    def dis_serial_list(self):
        port_list = self._get_port_list()
        if len(port_list) <= 0:
            self.statusbar.showMessage('no serial')
        else:
            self.comboBox.clear()
            for com in port_list:
                self.comboBox.addItem(str(com[0]))

    def open_serial_port(self):
        try:
            self._open_serial_port(self.comboBox.currentText(), self.comboBox_3.currentText())
            self.pushButton_4.setEnabled(False)
            self.lineEdit.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.comboBox_3.setEnabled(False)
        except Exception as e:
            QMessageBox.warning(self, 'WARNING', str(e))

    def close_serial_port(self):
        self.dis_serial_list()
        try:
            self._close_serial_port()
            if self._is_active() == None:
                self.pushButton_4.setEnabled(True)
                self.lineEdit.setEnabled(True)
                self.comboBox.setEnabled(True)
                self.comboBox_3.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, 'WARNING', str(e))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = UserUI()
    mainWindow.show()
    sys.exit(app.exec_())
