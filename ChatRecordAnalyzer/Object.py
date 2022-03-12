#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Object.py
# @Time      :2022/2/10 12:44
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
from typing import List


class Message(object):
    TYPE_TEXT = "Text"
    TYPE_IMAGE = "Image"
    TYPE_SOUND = "Sound"
    TYPE_FILE = "File"

    def __init__(self, **kwargs):
        self.__message_time = time.time()
        self.__content = ""
        self.__content_type = ""
        self.__person_name = ""
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def message_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.__message_time))

    @property
    def real_time(self):
        return self.__message_time

    @message_time.setter
    def message_time(self, time_info):
        if isinstance(time_info, str):
            self.__message_time = time.mktime(time.strptime(time_info, "%Y-%m-%d %H:%M:%S"))
        if isinstance(time_info, float):
            self.__message_time = time_info

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, message_content: str):
        self.__content = message_content

    @property
    def content_type(self):
        return self.__content_type

    @content_type.setter
    def content_type(self, message_content_type: str):
        self.__content_type = message_content_type

    @property
    def person_name(self):
        return self.__person_name

    @person_name.setter
    def person_name(self, message_person_name: str):
        self.__person_name = message_person_name

    def __str__(self):
        return f"<Message content={self.content}>"

    def __repr__(self):
        return f"<Message content={self.content}>"


class Enclosure(object):
    def __init__(self, **kwargs):
        self.name = ""
        self.content = b""
        for k, v in kwargs.items():
            setattr(self, k, v)


class ChatRecord(object):
    def __init__(self):
        self.__name = "未知"
        self.__group = "未知"
        self.__id = ""
        self.__message_list: List[Message] = []
        self.__enclosure_dict = {}

    def __str__(self):
        return f"<ChatRecord name={self.__name} group={self.__group} number={self.chat_number}>"

    def __repr__(self):
        return f"<ChatRecord name={self.__name} group={self.__group} number={self.chat_number}>"

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, person_id):
        self.__id = person_id

    @property
    def chat_number(self):
        return len(self.__message_list)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, string: str):
        self.__name = string

    @property
    def group(self):
        return self.__group

    @group.setter
    def group(self, string: str):
        self.__group = string

    @property
    def message_list(self):
        return self.__message_list

    def append_message(self, content, content_type, message_time, date, person_name):
        message = Message()
        message_real_time = time.mktime(time.strptime(f"{date} {message_time}", "%Y-%m-%d %H:%M:%S"))
        for i in self.__message_list:
            if i.real_time == message_real_time:
                if i.person_name == person_name:
                    break
        else:
            message.message_time = message_real_time
            message.content = content
            message.content_type = content_type
            message.person_name = person_name
            self.__message_list.append(message)

    def add_enclosure(self, name, content):
        self.__enclosure_dict[name] = Enclosure(name=name, content=content)
