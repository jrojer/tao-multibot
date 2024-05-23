# tao-multibot
LLM chat-bot infrastructure service featuring multiple bots instances with custom plugins (code/sql execution/document processing/etc.) and frontends (telegram, whatsapp, web).

Join [Project's Telegram Group](https://https://t.me/+3PbbqCddKt0zYWIy) and share your ideas.

## Getting started

```bash
python3 -m virtualenv .venv
source .venv/bin/activate

pip install -r requirements.txt

pytest
```
Then:
* Create a telegram bot using `@BotFather` and get a token.
* Set up an Openai account and get an API key. 
* Pull the repo

Create `master.json`:
```json
{
    "infra": {
        "debug": false,
        "server": {
            "port": 8080
        },
        "postgres": {
            "enabled": false,
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "password",
            "schemas": "public"
        },
        "influxdb": {
            "enabled": false,
            "url": "http://localhost:8086",
            "org": "org",
            "bucket": "bucket",
            "token": "token123123token"
        }
    },
    "bots": {
        "<YOUR BOT USERNAME>": {
            "bot_id": "<YOUR BOT USERNAME>",
            "type": "tg_bot",
            "token": "<TELEGRAM BOT TOKEN>",
            "tao_bot": {
                "username": "<YOUR BOT USERNAME>",
                "chats": [],
                "admins": [
                    "<YOUR USERNAME>"
                ],
                "users": [],
                "bot_mention_names": [
                    "tao",
                    "тао"
                ],
                "control_chat_id": "-",
                "messages_per_completion": 20,
                "system_prompt": "./"
            },
            "gpt": {
                "url": "https://api.openai.com/v1/chat/completions",
                "type": "openai",
                "token": "<YOUR OPENAI TOKEN>",
                "model": "gpt-3.5",
                "temperature": 0,
                "max_tokens": 1000,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
        }
}
```
Note, here `postgres` and `influxdb` are disabled. Chat messages are saved in-memory. You can configure the services later.

All is done, fire up the platform:
```bash
python entrypoint.py
```

## Further steps

* Set up `ffmpeg` for audio processing
* Set up `grafana` + `influxdb` for metric collection
* Set up `flyway` and `postgres` database to persist chat history
* Create more bots by adding their respected confs into `master.json`
* Set up a control chat (see "Authorisation" below)
* Write your own plugin (can be remote)

## Features

* **Authorisation**: bots know their admins, users and chats. Bot do not respond to unauthorised updates. In addition there is a control chat. Admins and control chat can convey bot commands, hence changing bot's behaviour. 
* **Plugins**: bots can call functions (basically any internal and external API). Plugins have common interface and can be easily added to the bot. Example of plugins:
  * code execution
  * sql query any databases
  * web search 
  * read pdf
  * generate images
  * send messages
  * transcribe audio
  * ... more to be invented
* **Voice recognition**: bots use `whisper` to transcribe audio messages.
* **Vision**: bots complete images as well as text
* **Observability**: logs and metrics are written into `influxdb` that can be visualised in `grafana`
* **Chat persistance**: chat history is saved in database
* **Extandable architecture**: the platform allows using not only telegram bot frontends but also other types like:
  * whatsapp
  * programmable telegram accounts (telethon)
  * any web based chat (i.e. websocket client talking to your server)
  * etc.
* **System prompts**: bots read system prompt in runtime from file. System prompt can be modified in runtime by the bot itself to persist relevant chat details and adjust bot's behaviour (dynamic sys prompts).
* **HTTP server**: bots can be configured via HTTP API. This allows to control all bots from a single control panel.

## Copilot notebook

Copilot notebook contains code that builds a systemp prompt out of all project files. Using this prompt the GPT can help you write code components and tests.