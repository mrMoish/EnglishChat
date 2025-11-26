from http import server, client
import os
import json

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
            'prompt':f'Create short, engaging messages in {target_lang} (1–2 sentences max), making sure to naturally include the following specific words: {words}',
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
                

                from elevenlabs.client import ElevenLabs
                client2 = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
                print('ELEVENLABS_API_KEY:', os.environ['ELEVENLABS_API_KEY'])

                audio = client2.text_to_speech.convert(
                    text=text,
                    voice_id="21m00Tcm4TlvDq8ikWAM",   # популярный голос (Rachel)
                    model_id="eleven_multilingual_v2"
                )

                file_path = "output.mp3"

                with open(file_path, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)


                boundary = "----1234567890"
                headers = {
                    "Content-Type": f"multipart/form-data; boundary={boundary}"
                }

                body_start = (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
                    f"{id}\r\n"
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="audio"; filename="sound.mp3"\r\n'
                    f"Content-Type: audio/mpeg\r\n\r\n"
                ).encode()

                with open(file_path, "rb") as f:
                    file_data = f.read()

                body_end = f"\r\n--{boundary}--\r\n".encode()

                body = body_start + file_data + body_end

                conn = client.HTTPSConnection("api.telegram.org")
                conn.request("POST", f"/bot{os.environ.get('BOT_TOKEN')}/sendAudio", body, headers)

                response = conn.getresponse()
                print(response.status)
                print(response.read().decode())
                
                
        else:
            pass
        conn.close()



def serve_forever():
    server.HTTPServer(('', int(os.environ['PORT'])), MyHandler).serve_forever()
    
# запуск на сервере, но не запускается при тестах
if __name__ == "__main__":
    serve_forever()
