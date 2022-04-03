#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Main.py
# @Time      :2021/6/8 20:32
# @Author    :Amundsen Severus Rubeus Bjaaland


import wordcloud

from ChatRecordAnalyzer import MhtFile, TxtFile


File1 = MhtFile("E:\YHL\Code\QQChatRecordAnalyzer\Data\疏儿(1369439362).mht")
File2 = MhtFile("E:\YHL\Code\QQChatRecordAnalyzer\Data\\test.mht")
MessageList1 = File1.get_message_list()
MessageList2 = File2.get_message_list()
MessageList3 = MessageList1 + MessageList2
MessageList3.merge(["Ephemeral", "章可晶(可可)(Cherley)", "章可晶(可可)(Sherley)", "半夏生", "疏儿"], "疏儿")
MessageList3.delete(['系统消息(10000)', ""])
Info1 = MessageList1.self_check()
# File2 = TxtFile("E:\YHL\Code\QQChatRecordAnalyzer\Data\疏儿(1369439362).txt")
# MessageList2 = File2.get_message_list()
# MessageList2.merge(["Ephemeral", "章可晶(可可)(Cherley)", "章可晶(可可)(Sherley)", "半夏生", "疏儿"], "疏儿")
# MessageList2.delete(['系统消息(10000)', ""])
# Info2 = MessageList2.self_check()
word_cloud_1 = wordcloud.WordCloud(
	max_words=100,
	width=2000,
	height=1200,
	font_path="C:\\Windows\\Fonts\\STXINGKA.TTF",
	stopwords={"撤回", "一条", "消息"}
)
word_cloud_1.generate_from_frequencies(Info1["BasicInfo"]["WordFrequency"]["AllSender"])
word_cloud_1.to_file("outfile.png")
a = 0