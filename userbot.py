import asyncio
import random
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ===== СЕССИЯ =====
SESSION = "1AZWarzUBu1oI9h_g78W0oqcKfDLve8NiYQLBdA5-Tw-zz6HSKd37sEYGiR5f_T0TrM3zRuHEBXwwirA_PlIiLdIPGPKQzKQYTi5Kc5MW5qU1hfGKlp8kgTMYxRF14mq4WuaPTw2L5Yt75JRjD_X3i7aWZYL2X9BjBwBdk6iMJOmlIQg1Yq662ANjej8VLuhb68Twt-uyRw7s3jbgD3-29pcq1-sxWpFJbOhMAq8itkTWcQuQ2DFIou73djHKV5wC2JSwFWV0hn6jY30pH3LgHzSNwMSNNNleMHnnCwvxCg9Xqy3h4G7AggEFh5IwOM7RiH3bJIEkfb6_kpyO-pY0nVq0uWeGok0="

client = TelegramClient(StringSession(SESSION), 7832255, "25d037f2d44d51691a7a9c92f2ed1a1d")

# ===== НАСТРОЙКИ =====
INTERVAL_MINUTES = 55
MESSAGES_FILE = "data.txt"

calendars = {}
auto_replies = {}
media_auto_replies = {}

# ===== ВИДЕО ДЛЯ .ping (замени на своё) =====
PING_VIDEO = None  # Сюда можно вставить file_id или путь к видео

def load_messages():
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def log_to_file(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

# ===== ОТПРАВКА ПО РАСПИСАНИЮ =====
async def send_scheduled_messages():
    await asyncio.sleep(10)
    while True:
        for user_id, msgs in list(calendars.items()):
            if msgs:
                msg = random.choice(msgs)
                try:
                    await client.send_message(user_id, msg)
                    log_to_file(f"Календарь для {user_id}: {msg[:30]}...")
                except Exception as e:
                    log_to_file(f"Ошибка отправки {user_id}: {e}")
        await asyncio.sleep(INTERVAL_MINUTES * 60)

# ===== МЕНЮ (с by domician) =====
@client.on(events.NewMessage(pattern=r'\.menu$'))
async def menu_command(event):
    menu_text = """
✦ **МЕНЮ ЮЗЕРБОТА** ✦

.dmcnc @username — календарь (если без юзера — для чата)
.dmcnr @username — автоответчик
.dmcnrm @username — медиа-автоответчик
.cln @username — очистка календаря
.stop @username — стоп автоответ
.stopm @username — стоп медиа
.readlog — лог
.ping — пинг (с видео, если настроено)
.menu — меню

✦ by domician ✦
    """
    await event.reply(menu_text)

# ===== .ping С ВИДЕО =====
@client.on(events.NewMessage(pattern=r'\.ping$'))
async def ping_command(event):
    if PING_VIDEO:
        try:
            await event.reply("✦ Понг!", file=PING_VIDEO)
        except:
            await event.reply("✦ Понг! (видео не загрузилось)")
    else:
        await event.reply("✦ Понг! (видео не настроено)")

# ===== КАЛЕНДАРЬ =====
@client.on(events.NewMessage(pattern=r'\.dmcnc\s*(?:@(\S+))?'))
async def calendar_command(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if target and target.startswith('@'):
        target = target[1:]
    else:
        target = None

    user_id = None
    if target:
        try:
            entity = await client.get_entity(target)
            user_id = entity.id
        except:
            await event.reply('✦ Юзернейм не найден')
            return
    else:
        user_id = event.chat_id

    if user_id not in calendars:
        calendars[user_id] = []
    calendars[user_id].append({
        'text': '✦ Отложенное сообщение',
        'time': datetime.now() + timedelta(hours=1)
    })
    log_to_file(f"Календарь для {user_id} продолжен ({len(calendars[user_id])} сообщений)")
    await event.reply(f'✦ Календарь для {target or "этого чата"} продолжен ({len(calendars[user_id])} сообщений)')

# ===== АВТООТВЕТЧИК =====
@client.on(events.NewMessage(pattern=r'\.dmcnr\s*(?:@(\S+))?'))
async def autoreply_command(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if target and target.startswith('@'):
        target = target[1:]
    else:
        target = None

    user_id = None
    if target:
        try:
            entity = await client.get_entity(target)
            user_id = entity.id
        except:
            await event.reply('✦ Юзернейм не найден')
            return
    else:
        user_id = event.chat_id

    auto_replies[user_id] = {'text': '✦ Я сейчас занят, отвечу позже!'}
    log_to_file(f"Автоответчик для {user_id} включен")
    await event.reply(f'✦ Автоответчик для {target or "этого чата"} включен')

# ===== МЕДИА-АВТООТВЕТЧИК =====
@client.on(events.NewMessage(pattern=r'\.dmcnrm\s*(?:@(\S+))?'))
async def media_autoreply_command(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if target and target.startswith('@'):
        target = target[1:]
    else:
        target = None

    user_id = None
    if target:
        try:
            entity = await client.get_entity(target)
            user_id = entity.id
        except:
            await event.reply('✦ Юзернейм не найден')
            return
    else:
        user_id = event.chat_id

    replied = await event.get_reply_message()
    if not replied or not replied.media:
        await event.reply('✦ Нужно ответить на медиа-сообщение')
        return
    media_auto_replies[user_id] = {
        'media': replied.media,
        'caption': replied.text or '✦ Медиа-ответ'
    }
    log_to_file(f"Медиа-автоответчик для {user_id} включен")
    await event.reply(f'✦ Медиа-автоответчик для {target or "этого чата"} включен')

# ===== ОЧИСТКА =====
@client.on(events.NewMessage(pattern=r'\.cln\s*(?:@(\S+))?'))
async def clear_calendar(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if target and target.startswith('@'):
        target = target[1:]
    else:
        target = None

    user_id = None
    if target:
        try:
            entity = await client.get_entity(target)
            user_id = entity.id
        except:
            await event.reply('✦ Юзернейм не найден')
            return
    else:
        user_id = event.chat_id

    if user_id in calendars:
        del calendars[user_id]
        log_to_file(f"Календарь для {user_id} очищен")
        await event.reply(f'✦ Календарь для {target or "этого чата"} очищен')
    else:
        await event.reply(f'✦ Календарь для {target or "этого чата"} не найден')

# ===== ОСТАНОВКА =====
@client.on(events.NewMessage(pattern=r'\.stop\s*(?:@(\S+))?'))
async def stop_autoreply(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if target and target.startswith('@'):
        target = target[1:]
    else:
        target = None

    user_id = None
    if target:
        try:
            entity = await client.get_entity(target)
            user_id = entity.id
        except:
            await event.reply('✦ Юзернейм не найден')
            return
    else:
        user_id = event.chat_id

    if user_id in auto_replies:
        del auto_replies[user_id]
        log_to_file(f"Автоответчик для {user_id} остановлен")
        await event.reply(f'✦ Автоответчик для {target or "этого чата"} остановлен')
    else:
        await event.reply(f'✦ Автоответчик для {target or "этого чата"} не найден')

# ===== ОСТАНОВКА МЕДИА =====
@client.on(events.NewMessage(pattern=r'\.stopm\s*(?:@(\S+))?'))
async def stop_media_autoreply(event):
    args = event.raw_text.split()
    target = args[1] if len(args) > 1 else None
    if target and target.startswith('@'):
        target = target[1:]
    else:
        target = None

    user_id = None
    if target:
        try:
            entity = await client.get_entity(target)
            user_id = entity.id
        except:
            await event.reply('✦ Юзернейм не найден')
            return
    else:
        user_id = event.chat_id

    if user_id in media_auto_replies:
        del media_auto_replies[user_id]
        log_to_file(f"Медиа-автоответчик для {user_id} остановлен")
        await event.reply(f'✦ Медиа-автоответчик для {target or "этого чата"} остановлен')
    else:
        await event.reply(f'✦ Медиа-автоответчик для {target or "этого чата"} не найден')

# ===== ЛОГ =====
@client.on(events.NewMessage(pattern=r'\.readlog$'))
async def read_log_command(event):
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            await event.reply(f'✦ Лог:\n{f.read()[-1000:]}')
    except:
        await event.reply('✦ Лог пуст')

# ===== АВТООТВЕТ НА ВХОДЯЩИЕ =====
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

# ===== ЗАПУСК =====
async def main():
    await client.start()
    print('✦ Юзербот запущен! by domician')
    asyncio.create_task(send_scheduled_messages())
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
