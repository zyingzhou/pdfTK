#! /usr/bin/env python
# coding:utf-8
"""
Author: zhiying 
关注志颖博客(www.zhouzying.cn)
Date: 20-2-6 下午9:06
Description: Regular Expression Engine for pdf parse

"""
import re
from encoding import hex_decode
# from encoding import mk_hex_string


# match object attribute

def match_attr(text):

    # object number

    attrs = []

    obj_num_re = re.compile(r'(\d+) 0 obj.*endobj', re.DOTALL)  # match start and end at anywhere
    if obj_num_re.search(text) is not None:
        result = obj_num_re.search(text)
        obj_num = result.group(1)
        tup = ('obj_num', obj_num)
        attrs.append(tup)

    attrs_pattern = (r'/(Type)[\s]?/([a-zA-Z0-9]+)[\s]?',    # Type
                     r'/(Title) <([a-zA-Z0-9]+)>\n',    # Title
                     r'/([a-zA-Z]+) (\d+)',    # Count
                     r'/([a-zA-Z]+) (\d+) 0 R',    # Pages Outlines, Root, Info, and so on
                     r'/(Dest) \[(\d+) 0 R .*\]'   # Dest

                     )
    # attribute iter
    for attr_pattern in attrs_pattern:
        regex = re.compile(attr_pattern)
        if len(regex.findall(text)) != 0:
            result = regex.findall(text)
            attrs = attrs + result

    # Kids

    kids_re = re.compile(r'/Kids[\s]?\[(.*)\]')
    if kids_re.search(text) is not None:
        result = kids_re.search(text)
        ls = result.group(1)
        kids = re.compile(r'(\d+) 0 R').findall(ls)
        if len(kids) != 0:
            tup = ('Kids', kids)
            attrs.append(tup)
    items = dict(attrs)
    if "Title" in items.keys():

        items['Title'] = hex_decode(items['Title'])

    return items
