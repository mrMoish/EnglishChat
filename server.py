from http import server, client

start = False

def encode_url(hello_msg: bytes) -> str:
    result = ''
    for byte in hello_msg.encode('utf-8'):
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

def send_telegram_message(chat_id: int, text: str) -> int:
    conn = client.HTTPSConnection('api.telegram.org')
    conn.request('GET', f'/bot{__import__('os').environ.get('BOT_TOKEN')}/sendMessage?chat_id={chat_id}&text={text}')
    response = conn.getresponse()
    message_id = __import__('json').loads(response.read())['result']['message_id']
    return message_id

class MyHandler(server.SimpleHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = __import__('json').loads(post_data)



     
        match data['message']['text']:
            case '/start':
                hello_msg = encode_url('Отправьте мне "да",\n если ваш родной язык — русский,\n и Вы хотите учить английский')
                send_telegram_message(data['message']['from']['id'], hello_msg)
            case _:
                global start
                if start:
                    print("начинаем урок")     
                    send_telegram_message(data['message']['from']['id'], encode_url('Урок начался!'))
                elif data['message']['text'] in {'да' , 'Да' , 'ДА' , 'yes' , 'Yes' , 'YES' , 'DA' , 'Da' , 'da'}:
                    start = True
                    send_telegram_message(data['message']['from']['id'], encode_url('Отлично!\nТеперь отправьте мне фразу на русском или английском языке, которую хотите выучить.\n\n И с помощью мини-уроков, включающих аудиозапись, текст и вопросы, вы сможете каждый день повторять нужные вам фразы')) 
                else:
                    send_telegram_message(data['message']['from']['id'], encode_url('Вот список доступных ботов для каждого языка:\nRU → EN\nRU → ES\n\nЕсли вашего языка нет в списке, напишите нам об этом (@mr_Moish), и мы постараемся добавить его в ближайшее время\n\nПерейдите в нужный бот или подтвердите, отправив "да", что ваш родной язык — русский, и вы хотите учить английский'))





def serve_forever():
    server.HTTPServer(('', int(__import__('os').environ['PORT'])), MyHandler).serve_forever()
    
# запуск на сервере, но не запускается при тестах
if __name__ == "__main__":
    serve_forever()
