#! /usr/bin/env python
# coding:utf-8
"""
Author: zhiying
关注志颖博客(www.zhouzying.cn)
Date: 20-2-6 下午9:44
Description: Encoding and Decoding for hex string

"""
from binascii import hexlify
from binascii import unhexlify


def hex_decode(s):
    """
    hex string decode
    :param s: (str) hex string
    :return: string: (str) human-readable strings
    """
    if type(s) is not str:
        raise ValueError('s should be str')
    else:
        # unhexlify(s2).decode('utf-16-be')
        strings = unhexlify(s.encode('utf-8')).decode('utf-16-be')
        # remove \ufeff
        return strings.replace('\ufeff', '').strip()


def mk_hex_string(s):
    """
    make hex string
    :param s: (str) string
    :return: hex_string: (str) hex string
    """

    if type(s) is not str:
        raise ValueError('s shoule be str')
    else:
        s = '\ufeff' + s
        hex_string = hexlify(s.encode('utf-16-be')).decode('utf-8')
        return hex_string
