# serialise/deserialise the .bbmap files which are the uncompressed versions of the archive.bin.cmp files found in level folders

import struct
import io

from lxml import etree

from bbmap import main

class BBCompiler():
    def __init__(self, file_in, file_out):
        self.file_in = file_in
        self.file_out = file_out

        self.main_struct = main()

        self.root = etree.Element("Map")

        self.file = open(self.file_in, 'rb')
        self.BD = io.BufferedReader(self.file)
        self.xml_recurse(self.main_struct, self.root)
        #print(etree.tostring(self.root, pretty_print = True))
        et = etree.ElementTree(self.root)
        et.write('data.xml', xml_declaration='<?xml version="1.0" encoding="utf-8"?>', pretty_print=True, encoding='utf-8')
        #self.recurse_print(self.main_struct)
        #dsd = self.main_struct.deserialise()
        #print(dsd)
        self.file.close()

    def xml_recurse(self, obj, node):
        # obj is the object we want to recurse over, and node is the current node in the xml etree was want to subelement things to
        for key in obj.data:
            fmt = obj.data[key]
            try:
                l = struct.calcsize(fmt)
                # if the code hasn't broken by this point then the data is just a format for the struct class
                sub_element = etree.SubElement(node, key, value = str(struct.unpack(fmt, self.BD.read(l))[0]))
            except:
                sub_element = etree.SubElement(node, key)
                self.xml_recurse(fmt, sub_element)

    def recurse_print(self, obj):
        for key in obj.data:
            fmt = obj.data[key]
            try:
                l = struct.calcsize(fmt)
                # if the code hasn't broken by this point then the data is just a format for the struct class
                print("{0}: {1}".format(key, struct.unpack(fmt, self.BD.read(l))[0]))        # need the [0] as this will always return a tuple
            except:
                self.recurse_print(fmt)
                """
                l = len(fmt)
                for subkey in fmt.data:
                    sublen = struct.calcsize(fmt.data[subkey])
                    print("{0}: {1}".format(subkey, struct.unpack(fmt.data[subkey], BD.read(sublen))[0]))        # need the [0] as this will always return a tuple
                """
            

a = BBCompiler('1-1.bbmap', None)

            
