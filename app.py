from flask import Flask, render_template, request, jsonify, session
from bot_simple import WhatsAppBot
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_secreta_muy_segura')  # Clave para las sesiones
bot = WhatsAppBot()

@app.route('/')
def index():
    # Asignar un ID de usuario si no existe
    if 'user_id' not in session:
        session['user_id'] = f'web_{uuid.uuid4().hex[:8]}'
    return render_template('index.html')

@app.route('/api/message', methods=['POST'])
def receive_message():
    data = request.json
    message = data.get('message', '')
    
    # Usar el ID de usuario de la sesión o el proporcionado
    user_id = data.get('user_id') or session.get('user_id', 'web_user')
    
    response = bot.procesar_mensaje(message, user_id)
    return jsonify({'response': response})

@app.route('/dashboard')
def dashboard():
    # Obtener estadísticas del bot
    stats = bot.obtener_estadisticas()
    return render_template('dashboard.html', stats=stats)

@app.route('/estadisticas')
def estadisticas():
    # Obtener estadísticas del bot
    stats = bot.obtener_estadisticas()
    return render_template('estadisticas.html', stats=stats)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)