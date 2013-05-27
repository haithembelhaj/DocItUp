# -*- coding: utf-8 -*-
import markdown2
import re
import os
import json
import subprocess
import time

# the Files to build
files = []
# the links Html
linksHtml = ""
# build path
build_path = ""
# src path
src_path = "src"
#settings
settings = ""
#files to ignore


def getCSS():
    css_filename = 'styles.css'
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


def convertmd(f):
    md = f.read()
    # convert the markdown
    markdown_html = markdown2.markdown(md, extras=['footnotes', 'toc','wiki-tables'])    
    # postprocess the html
    return postprocessor(markdown_html, os.path.basename(f.name))


def generateHtml(html, links=""):
    html_contents = u'<!DOCTYPE html>'
    html_contents += '<html><head><meta charset="utf-8">'
    styles = getCSS()
    html_contents += '<style>%s</style>' % styles
    html_contents += '<link rel="stylesheet" href="http://yandex.st/highlightjs/7.2/styles/solarized_light.min.css">'
    html_contents += '<script src="http://yandex.st/highlightjs/7.2/highlight.min.js"></script>'
    html_contents += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"></script>'
    html_contents += '<script>'
    html_contents += '$(document).ready(function(){$("pre code").each(function(i, e) {hljs.highlightBlock(e)});});'
    html_contents += '</script>'
    html_contents += u'</head><body><div id="container" class="clearfix"><div id="navigation"><h1>Navigation</h1>'
    html_contents += markdown2.markdown(links, extras=['footnotes', 'toc'])
    html_contents += '</div><div id="content">'
    html_contents += html
    html_contents += '</div></div>'
    html_contents += '<div id="footer"><p class="build"> Erstellt am: '+ time.strftime("%d %b %y %H:%M", time.gmtime()) + ' mit <a href="https://github.com/haithembelhaj/DocItUp"> DocItup</a></p></div>' 
    html_contents += '</body>'
    return html_contents.encode('utf-8')


def convertFile(f, links):
    html = generateHtml(convertmd(f), links)
    # print(f.path)
    htmlFile = open(build_path + "/" + os.path.basename(f.name)[:-2] + 'html', 'w')
    htmlFile.write(html)
    htmlFile.close()
    f.close()


def buildIndex(dirname, links):
    index = open(dirname + "/index.html", "w")
    index_src = open(src_path + "/index.md", "r")
    index_html = generateHtml(convertmd(index_src), markdown2.markdown(links, extras=['footnotes', 'toc']))    
    if dirname == build_path:
        title = settings['project_name'] + " Documentation"
    else:
        title = os.path.basename(dirname)
    print links
    index.write(index_html)
    index.close()


def convertFiles():
    global linksHtml
    links = ""
    links += '+ [%s](%s)\n' % ("Startseite", "index.html")
    for dirname, dirnames, filenames in os.walk(src_path):
        basenameDir = os.path.basename(dirname)
        
        if basenameDir != "src":
            print dirname
            links += "+ **" + os.path.basename(dirname).title() + '** \n'

        for filename in filenames:
            print filename

            if os.path.basename(filename)[:-3] != "index":

                srcFile = open(dirname+'/'+filename, 'r')
                headline = srcFile.readline().replace('#', '')
                srcFile.close()
                # filename[:-3].title()
                if filename[-3:] == ".md":
                    links += '+ [%s](%s)\n' % (headline, os.path.basename(filename)[:-3] + ".html")

    for dirname, dirnames, filenames in os.walk(src_path):
        for filename in filenames:
            if filename[-3:] == ".md" and os.path.basename(filename)[:-3] != "index":
                print links
                convertFile(open(os.path.join(dirname, filename), 'r'), links)

    buildIndex(build_path, links)


if __name__ == "__main__":
    settingFile = open("settings.json", 'r')
    settings = json.loads(settingFile.read())
    settingFile.close()
    build_path = settings['build_path']
    convertFiles()
    if 'hooks' in settings:
        for hook in settings['hooks']:
            p = subprocess.Popen(hook, shell=True, cwd=os.path.abspath(build_path))
            p.wait()
