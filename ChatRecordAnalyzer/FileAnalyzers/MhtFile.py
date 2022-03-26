#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :MhtFile.py
# @Time      :2022/3/19 14:03
# @Author    :Amundsen Severus Rubeus Bjaaland


import copy
import os
import base64
import json
import re
import time

from bs4 import BeautifulSoup as bs

from ..Object import Content, Message, MessageList


class MhtInfo(object):
	def __init__(self):
		self.file_creator = ""
		self.subject = ""
		self.version = ""
		self.content_type = ""
		self.charset = ""
		self.file_type = ""
		self.boundary = ""


class MhtFile(object):
	def __init__(self, path: str):
		if not os.path.exists(path):
			raise FileNotFoundError(f"未找到指定文件({path})。")
		self.path = path
		with open(path, "r", encoding="UTF-8-SIG") as File:
			self.__content = File.read()
		self.__info = MhtInfo()
		self.__message_list = MessageList()
		self.__analyze()
	
	def __analyze(self):
		_file_header(self.__content, self)
		_file_html(self.__content, _file_enclosure(self.__content, self), self)
		return None
	
	@property
	def info(self):
		return self.__info
	
	@property
	def message_list(self):
		return self.__message_list
	
	def get_message_list(self):
		return copy.deepcopy(self.__message_list)


def _file_header(mht_data: str, mht_object: MhtFile) -> bool:
	header = mht_data.split("\n\n")[0]
	header = header.replace("\t", "")
	header = header.replace("=", ":")
	header = header.replace(": ", ":")
	header = header.replace(";", "")
	header = header.replace("\n", ",")
	header = header.replace("\"", "")
	header = header.replace(":", "\":\"")
	header = header.replace(",", "\",\"")
	header = header.replace("-\":\"_", "---=_")
	header = "{\"" + header + "\"}"
	try:
		header = json.loads(header)
	except json.decoder.JSONDecodeError:
		return False
	mht_object.info.file_creator = header["From"]
	mht_object.info.subject = header["Subject"]
	mht_object.info.version = header["MIME-Version"]
	mht_object.info.content_type = header["Content-Type"]
	mht_object.info.charset = header["charset"]
	mht_object.info.file_type = header["type"]
	mht_object.info.boundary = header["boundary"]
	return True


def _file_enclosure(mht_data: str, mht_object: MhtFile) -> dict:
	enclosure = mht_data.split(mht_object.info.boundary)[2:]
	if len(enclosure) == 1:
		return {}
	enclosure = enclosure[:-1]
	buffer = {}
	for one_enclosure in enclosure:
		data = one_enclosure.split("\n\n")
		one_enclosure_header = data[0].lstrip("\n")
		one_enclosure_body = data[1].replace("\n", "")
		one_enclosure_header = json.loads(
			"{\"" + one_enclosure_header.replace(":", "\":\"").replace("\n", "\",\"") + "\"}"
		)
		buffer[one_enclosure_header["Content-Location"]] = base64.b64decode(one_enclosure_body)
	return buffer


def _file_html(mht_data: str, enclosure: dict, mht_object: MhtFile) -> bool:
	html = bs(mht_data.split(mht_object.info.boundary)[1], "lxml")
	message_list = html.find("table").find_all("td")[4:]
	date = [""]
	date_string_format = re.compile("日期: (.*?)##Finish")
	time_string_format = re.compile("(.*?)(\d{1,2}:\d{1,2}:\d{1,2})")
	for data in message_list:
		content = data.text
		if date_string_format.match(content+"##Finish"):
			date[0] = date_string_format.match(content+"##Finish").group(1)
			continue
		data = [i for i in data.children]
		send_info = time_string_format.match(data[0].text)
		message_object = Message(
			time.mktime(time.strptime(f"{date[0]} {send_info.group(2)}", "%Y-%m-%d %H:%M:%S")), send_info.group(1), ""
		)
		message_body = data[1]
		children_tag = list(message_body.children)
		if not children_tag:
			message_object.append_content(Content("EmptyMessage", Content.ContentType.TYPE_ERROR))
		for message_tag in children_tag:
			if message_tag.name == "font":
				message_object.append_content(Content(message_tag.text))
			elif message_tag.name == "img":
				if message_tag["src"] in enclosure:
					message_object.append_content(Content(enclosure[message_tag["src"]], Content.ContentType.TYPE_IMAGE))
				else:
					message_object.append_content(Content("PictureMissing", Content.ContentType.TYPE_ERROR))
			else:
				message_object.append_content(Content("UnknownTag", Content.ContentType.TYPE_ERROR))
		mht_object.message_list.append_message(message_object)
	return True
