#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Main.py
# @Time      :2021/6/8 20:32
# @Author    :Amundsen Severus Rubeus Bjaaland


from ChatRecordAnalyzer import MhtFile, TxtFile


File1 = MhtFile("E:\YHL\Code\QQChatRecordAnalyzer\Data\疏儿(1369439362).mht")
MessageList1 = File1.get_message_list()
Error1 = MessageList1.self_check()
File2 = TxtFile("E:\YHL\Code\QQChatRecordAnalyzer\Data\疏儿(1369439362).txt")
MessageList2 = File2.get_message_list()
Error2 = MessageList2.self_check()
a = 0