from http import server, client
import os
import json

import asyncio
import edge_tts

import os
import http.client
import uuid

def send_audio_bytes(bot_token: str, chat_id: str, audio_bytes: bytes,
                     filename: str = "voice.mp3", mime_type: str = "audio/mpeg"):
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    crlf = "\r\n"

    # Поля формы (chat_id и другие текстовые поля)
    part_chat_id = (
        f"--{boundary}{crlf}"
        f'Content-Disposition: form-data; name="chat_id"{crlf}{crlf}'
        f"{chat_id}{crlf}"
    ).encode()

    # Можно добавить подпись:
    # part_caption = (f"--{boundary}{crlf}"
    #                 f'Content-Disposition: form-data; name="caption"{crlf}{crlf}'
    #                 f"My caption{crlf}').encode()

    # Файл как часть multipart
    part_file_header = (
        f"--{boundary}{crlf}"
        f'Content-Disposition: form-data; name="audio"; filename="{filename}"{crlf}'
        f"Content-Type: {mime_type}{crlf}{crlf}"
    ).encode()

    body_end = (crlf + f"--{boundary}--{crlf}").encode()

    body = part_chat_id + part_file_header + audio_bytes + body_end

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
        # "User-Agent": "MyBot/1.0"  # опционально
    }

    conn = http.client.HTTPSConnection("api.telegram.org")
    path = f"/bot{bot_token}/sendAudio"
    conn.request("POST", path, body, headers)
    resp = conn.getresponse()
    resp_data = resp.read()
    conn.close()
    return resp.status, resp_data



def generate_tts_sync(text):
    filename = "speech.mp3"

    async def _gen():
        communicate = edge_tts.Communicate(text, voice="es-ES-AlvaroNeural")
        await communicate.save(filename)

    asyncio.run(_gen())

    with open(filename, "rb") as f:
        return f.read()



def encode_url(msg: bytes) -> str:
    result = ''
    for byte in msg.encode('utf-8'):
        match byte:
            # цифры 0-9
            case n if 0x30 <= n <= 0x39:
                result += chr(n)
            # латинские буквы A-Z
            case n if 0x41 <= n <= 0x5A:
                result += chr(n)
            # латинские буквы a-z
            case n if 0x61 <= n <= 0x7A:
                result += chr(n)
            # всё остальное кодируем
            case n:
                result += f"%{n:02X}"
    return result

def send_telegram_message(conn, chat_id: int, text: str) -> int:
    conn.request('GET', f'/bot{os.environ.get('BOT_TOKEN')}/sendMessage?chat_id={chat_id}&text={text}')
    response = conn.getresponse()
    message_id = json.loads(response.read())['result']['message_id']
    return message_id

def send_telegram_message_html(conn, chat_id: int, text: str) -> int:
    conn.request('GET', f'/bot{os.environ.get('BOT_TOKEN')}/sendMessage?chat_id={chat_id}&text={text}&parse_mode=HTML')
    response = conn.getresponse()



def edit_tg_msg(connection_to_telegram, chat_id: int, message_id: int, text: str):
    import urllib.parse
    reply_markup = urllib.parse.quote(
        '{"inline_keyboard":[[{"text":"мини-урок","callback_data":"/lesson"}]]}'
    )
    connection_to_telegram.request('GET',
        f'/bot{os.environ.get('BOT_TOKEN')}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={text}&reply_markup={reply_markup}')



def translate(message, source_lang, target_lang):

    # TODO: сохранять время запроса

    connection = client.HTTPSConnection('openrouter.ai')
    connection.request(
        'POST', '/api/v1/chat/completions',
        json.dumps({
            'model': 'openai/gpt-4o',
            'prompt':f'Be as brief as possible! Translate from {source_lang} to {target_lang}: {message}',
        }), {
            "Content-Type": "application/json",
            'Authorization': os.environ['OPENROUTER_API_KEY']
        })
    response = connection.getresponse()

    response = json.loads(response.read()) 
    row_translate = str(response['choices'][0]['text'])

    connection.close()
    return row_translate

def text_lesson(words, target_lang):
#     Create short, engaging messages in Spanish (1–2 sentences max), making sure to naturally include the following specific words:
# [INSERT WORDS HERE]
# The tone should be friendly, modern, and conversational.
# Avoid complex grammar. Keep it simple and catchy. Additional emojis are allowed if they help engagement.
    connection = client.HTTPSConnection('openrouter.ai')
    connection.request(
        'POST', '/api/v1/chat/completions',
        json.dumps({
            'model': 'openai/gpt-4o',
            'prompt':f'Create short, engaging messages in {target_lang} (1–2 sentences max), making sure to naturally include the following specific words: {words}. The tone should be friendly, modern, and conversational. Avoid complex grammar. Keep it simple and catchy.',
        }), {
            "Content-Type": "application/json",
            'Authorization': os.environ['OPENROUTER_API_KEY']
        })
    response = connection.getresponse()

    response = json.loads(response.read()) 
    row_translate = str(response['choices'][0]['text'])

    connection.close()
    return row_translate


class MyHandler(server.SimpleHTTPRequestHandler):
    def do_POST(self):
        print('do_POST')
        self.send_response(200)
        self.end_headers()


        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = __import__('json').loads(post_data)

        

        conn = client.HTTPSConnection('api.telegram.org')
        if 'message' in data:
            print('message found')
            id = data['message']['from']['id']
            if 'text' in data['message']:
                message = data['message']['text']
                
                match message:
                    case '/start':
                        hello_msg = 'Это бот для ежедневных мини-уроков испанского.\n\n  На данный момент этот бот работает в режиме переводчика c любого языка мира на русский и с русского на испанский🇪🇸 🇦🇷\n\nпреимущества:\n✅ сохраняетcя вся ваша история перевода, в удобном формате чата на всех устройствах, где есть телеграм\n\nв будущем:\n🚀 мы добавим мини-уроки, включающие аудиозапись, текст и вопросы, вы сможете каждый день повторять нужные лично вам фразы 🚀🚀🚀'
                        send_telegram_message(conn, id, encode_url(hello_msg))
                        send_telegram_message_html(conn, id, encode_url('<b>Начнем!? Напишите слово или фразу на русском или испанском!</b>'))
                    case _:
                        
                        
                        
                        if __import__('re').search(r"[\u0400-\u04FF]", message):
                            target_lang = 'Spanish'
                            source_lang = 'Russian'
                        else:
                            target_lang = 'Russian'
                            source_lang = 'Spanish'



                        msg = '⏳' if bool(hash(object()) % 2) else '⌛️'
                        msg_id = send_telegram_message(conn,id, encode_url(msg))
                        tr = translate(message, source_lang, target_lang)
                        edit_tg_msg(conn, id, msg_id, encode_url(tr))


            else:
                send_telegram_message(conn, id, encode_url('к сожалению, этот бот пока работает только с текстом 🥲'))

        elif 'callback_query' in data:
            print(data)
            if data['callback_query']['data'] == '/lesson':
                id = data['callback_query']['from']['id']
                msg = '⏳' if bool(hash(object()) % 2) else '⌛️'
                msg_id = send_telegram_message(conn,id, encode_url(msg))

                
                text = text_lesson(data['callback_query']['message']['text'].replace(" ", ", "), 'Spanish')
                

                print('Generated lesson text:')
                print(text)


                # boundary = "----1234567890"
                # headers = {
                #     "Content-Type": f"multipart/form-data; boundary={boundary}"
                # }

                # body_start = (
                #     f"--{boundary}\r\n"
                #     f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
                #     f"{id}\r\n"
                #     f"--{boundary}\r\n"
                #     f'Content-Disposition: form-data; name="audio"; filename="sound.mp3"\r\n'
                #     f"Content-Type: audio/mpeg\r\n\r\n"
                # ).encode()

                # with open(file_path, "rb") as f:
                #     file_data = f.read()

                # body_end = f"\r\n--{boundary}--\r\n".encode()

                # body = body_start + file_data + body_end

                # conn = client.HTTPSConnection("api.telegram.org")
                # conn.request("POST", f"/bot{os.environ.get('BOT_TOKEN')}/sendAudio", body, headers)


                audio_bytes = generate_tts_sync(text)

                
                BOT_TOKEN = os.environ.get("BOT_TOKEN")
                CHAT_ID = id  # ставь свой chat_id
                # audio_bytes = ...  # bytes сгенерированного mp3/ogg
                status, data = send_audio_bytes(BOT_TOKEN, CHAT_ID, audio_bytes=audio_bytes, filename="voz.mp3")
                print(status, data[:300])

                # response = conn.getresponse()
                # print(response.status)
                # print(response.read().decode())



                conn.request(
                    "GET",
                    f"/bot{os.environ.get('BOT_TOKEN')}/deleteMessage?chat_id={id}&message_id={msg_id}"
                )


                
                
        else:
            pass
        conn.close()



def serve_forever():
    server.HTTPServer(('', int(os.environ['PORT'])), MyHandler).serve_forever()
    
# запуск на сервере, но не запускается при тестах
if __name__ == "__main__":
    serve_forever()
