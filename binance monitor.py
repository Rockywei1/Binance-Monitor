import json
import requests
import os
import time
from datetime import datetime
from binance.client import Client
from collections import deque
import telebot
from urllib.parse import urljoin
import sys
import threading
import configparser
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMenuBar, QMenu, QAction, QDialog, QHBoxLayout, QTextEdit

class APISettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("API Settings")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        binance_label = QLabel("Binance API Key:")
        self.binance_entry = QLineEdit()

        binance_secret_label = QLabel("Binance API Secret:")
        self.binance_secret_entry = QLineEdit()
        self.binance_secret_entry.setEchoMode(QLineEdit.Password)

        telegram_chat_label = QLabel("Telegram Chat ID:")
        self.telegram_chat_entry = QLineEdit()

        telegram_token_label = QLabel("Telegram API Token:")
        self.telegram_token_entry = QLineEdit()

        layout.addWidget(binance_label)
        layout.addWidget(self.binance_entry)
        layout.addWidget(binance_secret_label)
        layout.addWidget(self.binance_secret_entry)
        layout.addWidget(telegram_chat_label)
        layout.addWidget(self.telegram_chat_entry)
        layout.addWidget(telegram_token_label)
        layout.addWidget(self.telegram_token_entry)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        load_button = QPushButton("Load Settings")
        save_button.clicked.connect(self.save_settings)
        load_button.clicked.connect(self.load_settings)
        layout.addWidget(save_button)
        layout.addWidget(load_button)

        self.setLayout(layout)

    def save_settings(self):
        binance_api_key = self.binance_entry.text()
        binance_api_secret = self.binance_secret_entry.text()
        telegram_chat_id = self.telegram_chat_entry.text()
        telegram_api_token = self.telegram_token_entry.text()

        config = configparser.ConfigParser()

        config.add_section('Settings')

        config.set('Settings', 'binance_api_key', binance_api_key)
        config.set('Settings', 'binance_api_secret', binance_api_secret)
        config.set('Settings', 'telegram_chat_id', telegram_chat_id)
        config.set('Settings', 'telegram_api_token', telegram_api_token)

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

    def load_settings(self):
        config = configparser.ConfigParser()

        try:
            config.read('settings.ini')
            binance_api_key = config.get('Settings', 'binance_api_key')
            binance_api_secret = config.get('Settings', 'binance_api_secret')
            telegram_chat_id = config.get('Settings', 'telegram_chat_id')
            telegram_api_token = config.get('Settings', 'telegram_api_token')

            self.binance_entry.setText(binance_api_key)
            self.binance_secret_entry.setText(binance_api_secret)
            self.telegram_chat_entry.setText(telegram_chat_id)
            self.telegram_token_entry.setText(telegram_api_token)
        except Exception as e:
            print(f"Error loading settings: {e}")

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Binance Monitor Setting")
        self.setGeometry(100, 100, 600, 450)
        self.init_ui()

    def init_ui(self):

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        hbox_layout = QHBoxLayout()

        threshold_label = QLabel("Percentage Change (1):")
        self.threshold_entry = QLineEdit()

        time_period_label = QLabel("Time Period (mins) (1):")
        self.time_period_entry = QLineEdit()

        hbox_layout.addWidget(threshold_label)
        hbox_layout.addWidget(self.threshold_entry)
        hbox_layout.addWidget(time_period_label)
        hbox_layout.addWidget(self.time_period_entry)

        layout.addLayout(hbox_layout)

        hbox_layout1 = QHBoxLayout()

        threshold_label = QLabel("Percentage Change (2):")
        self.threshold_entry1 = QLineEdit()

        time_period_label = QLabel("Time Period (mins) (2):")
        self.time_period_entry1 = QLineEdit()

        hbox_layout1.addWidget(threshold_label)
        hbox_layout1.addWidget(self.threshold_entry1)
        hbox_layout1.addWidget(time_period_label)
        hbox_layout1.addWidget(self.time_period_entry1)

        layout.addLayout(hbox_layout1)

        hbox_layout2 = QHBoxLayout()

        threshold_label = QLabel("Percentage Change (3):")
        self.threshold_entry2 = QLineEdit()

        time_period_label = QLabel("Time Period (mins) (3):")
        self.time_period_entry2 = QLineEdit()

        hbox_layout2.addWidget(threshold_label)
        hbox_layout2.addWidget(self.threshold_entry2)
        hbox_layout2.addWidget(time_period_label)
        hbox_layout2.addWidget(self.time_period_entry2)

        layout.addLayout(hbox_layout2)

        mode_buttons_layout = QHBoxLayout()
        self.spot_button = QPushButton("Spot")
        self.contract_button = QPushButton("Contract")
        mode_buttons_layout.addWidget(self.spot_button)
        mode_buttons_layout.addWidget(self.contract_button)

        self.spot_button.clicked.connect(self.set_mode_spot)
        self.contract_button.clicked.connect(self.set_mode_contract)
        layout.addLayout(mode_buttons_layout)

        mode_buttons_layout = QHBoxLayout()
        self.on_button = QPushButton("Start")
        self.off_button = QPushButton("Stop")
        mode_buttons_layout.addWidget(self.on_button)
        mode_buttons_layout.addWidget(self.off_button)

        self.on_button.clicked.connect(self.set_mode_on)
        self.off_button.clicked.connect(self.set_mode_off)
        layout.addLayout(mode_buttons_layout)

        self.output_text = QTextEdit()
        layout.addWidget(self.output_text)

        central_widget.setLayout(layout)

        menubar = self.menuBar()

        settings_menu = menubar.addMenu("Settings")

        api_settings_action = QAction("API Settings", self)
        api_settings_action.triggered.connect(self.open_api_settings)
        settings_menu.addAction(api_settings_action)

        exchange_select = QAction("Exchange Selection", self)
        settings_menu.addAction(exchange_select)

        self.binance_monitor = BinanceMonitor(self)

    def open_api_settings(self):
        api_settings_dialog = APISettingsDialog()
        api_settings_dialog.exec_()

    def set_mode_on(self):
        input1 = self.threshold_entry.text()
        input2 = self.threshold_entry1.text()
        input3 = self.threshold_entry2.text()
        input4 = self.time_period_entry.text()
        input5 = self.time_period_entry1.text()
        input6 = self.time_period_entry2.text()
        if len(input1) > 0 and len(input2) > 0 and len(input3) > 0 and len(input4) > 0 and len(input5) > 0 and len(input6) > 0:
            self.binance_monitor.get_inputs()
            self.binance_monitor.start_monitor()
            self.on_button.setStyleSheet("background-color: #00FF00;")
            self.off_button.setStyleSheet("")
            print('Start running')
            self.print_to_output('Start running')
        else:
            print('Please fill in percentage change and time period first')
            QMessageBox.warning(self, "Warning", "Please fill in percentage change and time period first")

    def set_mode_off(self):
        self.binance_monitor.stop_monitor()
        self.on_button.setStyleSheet("")
        self.off_button.setStyleSheet("background-color: #00FF00;")
        print('Pause running')
        self.print_to_output('Pause running')

    def set_mode_spot(self):
        self.binance_monitor.mode_trade = 'spot'
        self.contract_button.setStyleSheet("")
        self.spot_button.setStyleSheet("background-color: #00FF00;")
        print('Spot mode')
        self.print_to_output('Spot mode')

    def set_mode_contract(self):
        self.binance_monitor.mode_trade = 'contract'
        self.contract_button.setStyleSheet("background-color: #00FF00;")
        self.spot_button.setStyleSheet("")
        print('Contract mode')
        self.print_to_output('Contract mode')

    def print_to_output(self, text):
        self.output_text.append(text)

class BinanceMonitor():
    def __init__(self, set_window):
        self.set_window = set_window
        setting = APISettingsDialog()
        setting.load_settings()
        chat_id = setting.telegram_chat_entry.text()
        tele_api = setting.telegram_token_entry.text()
        api_key_binance = setting.binance_entry.text()
        api_secret_binance = setting.binance_secret_entry.text()
        print('setting1', chat_id, type(chat_id))
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(token=tele_api)
        self.client = Client(api_key=api_key_binance, api_secret=api_secret_binance)

        self.running = False
        self.thread = None
        self.mode_trade = ''
        self.repeat = 240
        self.difference = 30
        self.PAIR_WITH = 'USDT'
        self.k_volume = 1000000
        self.FIATS = ['BTTCUSDT', 'CVXUSDT', 'MOBUSDT', 'HIFIUSDT', 'FLOWUSDT', 'BLZUSDT', 'NBTUSDT', 'RIFUSDT', 'FORTHUSDT', 'POLSUSDT', 'AMBUSDT','ACHUSDT']

    def get_inputs(self):
        CHANGE_IN_PRICE0 = self.set_window.threshold_entry.text()
        CHANGE_IN_PRICE = self.set_window.threshold_entry1.text()
        CHANGE_IN_PRICE1 = self.set_window.threshold_entry2.text()
        self.CHANGE_IN_PRICE0 = float(CHANGE_IN_PRICE0)
        self.CHANGE_IN_PRICE = float(CHANGE_IN_PRICE)
        self.CHANGE_IN_PRICE1 = float(CHANGE_IN_PRICE1)

        self.time_p0 = self.set_window.time_period_entry.text()
        self.time_p = self.set_window.time_period_entry1.text()
        self.time_p1 = self.set_window.time_period_entry2.text()
        self.time_1 = 15
        time_p_1 = float(self.time_p0)*60
        time_p_2 = float(self.time_p)*60
        time_p_3 = float(self.time_p1)*60
        self.time_20 = int(time_p_1/self.time_1)
        self.time_2 = int(time_p_2/self.time_1)
        self.time_21 = int(time_p_3/self.time_1)
        self.time_30 = self.time_20 * self.time_1 / 60
        self.time_3 = self.time_2 * self.time_1 / 60
        self.time_31 = self.time_21 * self.time_1 / 60

    def prices_message_dict(self):
        self.prices0 = {coin: deque(maxlen=self.time_20) for coin in self.get_price().keys()}
        self.prices = {coin: deque(maxlen=self.time_2) for coin in self.get_price().keys()}
        self.prices1 = {coin: deque(maxlen=self.time_21) for coin in self.get_price().keys()}

        self.recent_messages0 = {coin: deque(maxlen=1) for coin in self.get_price().keys()}
        self.recent_messages = {coin: deque(maxlen=1) for coin in self.get_price().keys()}
        self.recent_messages1 = {coin: deque(maxlen=1) for coin in self.get_price().keys()}

        self.last_repeated_message_time0 = {}
        self.last_repeated_message_time = {}
        self.last_repeated_message_time1 = {}

    def get_price(self):
        initial_price = {}
        prices = self.client.get_all_tickers()

        url_f = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
        data = requests.get(url_f).json()['symbols']
        symbols = [item['symbol'] for item in data]

        if self.mode_trade == 'spot':
            for coin in prices:
                if self.PAIR_WITH in coin['symbol'] and all(item not in coin['symbol'] for item in self.FIATS):
                    initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}

        elif self.mode_trade == 'contract':
            for coin in prices:
                if coin['symbol'] in symbols:
                    if self.PAIR_WITH in coin['symbol'] and all(item not in coin['symbol'] for item in self.FIATS):
                        initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}

        else:
            print('Please select spot or contract!')
            self.set_window.print_to_output('Please select spot or contract!')
            self.set_window.on_button.setStyleSheet("")
            initial_price = None

        return initial_price

    def calculate_change(self, coin, price_list):
        last_price = float(price_list[-1])
        first_price = float(price_list[0])
        change = (last_price - first_price) / first_price * 100
        print(f"{coin} last:{last_price} first:{first_price} price change: {change:.2f}%")
        return change

    def update_spotCoins(self, coin, trade_mode):
        spot_coin = {}
        folder_path = f'bina_tele_coin/'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        coin_path = f'{folder_path}/coins.json'
        if os.path.isfile(coin_path):
            with open(coin_path) as file:
                spot_coin = json.load(file)

        if len(spot_coin['token_info']) >= 10:
            spot_coin['token_info'] = spot_coin['token_info'][-9:]

        if 'token_info' in spot_coin:
            spot_coin['token_info'].append({
                'coin': coin,
                'trade_mode': trade_mode,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
        else:
            spot_coin['token_info'] = [{
                'coin': coin,
                'trade_mode': trade_mode,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M"),
            }]

        with open(coin_path, 'w') as file:
            json.dump(spot_coin, file, indent=4)

    def start_monitor(self):
        print('start_monitor')
        self.running = True
        self.thread = threading.Thread(target=self.run_monitor)
        self.thread.start()

    def stop_monitor(self):
        if self.running:
            self.running = False
            self.thread.join()

    def run_monitor(self):
        if self.mode_trade != '':
            self.prices_message_dict()
        while self.running:

                url = 'https://www.tradingview.com'
                price_dict = self.get_price()

                if price_dict is None:
                    print('Please select spot or contract!')
                    self.set_window.print_to_output('Please select spot or contract!')
                    self.set_window.on_button.setStyleSheet("")
                    break

                for coin, price_data in price_dict.items():
                    price = float(price_data['price'])
                    self.prices0[coin].append(price)
                    self.prices[coin].append(price)
                    self.prices1[coin].append(price)

                    if len(self.prices0[coin]) == self.time_20:

                        change = self.calculate_change(coin, self.prices0[coin])
                        print('Change in percentage one:', self.CHANGE_IN_PRICE0)
                        if abs(change) > self.CHANGE_IN_PRICE0:

                            href = urljoin(url, f'/chart/?symbol=BINANCE%3A{coin}')
                            text = (f"{coin} The price change percentage in the last {self.time_30} minutes is {change:.2f}%")
                            self.set_window.print_to_output(text)

                            current_time = time.time()
                            if coin in self.recent_messages0 and self.recent_messages0[coin] != text.replace(f" {change:.2f}%", "").replace(f"{self.time_30}", ""):
                                self.bot.send_message(chat_id=self.chat_id, text=href)
                                self.bot.send_message(chat_id=self.chat_id, text=text)

                                self.last_repeated_message_time0[coin] = current_time
                                self.recent_messages0[coin] = text.replace(f" {change:.2f}%", "").replace(f"{self.time_30}", "")
                                self.update_spotCoins(coin, self.mode_trade)

                            if current_time - self.last_repeated_message_time0[coin] >= self.repeat * 60:
                                self.bot.send_message(chat_id=self.chat_id, text=href)
                                self.bot.send_message(chat_id=self.chat_id, text=text)
                                self.last_repeated_message_time0[coin] = current_time
                                self.recent_messages0[coin] = text.replace(f" {change:.2f}%", "").replace(f"{self.time_30}", "")
                                self.update_spotCoins(coin, self.mode_trade)

                    if len(self.prices[coin]) == self.time_2:
                        change = self.calculate_change(coin, self.prices[coin])
                        print('Change in percentage two:', self.CHANGE_IN_PRICE)
                        if abs(change) > self.CHANGE_IN_PRICE:

                            href = urljoin(url, f'/chart/?symbol=BINANCE%3A{coin}')
                            text = (f"{coin} The price change percentage in the last {self.time_3} minutes is {change:.2f}%")
                            self.set_window.print_to_output(text)

                            current_time = time.time()
                            if coin in self.recent_messages and self.recent_messages[coin] != text.replace(f" {change:.2f}%", "").replace(f"{self.time_3}", ""):
                                self.bot.send_message(chat_id=self.chat_id, text=href)
                                self.bot.send_message(chat_id=self.chat_id, text=text)
                                self.last_repeated_message_time[coin] = current_time
                                self.recent_messages[coin] = text.replace(f" {change:.2f}%", "").replace(f"{self.time_3}", "")
                                self.update_spotCoins(coin, self.mode_trade)

                            if current_time - self.last_repeated_message_time[coin] >= self.repeat * 60:
                                self.bot.send_message(chat_id=self.chat_id, text=href)
                                self.bot.send_message(chat_id=self.chat_id, text=text)
                                self.last_repeated_message_time[coin] = current_time
                                self.recent_messages[coin] = text.replace(f" {change:.2f}%", "").replace(f"{self.time_3}", "")
                                self.update_spotCoins(coin, self.mode_trade)

                    if len(self.prices1[coin]) == self.time_21:
                        change = self.calculate_change(coin, self.prices1[coin])
                        print('Change in percentage three:', self.CHANGE_IN_PRICE1)
                        if abs(change) > self.CHANGE_IN_PRICE1:

                            href = urljoin(url, f'/chart/?symbol=BINANCE%3A{coin}')
                            text = (f"{coin} The price change percentage in the last {self.time_31} minutes is {change:.2f}%")
                            self.set_window.print_to_output(text)

                            current_time = time.time()
                            if coin in self.recent_messages1 and self.recent_messages1[coin] != text.replace(f" {change:.2f}%", "").replace(f"{self.time_31}", ""):
                                self.bot.send_message(chat_id=self.chat_id, text=href)
                                self.bot.send_message(chat_id=self.chat_id, text=text)
                                self.last_repeated_message_time1[coin] = current_time
                                self.recent_messages1[coin] = text.replace(f" {change:.2f}%", "").replace(f"{self.time_31}", "")
                                self.update_spotCoins(coin, self.mode_trade)
                            if current_time - self.last_repeated_message_time1[coin] >= self.repeat * 60:
                                self.bot.send_message(chat_id=self.chat_id, text=href)
                                self.bot.send_message(chat_id=self.chat_id, text=text)
                                self.last_repeated_message_time1[coin] = current_time
                                self.recent_messages1[coin] = text.replace(f" {change:.2f}%", "").replace(f"{self.time_31}", "")
                                self.update_spotCoins(coin, self.mode_trade)

                time.sleep(self.time_1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()

    window.show()

    sys.exit(app.exec_())
