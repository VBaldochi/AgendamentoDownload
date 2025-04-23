

# 🎯 Agendador de Torrents

Este é um sistema web desenvolvido com **Python (Flask)** para agendar downloads de torrents via **qBittorrent**, com notificações automáticas via **Telegram** sempre que o download for concluído ou ocorrer um erro.

---

## 🚀 Funcionalidades

- ✅ Login com autenticação simples
- ⏰ Agendamento de torrents para horário específico
- 📡 Monitoramento automático dos downloads
- 📬 Notificações via Telegram ao concluir ou falhar um download
- 🔄 Pausar, retomar e excluir torrents pela interface
- 🗓️ Editar e remover agendamentos
- 📊 API para acompanhar o progresso dos torrents

---

## 🛠️ Tecnologias utilizadas

- **Flask**: framework web
- **qBittorrent API**: controle do cliente de torrent
- **schedule**: agendamentos de tarefas em background
- **Telegram Bot API**: envio de notificações
- **HTML + Tailwind CSS**: interface frontend
- **threading**: execução paralela das tarefas agendadas e monitoramento

---

## 📷 Interface

A interface é simples, intuitiva e responsiva, com suporte a **modo escuro**.

---

## ⚙️ Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

2. **Crie um ambiente virtual e instale as dependências:**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. **Certifique-se que o qBittorrent esteja configurado com a Web UI ativa:**

- Acesse o qBittorrent
- Vá em `Configurações > Interface Web`
- Ative e defina usuário: `admin`, senha: `adminadmin`

4. **Configure seu bot do Telegram:**

- Crie um bot em [@BotFather](https://t.me/botfather)
- Substitua a variável `TELEGRAM_TOKEN` em `app.py` pelo token do seu bot
- Descubra seu `chat_id` com o site [getids.bot](https://t.me/getidsbot)

---

## ▶️ Execução

Execute o servidor:

```bash
python app.py
```

Acesse em `http://localhost:5000`

Usuário padrão: `admin`  
Senha padrão: `senha123`

---

## 📦 Estrutura do Projeto

```
.
├── app.py               # Código principal do servidor Flask
├── schedules.json       # Armazena os agendamentos salvos
├── templates/
│   └── index.html       # Página principal do app
│   └── login.html       # Página de login
```

---

## 📡 Endpoints da API

| Método | Endpoint               | Descrição                          |
|--------|------------------------|------------------------------------|
| GET    | `/api/progresso`       | Retorna lista com progresso atual  |
| POST   | `/api/pause`           | Pausa um torrent específico        |
| POST   | `/api/resume`          | Retoma um torrent específico       |
| POST   | `/api/delete`          | Remove um torrent (mantém arquivos)|
| POST   | `/api/delete-schedule` | Remove um agendamento              |
| POST   | `/api/edit-schedule`   | Edita o horário de um agendamento  |

---

## 📌 Observações

- O sistema **não faz upload automático de torrents** — ele apenas agenda e monitora a adição de magnet links.
- É necessário manter o qBittorrent **rodando com a Web UI ativa**.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---