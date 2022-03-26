#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :TxtFile.py
# @Time      :2022/3/19 14:03
# @Author    :Amundsen Severus Rubeus Bjaaland


import os
import re
import time
import copy

from ..Object import MessageList, Message, Content


class TxtFile(object):
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"未找到指定文件({path})。")
        self.path = path
        with open(path, "r", encoding="UTF-8") as File:
            self.__content = File.read()
        self.__message_list = MessageList()
        self.__analyze()
    
    def __analyze(self):
        rows = self.__content.split("\n")[8:-1]
        messages = [rows[i:i + 2] for i in range(0, len(rows), 3)]
        info_string_format = re.compile("(\d{4}-\d\d-\d\d \d{1,2}:\d{1,2}:\d{1,2}) (.*?)##Finish")
        enclosure_string_format = re.compile("[.*?]")
        for one_message in messages:
            message_info = info_string_format.match(one_message[0]+"##Finish")
            message_object = Message(
                time.mktime(time.strptime(f"{message_info.group(1)}", "%Y-%m-%d %H:%M:%S")), message_info.group(2),
                ""
            )
            if not one_message[1]:
                message_object.append_content(Content("EmptyMessage", Content.ContentType.TYPE_ERROR))
            message_content = enclosure_string_format.split(one_message[1])
            buffer = []
            for one_content in message_content:
                buffer.append(Content(one_content, Content.ContentType.TYPE_TEXT))
                buffer.append(Content("PictureMissing", Content.ContentType.TYPE_ERROR))
            buffer = buffer[:1]
            for one_content in buffer:
                message_object.append_content(one_content)
            self.__message_list.append_message(message_object)
        return True
    
    def get_message_list(self):
        return copy.deepcopy(self.__message_list)
