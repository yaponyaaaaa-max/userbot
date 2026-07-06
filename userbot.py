import asyncio
import random
from datetime import datetime, timedelta
from telethon import TelegramClient, events

API_ID = 7832255
API_HASH = "25d037f2d44d51691a7a9c92f2ed1a1d"

client = TelegramClient("my_userbot", API_ID, API_HASH)

TARGET_CHAT = "@username"  # ЗАМЕНИ НА СВОЙ КАНАЛ/ЧАТ/ЮЗЕРНЕЙМ
INTERVAL_MINUTES = 55       # ИНТЕРВАЛ В МИНУТАХ
MESSAGES_FILE = "data.txt"  # ФАЙЛ С СООБЩЕНИЯМИ

calendars = {}
auto_replies = {}
media_auto_replies = {}

def load_messages():
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("✦ Файл data.txt не найден")
        return []

def log_to_file(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

async def send_scheduled_messages():
    now = datetime.now()
    minutes_now = now.hour * 60 + now.minute
    next_interval = ((minutes_now // INTERVAL_MINUTES) + 1) * INTERVAL_MINUTES
    wait_seconds = (next_interval - minutes_now) * 60 - now.second
    if wait_seconds <= 0:
        wait_seconds += INTERVAL_MINUTES * 60

    print(f"✦ Первый запуск через {wait_seconds // 60} мин {wait_seconds % 60} сек")
    await asyncio.sleep(wait_seconds)

    while True:
        try:
            messages = load_messages()
            if messages:
                msg = random.choice(messages)
                await client.send_message(TARGET_CHAT, msg)
                log_to_file(f"Отправлено: {msg[:50]}...")
                print(f"✦ Отправлено: {msg[:50]}...")
            else:
                print("✦ Нет сообщений для отправки")
                log_to_file("✦ Нет сообщений в data.txt")
        except Exception as e:
            log_to_file(f"✦ Ошибка отправки: {e}")
            print(f"✦ Ошибка: {e}")
        await asyncio.sleep(INTERVAL_MINUTES * 60)

# ===== МЕНЮ =====
@client.on(events.NewMessage(pattern=r'\.menu$'))
async def menu_command(event):
    menu_text = """
✦ **МЕНЮ ЮЗЕРБОТА** ✦

✦ `.dmcnc @username` — календарь (продолжает существующий)
✦ `.dmcnr @username` — автоответчик
✦ `.dmcnrm @username` — медиа-автоответчик
✦ `.cln @username` — очистка календаря
✦ `.stop @username` — остановка автоответчика
✦ `.stopm @username` — остановка медиа-автоответчика
✦ `.readlog` — показать лог-файл
✦ `.ping` — проверить, жив ли юзербот
✦ `.menu` — показать это меню
    """
    await event.reply(menu_text)

# ===== ПИНГ =====
@client.on(events.NewMessage(pattern=r'\.ping$'))
async def ping_command(event):
    start = datetime.now()
    await event.reply('✦ Понг!')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(f'✦ Понг! ({ms:.2f} мс)')

# ===== ОСТАЛЬНЫЕ КОМАНДЫ =====
@client.on(events.NewMessage(pattern=r'\.dmcnc\s+(.+?)(?:\s+шапка)?$'))
async def calendar_command(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if not target:
        await event.reply('✦ Укажи username или ID')
        return
    user_id = int(target) if target.isdigit() else target
    if user_id not in calendars:
        calendars[user_id] = []
    calendars[user_id].append({
        'text': '✦ Отложенное сообщение',
        'time': datetime.now() + timedelta(hours=1)
    })
    log_to_file(f"Календарь для {target} продолжен ({len(calendars[user_id])} сообщений)")
    await event.reply(f'✦ Календарь для {target} продолжен ({len(calendars[user_id])} сообщений)')

@client.on(events.NewMessage(pattern=r'\.dmcnr\s+(.+?)(?:\s+шапка)?$'))
async def autoreply_command(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if not target:
        await event.reply('✦ Укажи username или ID')
        return
    user_id = int(target) if target.isdigit() else target
    auto_replies[user_id] = {'text': '✦ Я сейчас занят, отвечу позже!'}
    log_to_file(f"Автоответчик для {target} включен")
    await event.reply(f'✦ Автоответчик для {target} включен')

@client.on(events.NewMessage(pattern=r'\.dmcnrm\s+(.+?)(?:\s+шапка)?$'))
async def media_autoreply_command(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if not target:
        await event.reply('✦ Укажи username или ID')
        return
    replied = await event.get_reply_message()
    if not replied or not replied.media:
        await event.reply('✦ Нужно ответить на медиа-сообщение')
        return
    user_id = int(target) if target.isdigit() else target
    media_auto_replies[user_id] = {
        'media': replied.media,
        'caption': replied.text or '✦ Медиа-ответ'
    }
    log_to_file(f"Медиа-автоответчик для {target} включен")
    await event.reply(f'✦ Медиа-автоответчик для {target} включен')

@client.on(events.NewMessage(pattern=r'\.cln\s+(.+)$'))
async def clear_calendar(event):
    target = event.raw_text.split()[1]
    user_id = int(target) if target.isdigit() else target
    if user_id in calendars:
        del calendars[user_id]
        log_to_file(f"Календарь для {target} очищен")
        await event.reply(f'✦ Календарь для {target} очищен')
    else:
        await event.reply(f'✦ Календарь для {target} не найден')

@client.on(events.NewMessage(pattern=r'\.stop\s+(.+)$'))
async def stop_autoreply(event):
    target = event.raw_text.split()[1]
    user_id = int(target) if target.isdigit() else target
    if user_id in auto_replies:
        del auto_replies[user_id]
        log_to_file(f"Автоответчик для {target} остановлен")
        await event.reply(f'✦ Автоответчик для {target} остановлен')
    else:
        await event.reply(f'✦ Автоответчик для {target} не найден')

@client.on(events.NewMessage(pattern=r'\.stopm\s+(.+)$'))
async def stop_media_autoreply(event):
    target = event.raw_text.split()[1]
    user_id = int(target) if target.isdigit() else target
    if user_id in media_auto_replies:
        del media_auto_replies[user_id]
        log_to_file(f"Медиа-автоответчик для {target} остановлен")
        await event.reply(f'✦ Медиа-автоответчик для {target} остановлен')
    else:
        await event.reply(f'✦ Медиа-автоответчик для {target} не найден')

@client.on(events.NewMessage(pattern=r'\.readlog$'))
async def read_log_command(event):
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            log_content = f.read()[-1500:]
            await event.reply(f'✦ Лог (последние 1500 символов):\n{log_content}')
    except FileNotFoundError:
        await event.reply('✦ Лог-файл пуст')

@client.on(events.NewMessage)
async def handle_incoming(event):
    if event.out:
        return
    sender_id = event.sender_id
    if sender_id in auto_replies:
        await asyncio.sleep(1)
        await event.reply(auto_replies[sender_id]['text'])
        return
    if sender_id in media_auto_replies:
        await asyncio.sleep(1)
        data = media_auto_replies[sender_id]
        await event.reply(data['caption'], file=data['media'])
        return

async def main():
    await client.start()
    print('✦ Юзербот запущен!')
    print(f'✦ Отправка сообщений каждые {INTERVAL_MINUTES} минут')
    print('✦ Команды: .menu, .ping, .dmcnc, .dmcnr, .dmcnrm, .cln, .stop, .stopm, .readlog')
    asyncio.create_task(send_scheduled_messages())
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
