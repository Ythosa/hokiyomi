import os
import subprocess
import sqlite3

import db
from exceptions import InvalidAttachments
from tokens import API_TOKEN


def add_person_picture(path, group_id, caption, bg):
    """Add new wall newspaper element to db"""
    if bg not in get_backgrounds():
        raise InvalidAttachments("Invalid bg name :c")

    pic = _get_picture_from_attachments(path)
    pic = sqlite3.Binary(pic)
    db.insert("images", {
        "group_id": group_id,
        "caption": caption,
        "image": pic,
        "bg": bg
    })

    if not pic:
        raise InvalidAttachments("You didn't attach a photo :c")


def _get_picture_from_attachments(path):
    """Get picture bytes from telegram server"""
    url = 'https://api.telegram.org/file/bot' + API_TOKEN + '/' + path

    pic_path = './photos/pic.jpg'
    curl_command = f'curl {url} > {pic_path}'

    data = subprocess.run(curl_command, shell=True)

    if data.returncode != 0:
        raise InvalidAttachments('Something evil has happened :c')

    with open(pic_path, 'rb') as f:
        data = f.read()

    return data


def remove_last(chat_id):
    """Remove last added element to db in chat with chat_id"""
    cur = db.get_cursor()
    cur.execute(
        f"DELETE FROM 'images' WHERE id = "
        f"(SELECT id FROM 'images' WHERE group_id = {chat_id} "
        f"ORDER BY id DESC LIMIT 1)"
    )


def get_backgrounds():
    """Returns list of all available backgrounds"""
    bgs = os.listdir('./backgrounds')
    bgs = [i[:-4] for i in bgs]
    return bgs


def get_wall_newspaper(chat_id, title):
    """Generate wall newspaper for chat by using ML models"""
    pics = db.fetchall('images', 'group_id, image, caption, group_id'.split(', '))
    paths = []
    for p in pics:
        if p['group_id'] == chat_id:
            fname = f'./toml/{k}.jpg'
            paths.append(fname)
            bg = p['bg']
            with open(fname, 'wb') as f:
                f.write(p['image'])

            subprocess.run(
                f'cutimage --image {fname} --background ./backgrounds/{bg}.jpg '
                f'--output_path ./output/{fname}.jpg', shell=True
            )

    gen_wns_command = f"papper --title '{title}' " \
        f"--images unnamed.png --images FullSizeRender-18-09-17-11-43.jpg --descs 'any' --descs 'school'"
    for p in paths:
        gen_wns_command += f'--images {p} '

    subprocess.run(gen_wns_command, shell=True)

