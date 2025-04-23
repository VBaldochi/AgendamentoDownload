from flask import Flask, render_template, request, redirect, session, jsonify
import schedule
import time
import threading
import uuid
import json
from datetime import datetime
import qbittorrentapi
import requests

# --- Constantes e Configuração ---
DATA_FILE = 'schedules.json'  # Arquivo onde os agendamentos serão salvos
SECRET_KEY = 'baldochi'  # Chave secreta para sessões Flask
USERNAME = 'admin'  # Nome de usuário padrão
PASSWORD = 'senha123'  # Senha padrão

# Configuração de notificação Telegram
TELEGRAM_TOKEN = '7743417874:AAGG6lpG4KpLHnPMlJizN7bpqaJ4zifrSag'
TELEGRAM_CHAT_ID = '345946900'

# --- Configuração do app ---
app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- Cliente qBittorrent ---
client = qbittorrentapi.Client(host='localhost', port=8080,
                            username='admin', password='adminadmin')
client.auth_log_in()

# --- Função de notificação Telegram ---
def send_telegram(message):
    """
    Envia uma mensagem para o chat via Bot do Telegram.
    Mostra o status da resposta no log para depuração.
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        response = requests.post(url, json=payload)
        app.logger.info(f"Status do envio Telegram: {response.status_code} - {response.text}")
    except Exception:
        app.logger.exception('Erro ao enviar notificação para o Telegram')

# --- Monitoramento de torrents para notificações ---
prev_states = {}  # Estados anteriores dos torrents
prev_progress = {}  # Progresso anterior dos torrents

def monitor_torrents():
    """
    Verifica o status dos torrents periodicamente para detectar
    conclusões ou erros e enviar notificações.
    """
    while True:
        try:
            torrents = client.torrents_info()
            for t in torrents:
                h = t.hash
                curr_state = t.state.lower()
                curr_progress = t.progress * 100

                # Inicializa estado se for o primeiro encontro
                if h not in prev_states:
                    prev_states[h] = curr_state
                    prev_progress[h] = curr_progress
                    continue

                # Detecta conclusão do download
                if prev_progress[h] < 100 and curr_progress >= 100:
                    msg = f"✅ Torrent concluído: {t.name}"
                    send_telegram(msg)

                # Detecta erro no torrent
                if curr_state in ['error', 'uploading_error'] and curr_state != prev_states[h]:
                    msg = f"⚠️ Erro no torrent: {t.name}"
                    send_telegram(msg)

                # Atualiza os estados anteriores
                prev_states[h] = curr_state
                prev_progress[h] = curr_progress

            time.sleep(10)
        except Exception:
            app.logger.exception('Erro ao monitorar torrents')
            time.sleep(30)

# Inicia thread para monitoramento de torrents
threading.Thread(target=monitor_torrents, daemon=True).start()

# --- Carregar/Salvar agendamentos ---
def load_schedules():
    """
    Carrega os agendamentos do arquivo JSON.
    """
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_schedules(lst):
    """
    Salva os agendamentos no arquivo JSON.
    """
    with open(DATA_FILE, 'w') as f:
        json.dump(lst, f)

# --- Agendamentos e jobs em memória ---
schedules = load_schedules()
jobs = {}

# --- Thread para execução de agendamentos ---
def run_schedule():
    """
    Executa periodicamente os agendamentos definidos.
    """
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()

# --- Função auxiliar: adicionar job de agendamento ---
def add_schedule_job(item):
    """
    Adiciona um novo job de agendamento com base no item informado.
    """
    def job_fn(m=item):
        client.torrents_add(urls=m['magnet'])
        print(f"[{datetime.now().strftime('%H:%M')}] Adicionado {m['magnet']}")
    job = schedule.every().day.at(item['time']).do(job_fn)
    jobs[item['id']] = job

# Registra os agendamentos salvos
for sched in schedules:
    add_schedule_job(sched)

# --- API para obter progresso dos torrents ---
def obter_progresso():
    """
    Retorna uma lista com o progresso atual dos torrents.
    """
    torrents = client.torrents_info()
    progresso = []
    for t in torrents:
        progresso.append({
            'hash': t.hash,
            'nome': t.name,
            'percentual': t.progress * 100,
            'velocidade': t.dlspeed / 1024,
            'tempo_restante': t.eta,
            'agendado': any(s['magnet'] == t.magnet_uri for s in schedules)
        })
    return progresso

# --- Rotas do aplicativo ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Página principal. Permite agendar um novo torrent.
    """
    if not session.get('logged_in'):
        return redirect('/login')
    if request.method == 'POST':
        magnet = request.form.get('magnet')
        time_str = request.form.get('horario')
        item = {'id': str(uuid.uuid4()), 'magnet': magnet, 'time': time_str}
        schedules.append(item)
        save_schedules(schedules)
        add_schedule_job(item)
        return redirect('/')
    return render_template('index.html', schedules=schedules)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login.
    """
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', erro='Usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Efetua logout do usuário.
    """
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/api/progresso')
def api_progresso():
    """
    Endpoint para obter o progresso dos torrents.
    """
    try:
        return jsonify(obter_progresso())
    except Exception:
        app.logger.exception('Erro ao obter progresso')
        return jsonify({'error': 'internal'}), 500

@app.route('/api/pause', methods=['POST'])
def api_pause():
    """
    Pausa o download de um torrent específico.
    """
    data = request.get_json()
    client.torrents_pause(torrent_hashes=data['hash'])
    return ('', 204)

@app.route('/api/resume', methods=['POST'])
def api_resume():
    """
    Retoma o download de um torrent específico.
    """
    data = request.get_json()
    client.torrents_resume(torrent_hashes=data['hash'])
    return ('', 204)

@app.route('/api/delete', methods=['POST'])
def api_delete():
    """
    Remove um torrent da lista (sem apagar os arquivos).
    """
    data = request.get_json()
    client.torrents_delete(torrent_hashes=data['hash'], delete_files=False)
    return ('', 204)

@app.route('/api/delete-schedule', methods=['POST'])
def api_delete_schedule():
    """
    Remove um agendamento salvo.
    """
    data = request.get_json()
    sid = data.get('id')
    global schedules
    schedules = [s for s in schedules if s['id'] != sid]
    save_schedules(schedules)
    job = jobs.pop(sid, None)
    if job:
        schedule.cancel_job(job)
    return jsonify({'status': 'ok'})

@app.route('/api/edit-schedule', methods=['POST'])
def api_edit_schedule():
    """
    Edita o horário de um agendamento já existente.
    """
    data = request.get_json()
    sid = data.get('id')
    new_time = data.get('time')
    for s in schedules:
        if s['id'] == sid:
            s['time'] = new_time
            save_schedules(schedules)
            job = jobs.get(sid)
            if job:
                schedule.cancel_job(job)
            add_schedule_job(s)
            break
    return jsonify({'status': 'ok'})

# --- Inicialização do app ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
