import xml.etree.ElementTree
from xml.sax.saxutils import escape
import common_lib

parser, st, stop = common_lib.Init()

f = open("output_small.xml", "wb")
f.write("<data>\n")
e = xml.etree.ElementTree.parse('small_sample.xml').getroot()
i = 1
for ves in e.findall('vespaadd'):
    for doc in ves.findall('document'):
        f.write("<doc number = \"" + str(i) + "\">\n")
        i += 1
        f.write("<subject>" + escape(doc.find('subject').text) + "</subject>\n")
        f.write("<content>" + escape(doc.find('content').text) + "</content>\n")
        #f.write("<category>" + escape(subject) + "</category>\n")
        f.write("<keywords>" + escape(common_lib.buildFullQuery(doc.find('subject').text, doc.find('content').text, parser, stop)) + "</keywords>\n")
        f.write("</doc>\n")
f.write("</data>\n")
f.close()

#print buildFullQuery("long-distance trail throughout CA", parser)
