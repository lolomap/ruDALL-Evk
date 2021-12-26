# -*- coding: utf-8 -*-
import asyncio
from threading import Thread
import requests
import VkApi
import time

chats_info = {}
alphabet = 'abcdefghijklmnopqrstuvwxyz'


class AsyncLoopThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


def get_request(text):
    request_text = text
    p = requests.get('https://rudalle.ru/demo')
    data = str(p.content)

    captcha_url = 'https://rudalle.ru/captcha/image/' + \
                  data.split('name="captcha_0" value="')[1].split('" required id="id_captcha_0"')[0]
    csrftoken = data.split('type="hidden" name="csrfmiddlewaretoken" value="')[1].split('">')[0]
    return {'captcha_url': captcha_url, 'csrf': csrftoken, 'cookies': p.cookies, 'text': request_text}


def send_request(text, captcha_url, captcha_inp, csrftoken, cookies):
    respond = requests.post('https://rudalle.ru/generate_image', headers={'UA': 'Chrome'},
                            cookies=cookies,
                            data={'text': text, 'captcha_0': captcha_url, 'captcha_1': captcha_inp,
                                  'csrfmiddlewaretoken': csrftoken})
    image_url = 'https://rudalle.ru/check_image/' + \
                respond.text.split('<a href="/check_image/')[1].split('"')[0]
    return image_url


async def process_message(session, event, chat_id):
    try:
        
        msg_text = event.obj.message['text'].lower()
        if chat_id == 281646826:
            VkApi.send_message('Тупой солодов', session, event)
        if 'иид' in msg_text or 'дукс' in msg_text:
            VkApi.send_message('Приплетено👍🏻', session, event)
        if 'пикча ' in msg_text:
            if 'пикча ' in msg_text:
                text = msg_text.split('пикча ')[1]
            else:
                text = msg_text.split('rd ')[1]
            r = get_request(text)
            if chat_id not in chats_info.keys():
                chats_info[chat_id] = []
            chats_info[chat_id].append(r)
            photo = VkApi.get_photo_to_send(r['captcha_url'], session, event)
            VkApi.send_message_photo('Отправьте текст капчи', photo, session, event)
        elif len(msg_text) == 4 and all(letter in alphabet for letter in msg_text):
            text = msg_text.upper()
            url = send_request(chats_info[chat_id][-1]['text'], chats_info[chat_id][-1]['captcha_url'].split('/')[-1],
                               text, chats_info[chat_id][-1]['csrf'], chats_info[chat_id][-1]['cookies'])
            VkApi.send_message('Пикча генерируется...', session, event)
            is_ready = True
            while is_ready:
                img_p = requests.get(url)
                if 'src="https://img.rudalle.ru/images' in str(img_p.text):
                    is_ready = False
                await asyncio.sleep(10)
            idd = str(img_p.content).find('src="https://img.rudalle.ru/images')
            img_url = str(img_p.content)[idd + 5:].split('"')[0]
            photo = VkApi.get_photo_to_send(img_url, session, event)
            VkApi.send_message_photo('Пикча по запросу ' + chats_info[chat_id][0]['text'], photo, session, event)
            chats_info[chat_id].pop(0)
        elif msg_text == '!сброс':
            del chats_info[chat_id][:]
            VkApi.send_message('Сброс бота', session, event)
    except Exception as ep:
        VkApi.send_message('Ошибка обработки. Возможно вы неправильно ввели капчу', session, event)
        print(ep)


async def main():
    try:
        print('Bot started')
        vk = VkApi.create_session()
        looph = AsyncLoopThread()
        looph.start()
        session = vk['session']
        longpoll = vk['longpoll']

        for event in longpoll.listen():
            if VkApi.is_event_message(event.type):
                chat_ide = event.obj.message['peer_id']

                asyncio.run_coroutine_threadsafe(process_message(session, event, chat_ide), looph.loop)

    except Exception as e:
        print(e)
        return


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(e)
            continue
