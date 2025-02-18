"""
Generate a sitemap.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

with open('CNAME') as fid:
    cname = fid.read().strip()
    base_url = f"https://{cname}"

base_path = "version/stable"

def create_sitemap_element(url):
    url_elem = ET.Element("url")
    loc_elem = ET.SubElement(url_elem, "loc")
    loc_elem.text = url
    return url_elem

sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            url = os.path.join(base_url, file_path)
            sitemap_element = create_sitemap_element(url)
            sitemap.append(sitemap_element)

tree = ET.ElementTree(sitemap)

# Pretty-print the XML content
pretty_xml = parseString(ET.tostring(tree.getroot(), encoding="utf-8")).toprettyxml(indent="  ")

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(pretty_xml)
