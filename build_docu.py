# -*- coding: utf-8 -*-
import markdown2
import re
import os
import json

# the Files to build
files = []
# the links Html
linksHtml = ""
# build path
build_path = ""
#settings
settings = ""


def getCSS():
    css_filename = 'markdown.css'
    return open(css_filename, 'r').read().decode('utf-8')


def postprocessor(html, filename):
    # fix relative paths in images/scripts
    def tag_fix(match):
        tag, src = match.groups()
        if not src.startswith(('file://', 'https://', 'http://', '/')):
            abs_path = u'file://%s/%s' % (os.path.dirname(filename), src)
            tag = tag.replace(src, abs_path)
        return tag
    RE_SOURCES = re.compile("""(?P<tag><(?:img|script)[^>]+src=["'](?P<src>[^"']+)[^>]*>)""")
    html = RE_SOURCES.sub(tag_fix, html)
    return html


def getFiles():
    links = ""
    global linksHtml
    for dirname, dirnames, filenames in os.walk(build_path):
        for filename in filenames:
            if filename[-3:] == ".md":
                files.append(open(os.path.join(dirname, filename), 'r'))
                links += '+ [%s](%s)\n' % (filename, filename[:-3] + ".html")
    linksHtml = markdown2.markdown(links, extras=['footnotes', 'toc'])


def convertmd(f):
    md = f.read()
    # convert the markdown
    markdown_html = markdown2.markdown(md, extras=['footnotes', 'toc'])
    # postprocess the html
    return postprocessor(markdown_html, os.path.basename(f.name))


def generateHtml(html):
    html_contents = u'<!DOCTYPE html>'
    html_contents += '<html><head><meta charset="utf-8">'
    styles = getCSS()
    html_contents += '<style>%s</style>' % styles
    html_contents += u'</head><body><div id="jump_to">         Jump To …         <div id="jump_wrapper"><div id="jump_page">'
    html_contents += linksHtml
    html_contents += '</div></div></div>'
    html_contents += html
    html_contents += '</body>'
    return html_contents.encode('utf-8')


def convertFiles():
    for f in files:
        html = generateHtml(convertmd(f))
        htmlFile = open(f.name[:-2] + 'html', 'w')
        htmlFile.write(html)
        htmlFile.close()
        f.close()


def buildIndex():
    index = open(build_path + "/index.html", "w")
    index.write(generateHtml('<h1>' + settings['project_name'] + '</h1>' + linksHtml))
    index.close()


if __name__ == "__main__":
    settingFile = open("settings.json", 'r')
    settings = json.loads(settingFile.read())
    settingFile.close()
    build_path = settings['build_path']
    getFiles()
    convertFiles()
    buildIndex()
