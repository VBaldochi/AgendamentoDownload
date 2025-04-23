import qbittorrentapi
import schedule
import time
from datetime import datetime

# Configurar cliente qBittorrent
client = qbittorrentapi.Client(
    host='localhost',
    port=8080,
    username='admin',
    password='adminadmin'
)

try:
    client.auth_log_in()
    print("✅ Conectado ao qBittorrent!")
except qbittorrentapi.LoginFailed as e:
    print("❌ Falha ao logar:", e)
    exit()

# Lista para armazenar agendamentos
agendamentos = []

# Função para adicionar torrent
def adicionar_torrent_agendado(magnet_link):
    client.torrents_add(urls=magnet_link)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Torrent adicionado: {magnet_link}")

# Loop interativo
while True:
    print("\n📥 Novo agendamento de torrent")
    magnet = input("🔗 Cole o magnet link: ").strip()
    horario = input("🕒 Horário de download (formato HH:MM): ").strip()

    if not magnet.startswith("magnet:?xt="):
        print("⚠️ Magnet link inválido. Tente novamente.")
        continue

    try:
        schedule.every().day.at(horario).do(adicionar_torrent_agendado, magnet_link=magnet)
        agendamentos.append((magnet, horario))
        print(f"✅ Agendamento criado para {horario}")
    except Exception as e:
        print("❌ Erro ao agendar:", e)

    mais = input("➕ Deseja agendar outro? (s/n): ").strip().lower()
    if mais != 's':
        break

# Mostrar agenda atual
print("\n📋 Agendamentos programados:")
for idx, (mag, hr) in enumerate(agendamentos, 1):
    print(f"{idx}. ⏰ {hr} | 🔗 {mag[:60]}...")

# Loop de execução
print("\n⏳ Aguardando horários agendados...\n(Use Ctrl+C para sair)\n")
while True:
    schedule.run_pending()
    time.sleep(30)
