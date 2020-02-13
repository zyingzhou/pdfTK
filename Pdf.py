#! /usr/bin/env python
# coding:utf-8
"""
Author: zhiying (www.zhouzying.cn)
Date: 20-1-26 下午5:08
Description: pdf parser and Tool Kit.

"""
import re
from regex import match_attr
# import codecs


class Pdf:
    """manipulate pdf document"""
    def __init__(self, path):
        """
        initialize a pdf document
        :param path: pdf file path
        """
        self.path = path
        self.version = self._get_version()
        self.debug = self._read()
        self.doc = "%PDF1-7\n"

    def _read(self):
        """read a pdf document"""
        with open(self.path, 'rt', errors='ignore') as pf:
            return pf.read()

    def _get_version(self):
        """
        read PDF version
        :return: PDF version, return 'No version number' if errors happen
        """
        v_regex = re.compile(r'^%PDF-(1\.\d+)')
        if v_regex.search(self._read()) is not None:
            result = v_regex.search(self._read())
            return result.group(1)
        else:
            return 'No version number'

    def _get_xref(self):
        """
        get xref
        :return: raw xref string
        """
        content = self._read()
        xref_regex = re.compile(r'xref.*?startxref', re.DOTALL)
        xref = xref_regex.findall(content)
        if len(xref) > 0:
            return xref[0]    # else return None

    def _byte_offset(self):
        """
        Byte_offset_of_last_cross-reference
        :return: byte_offset
        """
        offset_re = re.compile(r'startxref\n(\d+)\n%%EOF')
        if offset_re.search(self._read()) is not None:
            result = offset_re.search(self._read())
            byte_offset = result.group(1)
            return byte_offset
        else:
            return ''

    def get_trailer(self):
        """
        Trailer
        :return: (dict) trailer dictionary, else return None
        """
        xref = self._get_xref()
        items = {}
        if xref is not None:
            trailer_regex = re.compile(r'trailer\s?<<(.*)>>\s?startxref', re.DOTALL)
            if trailer_regex.search(xref) is not None:
                result = trailer_regex.search(xref)
                trailer_text = result.group(1).replace('\n', '').strip()

                # Size

                regex1 = re.compile(r'/([a-zA-Z]*) (\d+)')
                if regex1.search(trailer_text) is not None:
                    result = regex1.search(trailer_text)
                    items[result.group(1)] = result.group(2)

                # Root info Encrypt

                regex2 = re.compile(r'/([a-zA-Z]*) (\d+) 0 R')
                if len(regex2.findall(trailer_text)) != 0:
                    result = regex2.findall(trailer_text)
                    for tup in result:
                        items[tup[0]] = tup[1]

                # ID

                regex3 = re.compile(r'/ID [(.*)]')
                if regex3.search(trailer_text) is not None:
                    result = regex3.search(trailer_text)
                    items['ID'] = result.group()

                return items

    # raw objects

    def get_objs(self):
        """
        get all objects
        :return: objects
        """
        obj_regex = re.compile(r'\d+ 0 obj.*?endobj', re.DOTALL)
        objs = obj_regex.findall(self._read())
        if len(objs) > 0:
            return objs

    def get_attrs(self):
        """
        show all object attribute
        :return: obj_items: (list)
        """
        pdf_obj_list = []
        objs = self.get_objs()
        if objs is not None:
            for obj in objs:
                attrs = match_attr(obj)
                if 'obj_num' in attrs.keys():
                    tup = (attrs['obj_num'], attrs)

                    pdf_obj_list.append(tup)

        return pdf_obj_list

    def get_entry(self):
        """
        get entry object number (Root)
        :return: entry and object attributes dict
        """
        entry = None
        trailer = self.get_trailer()

        # obj_list: (tuple) ('obj_num', attrs)

        obj_list = self.get_attrs()
        if trailer is not None and 'Root' in trailer.keys():
            entry = trailer['Root']

        else:

            if len(obj_list) != 0:
                for obj in obj_list:

                    if 'Root' in obj[-1].keys():
                        entry = obj[-1]['Root']

        return entry, dict(obj_list)

    # TODO: show catalog

    def get_catalog(self):
        """
        get pdf document catalog(outlines)
        :return: (list) [[hierarchy,title,page-number],,...]
        """
        entry, objs_dict = self.get_entry()

        catalog = []
        if entry is not None:
            catalog_dict = objs_dict[entry]

            page_order = {}

            # page tree
            if 'Pages' in catalog_dict.keys():
                pages_no = catalog_dict['Pages']
                pages_dict = objs_dict[pages_no]
                if 'Kids' in pages_dict.keys():
                    pages_kids = pages_dict['Kids']
                    n = 1
                    for kid in pages_kids:
                        page_order[kid] = n
                        n += 1

            else:
                raise ValueError('No Pages attribute')

            # outlines
            if 'Outlines' in catalog_dict.keys():
                outlines_no = catalog_dict['Outlines']
                outlines_dict = objs_dict[outlines_no]
                if 'First' and 'Last' in outlines_dict.keys():
                    first = eval(outlines_dict['First'])
                    last = eval(outlines_dict['Last'])
                    for i in range(first, last + 1):
                        outline = []
                        outline_item = objs_dict[str(i)]

                        if 'Parent' in outline_item.keys():
                            parent = (outline_item['Parent'])
                            hierarchy = 2
                            if parent == outlines_no:
                                hierarchy = 1
                            outline.append(hierarchy)

                        if 'Title' in outline_item.keys():
                            title = outline_item['Title']
                            outline.append(title)

                        if 'Dest' in outline_item.keys():
                            dest = outline_item['Dest']
                            page_number = page_order[dest]
                            outline.append(page_number)

                        catalog.append(outline)

                    return catalog

            else:
                raise ValueError('No Outlines attribute')

        else:
            raise ValueError('No Catalog attribute')

    # TODO: import catalog



