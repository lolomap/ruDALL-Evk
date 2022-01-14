# -*- coding: utf-8 -*-

import json
import os
import random

import requests

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_session():
    api = vk_api.VkApi(token='4b3b846a09bce47afc723a631d635fb291f7cee3a236995a923fc02194174c8b050f346376de0e1d3efed')
    longpoll = VkBotLongPoll(api, 208843579)
    session = api.get_api()
    print('session created')
    return {'session': session, 'longpoll': longpoll}


def get_photo_to_send(url, session, event):
    photo_file = session.photos.getMessagesUploadServer(peer_id=event.obj.message['peer_id'])
    r_data = {'photo': (str(random.randint(10, 100000)) + '.jpg', requests.get(url).content)}
    photo_data = requests.post(photo_file['upload_url'], files=r_data).json()
    photo = session.photos.saveMessagesPhoto(server=photo_data['server'],
                                             photo=photo_data['photo'],
                                             hash=photo_data['hash'])[0]
    return photo


def get_chat_users(msg, session):
    users = session.messages.getConversationMembers(peer_id=msg['peer_id'])
    profiles = []
    for user in users['profiles']:
        profiles.append(user['id'])
    return profiles


def get_user_id(short_name, session):
    user = session.users.get(user_ids=short_name)[0]
    return user['id']

def get_user(short_name, session):
    user = session.users.get(user_ids=short_name)[0]
    return user


def send_message(msg, session, event):
    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message=msg,
                          random_id=random.randint(100000, 999999))


def send_message_photo(msg, photo, session, event):
    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message=msg,
                          attachment='photo' + str(photo['owner_id']) + '_' + str(photo['id']),
                          random_id=random.randint(100000, 999999))


def is_event_message(event):
    if event == VkBotEventType.MESSAGE_NEW:
        return True
    else:
        return False
