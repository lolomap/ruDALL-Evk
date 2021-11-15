# -*- coding: utf-8 -*-
import asyncio

import requests
import VkApi
import time


chats_info = {}


def get_request(text):
	request_text = text
	p = requests.get('https://rudalle.ru/demo')
	data = str(p.content)

	captcha_url = 'https://rudalle.ru/captcha/image/' +\
				  data.split('name="captcha_0" value="')[1].split('" required id="id_captcha_0"')[0]
	csrftoken = data.split('type="hidden" name="csrfmiddlewaretoken" value="')[1].split('">')[0]
	return {'captcha_url': captcha_url, 'csrf': csrftoken, 'cookies': p.cookies, 'text': request_text}


def send_request(text, captcha_url, captcha_inp, csrftoken, cookies):
	respond = requests.post('https://rudalle.ru/generate_image', headers={'UA': 'Chrome'},
							cookies=cookies,
							data={'text': text, 'captcha_0': captcha_url, 'captcha_1': captcha_inp,
								  'csrfmiddlewaretoken': csrftoken})
	print(respond.status_code)
	image_url = 'https://rudalle.ru/check_image/' +\
				respond.text.split('<a href="/check_image/')[1].split('"')[0]
	return image_url


async def process_message(session, event, chat_id):
	try:
		msg_text = event.obj.message['text'].lower()
		if 'пикча ' in msg_text:
			text = msg_text.split('пикча ')[1]
			r = get_request(text)
			chats_info[chat_id] = r
			photo = VkApi.get_photo_to_send(r['captcha_url'], session, event)
			VkApi.send_message_photo('Отправьте captcha [ТЕКСТ С КАПЧИ]', photo, session, event)
		elif 'captcha ' in msg_text:
			text = msg_text.split('captcha ')[1].upper()
			url = send_request(chats_info[chat_id]['text'], chats_info[chat_id]['captcha_url'].split('/')[-1], text,
							   chats_info[chat_id]['csrf'], chats_info[chat_id]['cookies'])
			VkApi.send_message('Пикча генерируется...', session, event)
			is_ready = True
			while is_ready:
				img_p = requests.get(url)
				if 'src="https://img.rudalle.ru/images' in str(img_p.text):
					is_ready = False
				time.sleep(30)
			idd = str(img_p.content).find('src="https://img.rudalle.ru/images')
			img_url = str(img_p.content)[idd+5:].split('"')[0]
			print(img_url)
			photo = VkApi.get_photo_to_send(img_url, session, event)
			VkApi.send_message_photo('Пикча по запросу ' + chats_info[chat_id]['text'], photo, session, event)
	except:
		VkApi.send_message('Ошибка. Возможно вы неправильно ввели капчу', session, event)


async def main():
		print('Bot started')
		vk = VkApi.create_session()
		session = vk['session']
		longpoll = vk['longpoll']
		for event in longpoll.listen():
			if VkApi.is_event_message(event.type):
				#print('Message catched')
				chat_ide = event.obj.message['peer_id']
				coroutin = process_message(session, event, chat_ide)
				coroutin.send(None)


if __name__ == '__main__':
	while True:
		try:
			loop = asyncio.get_event_loop()
			asyncio.ensure_future(main())
			loop.run_forever()
		except:
			pass
