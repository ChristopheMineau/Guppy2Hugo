#! /usr/bin/python
import glob
import html2text # pip install html2text
from pathlib import Path
import re
import os
import shutil

DATA_PATH = "C:/Users/Papou/Documents/www/Hugo/LBN2Hugo/data"
FILE_PATH = "C:/Users/Papou/Documents/www/Hugo/LBN2Hugo/file"
SOURCE_PATH = "C:/Users/Papou/Documents/www/Hugo/LBN2Hugo/"
IMG_PATH = "C:/Users/Papou/Documents/www/Hugo/Sites/LaBelleNote/static/img"
CONTENT_PATH = "C:/Users/Papou/Documents/www/Hugo/LBN2Hugo/content"

def cleanHtml(html):
    m = re.search('(<!\-*\d+\-*>)?(.*)', html)
    resu = m.group(2)
    resu = resu.strip()
    resu = resu.replace('"','')
    return resu

def cleanPathElement(html):
    resu = cleanHtml(html)
    resu = resu.replace(' ','_')
    resu = resu.replace('"','')
    resu = resu.replace(',','')
    resu = resu.replace('\'','_')
    resu = resu.replace('?','')
    resu = resu.replace('!','')
    resu = resu.replace(':','_')
    resu = resu.replace('<','_')
    resu = resu.replace('>','_')
    resu = resu.replace('=','_')
    resu = resu.replace('é','e')
    resu = resu.replace('è','e')
    resu = resu.replace('ê','e')
    resu = resu.replace('à','a')
    resu = resu.replace('â','a')
    resu = resu.replace('ô','o')
    resu = resu.replace('ü','u')
    resu = resu.replace('ï','i')
    resu = resu.replace('î','i')
    return resu

def title2Folder(title):
    def camel_case(s):
        s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return ''.join(s)
    resu = cleanPathElement(title)
    resu = camel_case(resu)
    return resu

class IncFile:
    class Field:
        def __init__(self, name, line):
            self.name = name
            self.txt = self.stripslashes(line)
        def addLine(self, line):
            self.txt += '\n' + self.stripslashes(line)
        def stripslashes(self, l):
            return l.replace('\\','')

    def __init__(self, n):
        self.path = Path(DATA_PATH) / "dbdocs/docs" / f"{n:08}.inc"
        with open(self.path,  encoding="utf8") as f:
            self.lines = f.readlines()
        self.fields = dict()
        self.createDate = ''
        self.modDate = ''
        self.getFields()
    
    def getFields(self):
        newField = None
        for l in self.lines:
            creadateMatch = re.search(r'^\$creadate = \'(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', l)
            if creadateMatch:
                self.createDate = f"{creadateMatch.group(1)}-{creadateMatch.group(2)}-{creadateMatch.group(3)}T{creadateMatch.group(4)}:{creadateMatch.group(5)}:00+01:00"
                continue

            modeMatch = re.search(r'^\$moddate = \'(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', l)
            if modeMatch:
                self.modDate = f"{modeMatch.group(1)}-{modeMatch.group(2)}-{modeMatch.group(3)}T{modeMatch.group(4)}:{modeMatch.group(5)}:00+01:00"
                continue

            fieldBegin = re.search(r'^\$(field[abcd][12]) = stripslashes\(\'(.*?)(\'\);)?$', l)
            if fieldBegin:
                newField = self.Field(fieldBegin.group(1), fieldBegin.group(2))
                if fieldBegin.group(3):
                    self.fields[newField.name] = newField
                    newField = None
                continue

            if newField is not None:
                fieldEnd = re.search(r'\'\);$', l)
                if fieldEnd:
                    self.fields[newField.name] = newField
                    newField = None
                else:
                    newField.addLine(l)

class GuppyDoc:
    class Resource:
        def __init__(self, path, file):
            self.relPath = path  
            self.sourcePath = Path(SOURCE_PATH) / Path(path[:-5] if 'vgnt' in path else path)
            self.file = file
            assert os.path.isfile(self.sourcePath / self.file) , f'Error: Ressource file does not exist : {self.sourcePath / self.file}'
        
        def moveResource(self, targetResourcePath):
            shutil.copyfile(self.sourcePath / self.file, Path(targetResourcePath) / self.file)

    def __init__(self):
        self.num = 0
        self.mdFr = ""
        self.mdEn = ""
        self.date = ""
        self.titleFr = ""
        self.titleEn = ""
        self.resources = []
        self.featuredImage = ""
        self.tagsFr = []
        self.tagsEn = []
        self.categories = []
        self.targetPath = Path(CONTENT_PATH)
        self.hasYoutube = False
        self.hasLink = False
        self.hasPhotorama = False
        self.hasSlideshow = False
        self.hasAudio = False
    
    def inspectHtml(self, html):
        if 'photorama' in html:
            self.hasPhotorama = True
        if 'audio' in html:
            self.hasAudio = True
        if '<a ' in html:
            self.hasLink = True
        videos = []
        for m in re.finditer('<iframe.*?youtube\.com\/(\w+?\/)+?(\w+).*?iframe>', html):
            self.hasYoutube = True
            videos.append((m.group(0), m.group(2)))
        # keep youtube iframes as text (html2txt would remove them)
        for v in videos:
            html = html.replace(v[0], f" youtube_{v[1]} ")
        if 'data-image' in html:
            self.hasSlideshow = True
        return html

    def insertYoutube(self, md):
        videos = []
        for m in re.finditer('youtube_(\w+)', md):
            videos.append((m.group(0), m.group(1)))
        for v in videos:
            md = md.replace(v[0], f"{{{{< youtube {v[1]} >}}}}")
        return md

              
    def createHugoPageBundle(self):
        os.makedirs(self.targetPath, exist_ok=True)
        with open(self.targetPath / "index.md", encoding='utf-8', mode='w+') as f:
            f.write('+++\n')
            f.write(f'title = "{self.titleFr}"\n')
            f.write(f'description = "{self.titleFr}"\n')
            f.write(f'author = "Christophe Mineau"\n')
            f.write(f'date = {self.date}\n')
            if self.featuredImage:
                f.write(f'featured = "{self.featuredImage}"\n')
            f.write(f'draft = "false"\n')
            f.write(f'categories = {str(self.categories)}\n')
            f.write(f'tags = {str(self.tagsFr)}\n')
            f.write('+++\n')
            f.write(f'{self.mdFr}\n')
        with open(self.targetPath / "index.en.md", encoding='utf-8', mode='w+') as f:
            f.write('+++\n')
            f.write(f'title = "{self.titleEn}"\n')
            f.write(f'description = "{self.titleEn}"\n')
            f.write(f'author = "Christophe Mineau"\n')
            f.write(f'date = {self.date}\n')
            if self.featuredImage:
                f.write(f'featured = "{self.featuredImage}"\n')
            f.write(f'categories = {str(self.categories)}\n')
            f.write(f'tags = {str(self.tagsEn)}\n')
            f.write(f'draft = "false"\n')
            f.write('+++\n')
            f.write(f'{self.mdEn}\n')

    def findPageResources(self):
        for m in re.finditer('\(((\w+\/)*?)([\w\.]+\.(JPG|jpg|Jpg|PNG|png|Png|gif|GIF|Gif))\)', self.mdFr):
            self.resources.append(self.Resource(m.group(1), m.group(3)))
        # identify featured image
        m = re.search('\[FB\]\(((\w+\/)*?)([\w\.]+\.(JPG|jpg|Jpg|PNG|png|Png|gif|GIF|Gif))\)', self.mdFr)
        if m:
            self.featuredImage = m.group(3)
        else:
            if len(self.resources)>0:
               self.featuredImage =  self.resources[0].file
            else:
                self.featuredImage = ""

    def moveResources(self):
        for r in self.resources:
            r.moveResource(self.targetPath)
    
    def useResourcesLocally(self):
        for r in self.resources:
            self.mdFr = self.mdFr.replace(r.relPath, '')
            self.mdEn = self.mdEn.replace(r.relPath, '')

    def findTagsAndCategories(self):
        contentIx = self.targetPath._parts.index('content')
        if len(self.targetPath._parts)>=contentIx+2:
            self.categories.append(self.targetPath._parts[contentIx+1].replace('_',' '))
        if len(self.targetPath._parts)>=contentIx+3:
            self.categories.append(self.targetPath._parts[contentIx+2].replace('_',' '))
        with open(Path(DATA_PATH) / "dbdocs/index/kw.dtb", encoding="utf8") as f:
            docs = [l.split('||') for l in f.readlines()]
        doc = next((d for d in docs if int(d[0])==self.num), [])
        if doc:
            self.tagsFr = [t.strip() for t in doc[3].split(';')]
            self.tagsEn = [t.strip() for t in doc[4].split(';')]


class Article(GuppyDoc):
    def __init__(self, indexLine):
        super().__init__()
        elements = indexLine.split('||')
        self.SubMenuFr = elements[0]
        self.SubMenuEn = elements[1]
        self.titleFr = cleanHtml(elements[2])
        self.titleEn = cleanHtml(elements[3])
        self.num = int(elements[4])
        self.menu = elements[5]
        self.menuLevel1Fr = ''
        self.menuLevel1En = ''
        self.menuLevel2Fr = ''
        self.menuLevel2En = ''
        self.menuLevel3Fr = ''
        self.menuLevel3En = ''
        self.incFile = IncFile(self.num)
        self.date = self.incFile.createDate
        self.htmlFr = self.incFile.fields["fieldc1"].txt
        self.htmlFr = self.inspectHtml(self.htmlFr)
        self.htmlEn = self.incFile.fields["fieldc2"].txt
        self.htmlEn = self.inspectHtml(self.htmlEn)
        self.mdFr = html2text.html2text(self.htmlFr)
        self.mdEn = html2text.html2text(self.htmlEn)
        self.mdFr = self.insertYoutube(self.mdFr)
        self.mdEn = self.insertYoutube(self.mdEn)
        self.findPageResources()
        self.getMenuTree()
        self.useResourcesLocally()
        self.findTagsAndCategories()
        self.createHugoPageBundle()
        self.moveResources()

    def getMenuTree(self):
        with open(Path(DATA_PATH) / "dbdocs/index/arom.dtb", encoding="utf8") as f:
            menus  = [l.split('||') for l in f.readlines()]
        for menu in menus:
            if int(menu[0])==self.num:
                self.menuLevel1Fr = menu[3]
                self.menuLevel1En = menu[4]
                menul2l3 = menu[5].split('|')
                self.menuLevel2Fr = menul2l3[0]
                self.menuLevel3Fr =  menul2l3[1] if len(menul2l3)>1 else ''
                menul2l3 = menu[6].split('|')
                self.menuLevel2En = menul2l3[0]
                self.menuLevel3En =  menul2l3[1] if len(menul2l3)>1 else ''
                self.targetPath /= cleanPathElement(self.menuLevel1Fr)
                self.targetPath /= cleanPathElement(self.menuLevel2Fr)
                if self.menuLevel3Fr:
                    self.targetPath /= cleanPathElement(self.menuLevel3Fr)
                self.targetPath /= title2Folder(self.titleFr)
                return
        # articles with no menu
        self.targetPath /= "orphan_articles"

    def __str__(self):
        s = f"{self.num};{self.titleFr};{self.targetPath};{len(self.resources)};"
        s += f"{'youtube'if self.hasYoutube else '       '};"
        s += f"{'links'if self.hasLink else '     '};"
        s += f"{'photorama'if self.hasPhotorama else '        '};"
        s += f"{'slideshow'if self.hasSlideshow else '         '};"
        s += f"{'audio'if self.hasAudio else '     '};"
        return(s)

class News(GuppyDoc):
    def __init__(self, indexLine):
        super().__init__()
        elements = indexLine.split('||')
        self.titleFr = cleanHtml(elements[2])
        self.titleEn = cleanHtml(elements[3])
        self.num = int(elements[4])
        self.incFile = IncFile(self.num)
        self.date = self.incFile.modDate
        self.htmlFr = self.incFile.fields["fieldc1"].txt
        self.htmlFr = self.inspectHtml(self.htmlFr)
        self.htmlEn = self.incFile.fields["fieldc2"].txt
        self.htmlEn = self.inspectHtml(self.htmlEn)
        self.mdFr = html2text.html2text(self.htmlFr)
        self.mdEn = html2text.html2text(self.htmlEn)
        self.mdFr = self.insertYoutube(self.mdFr)
        self.mdEn = self.insertYoutube(self.mdEn)
        self.findPageResources()
        self.targetPath /= 'blog'
        self.targetPath /= title2Folder(self.titleFr)
        self.useResourcesLocally()
        self.createHugoPageBundle()
        self.moveResources()

    def __str__(self):
        s = f"{self.num};{self.titleFr};{self.targetPath};{len(self.resources)};"
        s += f"{'youtube'if self.hasYoutube else '       '};"
        s += f"{'links'if self.hasLink else '     '};"
        s += f"{'photorama'if self.hasPhotorama else '        '};"
        s += f"{'slideshow'if self.hasSlideshow else '         '};"
        s += f"{'audio'if self.hasAudio else '     '};"
        return(s)


#
# navigate through the index folder
with open(Path(DATA_PATH) / "dbdocs/index/ar.dtb", encoding="utf8") as f:
    articles = [Article(l) for l in f.readlines()]

with open(Path(DATA_PATH) / "dbdocs/index/ne.dtb", encoding="utf8") as f:
    news = [News(l) for l in f.readlines()]

print("*** Articles ***")
for a in articles:
    print(a)

print("*** News ***")
for n in news:
    print(n)
