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
    conn.request('GET', f'/bot{__import__('os').environ.get('BOT_TOKEN')}/sendMessage?chat_id={chat_id}&text={text}')
    response = conn.getresponse()
    message_id = json.loads(response.read())['result']['message_id']
    return message_id

def edit_tg_msg(connection_to_telegram, chat_id: int, message_id: int, text: str):
    connection_to_telegram.request('GET',
        f'/bot{__import__('os').environ.get('BOT_TOKEN')}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={text}')

def deepl(message, target_lang):

    # TODO: сохранять время запроса

    connection = client.HTTPSConnection('api-free.deepl.com')
    connection.request(
        'POST', '/v2/translate',
        json.dumps({
            'text': [message],
            'target_lang': target_lang
            # TODO: указать язык из кого переводить
        }), {
            "Content-Type": "application/json",
            'Authorization': os.environ['DEEPL_API_KEY']
        })
    response = connection.getresponse()

    response = json.loads(response.read()) 

    row_translate = str(response['translations'][0]['text'])
  
    connection.close()
    return row_translate

def gpt_translate(message, target_lang):

    # TODO: сохранять время запроса

    connection = client.HTTPSConnection('openrouter.ai')
    
    connection.request(
        'POST', '/api/v1/chat/completions',
        json.dumps({
        # "model": "openai/gpt-5",
        'model': 'x-ai/grok-4',
        "messages": [
            {
            "role": "user",
            "content": 'Provide only all possible natural Russian translations of the following text: ' + message,
            },
        ],
        }), {
      "Content-Type": "application/json",
      "Authorization": os.environ['OPENROUTER_API_KEY'],
      "X-Custom-Header": "custom-value",
    })

    response = connection.getresponse()

    response = json.loads(response.read()) 


    translate = response['choices'][0]['message']['content']

  
    connection.close()
    return translate

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
            id = data['message']['from']['id']
            if 'text' in data['message']:
                message = data['message']['text']
                
                match message:
                    case '/start':
                        hello_msg = 'Это бот для ежедневных мини-уроков испанского.\n\n  На данный момент этот бот работает в режиме переводчика c любого языка мира на русский и с русского на испанский🇪🇸 🇦🇷\n\nпреимущества:\n✅ сохраняетcя вся ваша история перевода, в удобном формате чата на всех устройствах, где есть телеграм\n\nв будущем:\n🚀 мы добавим мини-уроки, включающие аудиозапись, текст и вопросы, вы сможете каждый день повторять нужные лично вам фразы 🚀🚀🚀\n\nНачнем!? Напишите слово или фразу на русском или испанском'
                        send_telegram_message(conn, id, encode_url(hello_msg))
                    case _:
                        
                        
                        

                        target_lang = 'ES' if __import__('re').fullmatch(r"[\u0400-\u04FF\s]+", message) else 'RU'
                        msg = '⏳' if bool(hash(object()) % 2) else '⌛️'
                        if len(message.split()) == 1:
                            msg_id = send_telegram_message(conn,id, encode_url('Одно слово переводится дольше (примерно 30 секунд), потому что будет использоваться более мощный инструмент перевода, чтобы выдать более полный список возможных переводов этого слова. Пожалуйста, подождите ⏳'))
                            tr = gpt_translate(message, target_lang)
                        else:
                            msg_id = send_telegram_message(conn,id, encode_url(msg))
                            tr = deepl(message, target_lang)
                        edit_tg_msg(conn, id, msg_id, encode_url(tr))
            else:
                send_telegram_message(conn, id, encode_url('к сожалению, этот бот пока работает только с текстом 🥲'))

        else:
            pass
        conn.close()



def serve_forever():
    server.HTTPServer(('', int(os.environ['PORT'])), MyHandler).serve_forever()
    
# запуск на сервере, но не запускается при тестах
if __name__ == "__main__":
    serve_forever()
