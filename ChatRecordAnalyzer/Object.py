#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Object.py
# @Time      :2022/3/19 14:04
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
import os
import pickle
from typing import Union, List, Dict
from collections import defaultdict, OrderedDict

import jieba

_stopwords_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stopwords.txt")
with open(_stopwords_file_path, "r", encoding="UTF-8") as File:
	STOPWORDS = File.read().split("\n")


def _word_filter(word: str) -> bool:
	if len(word) <= 1:
		return False
	if word in STOPWORDS:
		return False
	return True


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
		self.message_dict_time: Dict[str, Message] = {}
		self.message_dict_people: Dict[str, List[Message]] = defaultdict(list)
	
	def __str__(self):
		return f"<MessageList number={len(self.message_list)} people={'、'.join(self.all_sender)}>"
	
	def __repr__(self):
		return str(self)
	
	@classmethod
	def sort_message(cls, message_list: List[Message]):
		return sorted(message_list, key=lambda x: x.message_time)
	
	def append_message(self, message: Message) -> bool:
		self.message_list.append(message)
		self.message_dict_time[str(message.message_time)] = message
		self.message_dict_people[message.sender].append(message)
		return True
	
	def format(self):
		return pickle.dumps(self)
	
	def merge(self, people_name_list: List[str], new_name: str):
		for people in people_name_list:
			if people not in self.all_sender:
				raise ValueError("指定的人名不存在。")
		new_message_list = [self.message_dict_people[people_name] for people_name in people_name_list]
		message_list = []
		for people_message in new_message_list:
			for one_message in people_message:
				one_message.sender = new_name
				message_list.append(one_message)
		for people in people_name_list:
			del self.message_dict_people[people]
		self.message_dict_people[new_name] = self.sort_message(message_list)
		return True
	
	def delete(self, people_name_list: List[str]):
		for people in people_name_list:
			if people not in self.all_sender:
				raise ValueError("指定的人名不存在。")
		for people in people_name_list:
			del self.message_dict_people[people]
		buffer = []
		for index, one_message in enumerate(self.message_list):
			if one_message.sender in people_name_list:
				buffer.append(index)
		for index in buffer: self.message_list.pop(index)
		buffer = []
		for key, one_message in self.message_dict_time.items():
			if one_message.sender in people_name_list:
				buffer.append(key)
		for key in buffer: del self.message_dict_time[key]
		return True
		
	@property
	def errors(self):
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
		return error_dict
	
	@property
	def all_sender_word_frequency(self):
		word_dict = defaultdict(int)
		for one_message in self.message_list:
			for one_content in one_message.content:
				if one_content.content_type == Content.ContentType.TYPE_TEXT:
					for one_word in jieba.cut(one_content.data):
						if _word_filter(one_word):
							word_dict[one_word] += 1
		word_list = sorted(word_dict.items(), key=lambda d: d[1], reverse=True)
		word_dict = OrderedDict()
		for word in word_list:
			word_dict[word[0]] = word[1]
		return word_dict
	
	@property
	def single_sender_word_frequency(self):
		people_dict = {}
		for people_name, message_list in self.message_dict_people.items():
			word_dict = defaultdict(int)
			for one_message in message_list:
				for one_content in one_message.content:
					if one_content.content_type == Content.ContentType.TYPE_TEXT:
						for one_word in jieba.cut(one_content.data):
							if _word_filter(one_word):
								word_dict[one_word] += 1
			word_list = sorted(word_dict.items(), key=lambda d: d[1], reverse=True)
			word_dict = OrderedDict()
			for word in word_list:
				word_dict[word[0]] = word[1]
			people_dict[people_name] = word_dict
		return people_dict
	
	@property
	def all_sender(self):
		return [i for i in self.message_dict_people.keys()]
	
	def self_check(self):
		return {
			"BasicInfo": {
				"PeopleName": self.all_sender,
				"WordFrequency": {
					"AllSender": self.all_sender_word_frequency,
					"SingleSender": self.single_sender_word_frequency
				}
			},
			"Error": self.errors
		}
