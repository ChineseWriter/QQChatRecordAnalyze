#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Object.py
# @Time      :2022/3/19 14:04
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
import pickle
from typing import Union, List


class Content(object):
	class ContentType(object):
		TYPE_TEXT = "Text"
		TYPE_IMAGE = "Image"
		TYPE_SOUND = "Sound"
		TYPE_FILE = "File"
		TYPE_ERROR = "Error"
	
	def __init__(self, data: Union[str, bytes], content_type: str = ContentType.TYPE_TEXT):
		self.data = data
		self.content_type = content_type
	
	def __str__(self):
		if self.content_type == self.ContentType.TYPE_TEXT:
			if len(self.data) > 15:
				return f"<Content text='{self.data[:15]} . . .'>"
			else:
				return f"<Content text='{self.data}'>"
		elif self.content_type == self.ContentType.TYPE_IMAGE:
			return f"<Content image=b'{self.data[:15]} . . .'>"
		elif self.content_type == self.ContentType.TYPE_FILE:
			return f"<Content file=b'{self.data[:15]} . . .'>"
		elif self.content_type == self.ContentType.TYPE_SOUND:
			return f"<Content sound=b'{self.data[:15]} . . .'>"
		elif self.content_type == self.ContentType.TYPE_ERROR:
			return f"<Content error='{self.data}'>"
	
	def __repr__(self):
		return str(self)


class Message(object):
	def __init__(self, message_time: float, sender: str, sender_id: str, **kwargs):
		self.message_time: float = message_time
		self.sender: str = sender
		self.sender_id: str = sender_id
		self.create_time = time.time()
		self.content: List[Content] = []
		for k, v in kwargs.items():
			setattr(self, k, v)
	
	def __str__(self):
		return f"<Message send-time={self.message_time} content={self.content} create-time={self.create_time}>"
	
	def __repr__(self):
		return str(self)
	
	def append_content(self, content: Content) -> bool:
		self.content.append(content)
		return True


class MessageList(object):
	def __init__(self):
		self.message_list: List[Message] = []
	
	def __str__(self):
		return f"<MessageList number={len(self.message_list)}>"
	
	def __repr__(self):
		return str(self)
	
	def append_message(self, message: Message) -> bool:
		self.message_list.append(message)
		return True
	
	def format(self):
		return pickle.dumps(self)
	
	def self_check(self):
		error_dict = {"EmptyMessage": [], "PictureMissing": [], "UnknownTag": []}
		for one_message in self.message_list:
			for one_content in one_message.content:
				if one_content.content_type == Content.ContentType.TYPE_ERROR:
					if one_content.data == "EmptyMessage":
						error_dict["EmptyMessage"].append(one_message)
					elif one_content.data == "PictureMissing":
						error_dict["PictureMissing"].append(one_message)
					elif one_content.data == "UnknownTag":
						error_dict["UnknownTag"].append(one_message)
		basic_info_dict = {"PeopleName": []}
		for one_message in self.message_list:
			if one_message.sender not in basic_info_dict["PeopleName"]:
				basic_info_dict["PeopleName"].append(one_message.sender)
		return {"BasicInfo": basic_info_dict, "Error": error_dict}
