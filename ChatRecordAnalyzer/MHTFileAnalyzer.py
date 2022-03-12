#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :MHTFileAnalyzer.py
# @Time      :2022/2/11 12:12
# @Author    :Amundsen Severus Rubeus Bjaaland


import os
import re
import base64

from bs4 import BeautifulSoup as bs

from ChatRecordAnalyzer.Object import ChatRecord


class QQMhtFile(object):
    """QQ的消息记录导出文件(MHT格式保存)的对应信息保存类"""

    def __init__(self):
        self.creator = "Tencent MsgMgr"
        self.version = "1.0"
        self.encoding = "utf-8"
        self.type = "text/html"
        self.split = ""
        self.chat_record = ChatRecord()


def _file_header(mht: QQMhtFile, data: str):
    header = data[1:-1].replace("\t", "").replace(": ", ":").replace(";", "").replace("=\"", ":\"")
    info_dict = {i.split(":")[0]: i.split(":")[1] for i in header.split("\n")}
    mht.creator = re.match("<Save by (.*?)>", info_dict["From"]).group(1)
    mht.encoding = info_dict["charset"]
    mht.version = info_dict["MIME-Version"]
    mht.type = info_dict["type"]
    mht.split = "--" + info_dict["boundary"].replace("\"", "")
    return None


def _analyze_block_header(block: str):
    block_info = block.split("\n\n")[0].split("\n")
    return {info.split(":")[0]: info.split(":")[1].replace(" ", "") for info in block_info}


def _analyze_html(mht: QQMhtFile, block_content: str):
    html = bs(block_content, "lxml")
    info_tags = html.find_all("tr")
    person_info = info_tags[:4]
    chat_data = info_tags[4:]
    mht.chat_record.group = person_info[1].text.split(":")[1]
    mht.chat_record.name = person_info[2].text.split(":")[1]
    date_buffer = [""]
    null_buffer = []
    for one_record in chat_data:
        date_tag = one_record.find("div")
        if not date_tag:
            date_buffer[0] = one_record.text.split(":")[1].replace(" ", "")
            continue
        image_tag = one_record.find("img")
        if image_tag:
            message = re.match("(.*?)(\d{1,2}\:\d\d\:\d\d)(.*?)##Finish", one_record.text + "##Finish")
            mht.chat_record.append_message(
                message.group(3) + image_tag["src"],
                "Image",
                message.group(2),
                date_buffer[0],
                message.group(1)
            )
            continue
        message = re.match("(.*?)(\d{1,2}\:\d\d\:\d\d)(.*?)##Finish", one_record.text + "##Finish")
        if not message.group(3):
            null_buffer.append(one_record)
        mht.chat_record.append_message(
            message.group(3),
            "Text",
            message.group(2),
            date_buffer[0],
            message.group(1)
        )
    return None


def _analyze_image(mht: QQMhtFile, name: str, block_content: str):
    image_data = base64.b64decode(block_content.replace("\n", ""))
    mht.chat_record.add_enclosure(name, image_data)
    return None


def analyze_mht_file(file_path: str) -> QQMhtFile:
    if not os.path.exists(file_path):
        raise FileNotFoundError("指定的聊天记录文件不存在")
    mht_object = QQMhtFile()
    file_name = os.path.splitext(os.path.split(file_path)[1])[0]
    file_name = re.match("(.*?)\((\d+)\)", file_name)
    if file_name:
        mht_object.chat_record.id = file_name.group(2)
    with open(file_path, "r", encoding="UTF-8") as File:
        header_buffer = ""
        while True:
            data = File.readline()
            if data == "\n":
                break
            header_buffer = header_buffer + data
        _file_header(mht_object, header_buffer)
        File.readline()
        data_block_buffer = File.read().split(mht_object.split + "\n")
    for block in data_block_buffer:
        block_info = _analyze_block_header(block)
        if block_info["Content-Type"] == "text/html":
            _analyze_html(mht_object, block.split("\n\n")[1])
        elif block_info["Content-Type"][:5] == "image":
            _analyze_image(mht_object, block_info["Content-Location"], block.split("\n\n")[1])
        else:
            raise Exception
    return mht_object
