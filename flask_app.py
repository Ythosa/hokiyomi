# -*- coding: utf-8 -*-
from flask import Flask, request
import vk_api
from vk_api.utils import get_random_id

from tokens import API_TOKEN, CONFIRMATION_CODE

app = Flask(__name__)
vk_session = vk_api.VkApi(token=API_TOKEN)
vk = vk_session.get_api()

confirmation_code = CONFIRMATION_CODE


@app.route('/my_bot', methods=['POST'])
def bot():
    data = request.get_json(force=True, silent=True)

    if not data or 'type' not in data:
        return 'error'

    if data['type'] == 'confirmation':
        return confirmation_code
    elif data['type'] == 'message_new':
        text = data['object']["text"]
        if text.lower() == "/echo":
            from_id = data['object']['peer_id']
            vk.messages.send(
                message='Hi :3',
                random_id=get_random_id(),
                peer_id=from_id
            )
            return 'ok'

    return 'ok'
