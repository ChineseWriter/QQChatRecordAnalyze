#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Options.py
# @Time      :2021/6/8 20:32
# @Author    :Amundsen Severus Rubeus Bjaaland


import sys
import time
import jieba
import wordcloud

with open("./stopwords.txt", "r", encoding="UTF-8") as File:
    STOPWORDS = File.read().split("\n")

STOPWORDS.append("图片")
STOPWORDS.append("表情")

SelectedFiles = sys.argv[1:]
for OneFile in SelectedFiles:
    with open(OneFile, "r", encoding="UTF-8") as File:
        Contents = File.readlines()[8:]
    LastHead = None
    Messages = []
    for OneLine in Contents:
        if OneLine == "\n":
            continue
        OneLine = OneLine.rstrip("\n")
        Head = OneLine.split(" ")
        if len(Head) == 3:
            LastHead = Head
        else:
            Time = time.strptime(LastHead[0] + "-" + LastHead[1], "%Y-%m-%d-%H:%M:%S")
            Sender = LastHead[2]
            Message = OneLine.rstrip("\n")
            Messages.append({
                "Time": Time,
                "Sender": Sender,
                "Message": Message
            })
    WordList = {}
    for Message in Messages:
        Words = jieba.cut(Message.get("Message"))
        for OneWord in Words:
            if OneWord in STOPWORDS:
                continue
            if OneWord in WordList:
                WordList[OneWord] += 1
            else:
                WordList[OneWord] = 0
    SortedDict = sorted(WordList.items(), key=lambda x: x[1], reverse=True)
    Counter_1 = 30
    Counter_2 = 0
    BufferList = []
    for i in SortedDict:
        BufferList.append(i[0])
        Counter_2 += 1
        if Counter_2 == Counter_1:
            break
    w = wordcloud.WordCloud(font_path='msyh.ttc', width=1000, height=700, background_color='white')
    Text = " ".join(BufferList)
    w.generate(Text)
    w.to_file('Welove.png')
    input("hhh")



