# Caesar Phishing Framework 👑

A modern, interactive platform for managing phishing campaigns, built with Flask. Features an elegant dark interface and real-time monitoring capabilities.

![Caesar Phishing](https://img.shields.io/badge/Caesar-Phishing-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Why Caesar Phishing Framework?

Caesar Phishing Framework is designed to provide cybersecurity professionals with a powerful tool for testing security awareness within organizations. This framework is extremely useful for:

- 🎯 Training employees to recognize phishing attacks
- 📊 Analyzing organizational vulnerabilities
- 🔍 Testing the effectiveness of defense systems
- 📈 Improving overall cybersecurity
- 🤖 Telegram integration for instant notifications

## ✨ Key Features

- 🎨 Ready-to-use phishing templates:
  - Social networks (Facebook, Instagram, Twitter, LinkedIn)
  - Email services (Gmail, Outlook)
  - Financial services (PayPal, Credit Cards)
- 📊 Real-time monitoring:
  - Active campaign tracking
  - Success statistics
  - User behavior analysis
  - Instant Telegram notifications
- 🌐 Ngrok integration:
  - Automatic tunnel creation
  - Secure external access
  - Easy configuration
- 🎯 Modern interface:
  - Dark theme for better visualization
  - Responsive design for all devices
  - Interactive effects and animations
- 🔒 Security:
  - Administrative access control
  - Protected sessions
  - Secure data storage

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/caesar-phishing.git
cd caesar-phishing
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure Ngrok and Telegram:
- Sign up at [ngrok.com](https://ngrok.com)
- Get your auth token
- Create a Telegram bot via [@BotFather](https://t.me/botfather)
- Update tokens in `data/config.json`

## 🛠️ Configuration

The configuration file (`data/config.json`) contains:
```json
{
    "ngrok_token": "your_ngrok_token",
    "telegram_token": "your_telegram_token",
    "telegram_chat_id": "your_chat_id",
    "server": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": true
    },
    "security": {
        "secret_key": "your_secret_key"
    }
}
```

## 🎮 How to Use?

1. Start the server:
```bash
python app.py
```

2. Access the admin panel:
- Open `http://localhost:5000` in your browser
- Access is restricted to administrators only

3. Create a campaign:
- Select "New Campaign"
- Choose a template
- Copy the generated Ngrok URL
- Receive Telegram notifications for new data

4. Monitor campaigns:
- Track active campaigns
- Analyze data in real-time
- Export results to CSV
- Receive instant Telegram notifications

## 🔒 Security

The framework includes multiple security layers:
- Access control for administrators only
- Local network access restriction
- Ngrok URL filtering
- Secure data storage
- Session protection
- Secure Telegram integration

## 📊 Data Management

Collected data is stored in:
- `data/captured_data.json`
- `data/active_pages.json`

Export capabilities:
- CSV export with timestamps
- Detailed data fields
- Secure information processing
- Automatic Telegram notifications

## 🎨 Interface

- Interactive particles and effects
- Real-time statistics
- Smooth animations
- Clipboard copy function
- Event notifications
- Responsive grid layouts
- Modern glass-effect design

## ⚠️ Important Warning

This tool is intended for educational purposes only. The authors are not responsible for misuse or damages caused by the program. Use responsibly.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Push to the branch
5. Open a pull request

## 📧 Contact

For questions and support, please open an issue in the GitHub repository.
