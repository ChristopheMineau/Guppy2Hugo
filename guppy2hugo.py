#! /usr/bin/python
import glob
import html2text # pip install html2text
from pathlib import Path
import re
import os
import shutil

DATA_PATH = Path.cwd() / "../data"
FILE_PATH = Path.cwd() / "../file"
PHOTO_PATH = Path.cwd() / "../photo"
SOURCE_PATH = Path.cwd() / "../"
CONTENT_PATH = Path.cwd() / "../content"
HTACCESS_PATH = Path.cwd() / "../htAccess.txt"

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
    resu = resu.replace('.','')
    resu = resu.replace('\'','_')
    resu = resu.replace('°','_')
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
    resu = resu.replace('ò','o')
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

def fixLinks(docList, linkDict):
    def replaceLink(md, linkDict):
        resu = md
        for m in re.finditer('\(\w+\.php.*?&pg=(\d+).*?\)', md):
            docId = int(m.group(1))
            guppyLink = m.group(0)
            if docId in linkDict:
                resu = resu.replace(guppyLink, f"({linkDict[docId]})")
        return resu

    for d in docList:
        d.mdEn = replaceLink(d.mdEn, linkDict)
        d.mdFr = replaceLink(d.mdFr, linkDict)
        d.createHugoPageBundle()
            
                    


def getDocUris(docList):
    linkDict = dict()
    for d in docList:
        linkDict[d.num] = '/' + str(d.relPath).replace('\\','/').lower()
    return linkDict

class Comment:
    def __init__(self, incNum):
        self.incFile = IncFile(incNum)
        self.incNum = incNum
        self.num = int(self.incFile.fields["fielda1"].txt)
        self.date = self.incFile.createDate
        self.author = self.incFile.author
        self.email = self.incFile.email
        self.html = self.incFile.fields["fieldc1"].txt
        self.md = html2text.html2text(self.html).strip()
        self.mailNonDisclosure = self.incFile.fields["fieldd1"].txt

    def getMd(self):
        md = f'{{{{< comment date="{self.date}" author="{self.author}" email="{self.email}" mailNonDisclosure="{self.mailNonDisclosure}" >}}}}\n'
        md += f'{self.md}\n'
        md += f'{{{{< /comment >}}}}\n\n'
        return md

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

            authorMatch = re.search(r'^\$author = stripslashes\(\'(.*?)\'\);$', l)
            if authorMatch:
                self.author = authorMatch.group(1)
                continue

            mailMatch = re.search(r'^\$email = stripslashes\(\'(.*?)\'\);$', l)
            if mailMatch:
                self.email = mailMatch.group(1)
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
        self.relPath = Path()
        self.hasYoutube = False
        self.hasLink = False
        self.hasPhotorama = False
        self.hasSlideshow = False
        self.hasAudio = False
        self.oldUri = ""
        self.newUri = ""
    
    def inspectHtml(self, html):
        if 'photorama' in html:
            self.hasPhotorama = True
        if '<a ' in html:
            self.hasLink = True
        videos = []
        for m in re.finditer('<iframe.*?youtube\.com\/(\w+?\/)+?([\w_\-]+).*?iframe>', html):
            self.hasYoutube = True
            videos.append((m.group(0), m.group(2)))
        # keep youtube iframes as text (html2txt would remove them)
        for v in videos:
            html = html.replace(v[0], f" youtube_{v[1]} ")
        if 'data-image' in html:
            self.hasSlideshow = True
        audios = []
        for m in re.finditer('<audio(.|\n)*?src=\\\"((.|\n)*?)\\\"(.|\n)*?\/audio>|\n]', html, re.MULTILINE):
            self.hasAudio = True
            path = os.path.dirname(m.group(2)) + '/'
            file = os.path.basename(m.group(2))
            self.resources.append(GuppyDoc.Resource(path, file))
            audios.append((m.group(0), file))
        for a in audios:
            html = html.replace(a[0], f" audio_{a[1]} ")
        return html

    def insertYoutube(self, md):
        videos = []
        for m in re.finditer('youtube_([\w_\-]+)', md):
            videos.append((m.group(0), m.group(1)))
        for v in videos:
            md = md.replace(v[0], f"{{{{< youtube {v[1]} >}}}}")
        return md

    def insertAudio(self, md):
        audios = []
        for m in re.finditer('audio_([\w_\-]+\.mp3)', md):
            audios.append((m.group(0), m.group(1)))
        for a in audios:
            md = md.replace(a[0], f"{{{{< audio mp3=\"{a[1]}\" >}}}}")
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
            self.featuredImage = next((r.file for r in self.resources if re.search('\.(JPG|jpg|Jpg|PNG|png|Png|gif|GIF|Gif)', r.file)), '')


    def moveResources(self):
        for r in self.resources:
            r.moveResource(self.targetPath)
    
    def useResourcesLocally(self):
        for r in self.resources:
            self.mdFr = self.mdFr.replace(r.relPath, '')
            self.mdEn = self.mdEn.replace(r.relPath, '')

    def findTagsAndCategories(self):
        if len(self.relPath._parts)>=1:
            self.categories.append(self.relPath._parts[0].replace('_',' '))
        if len(self.relPath._parts)>=2:
            self.categories.append(self.relPath._parts[1].replace('_',' '))
        with open(Path(DATA_PATH) / "dbdocs/index/kw.dtb", encoding="utf8") as f:
            docs = [l.split('||') for l in f.readlines()]
        doc = next((d for d in docs if int(d[0])==self.num), [])
        if doc:
            self.tagsFr = [t.strip() for t in doc[3].split(';')]
            self.tagsEn = [t.strip() for t in doc[4].split(';')]

    def setUris(self):
        self.oldUri = f"pg={self.num}"
        self.newUri = str(self.relPath).lower().replace('\\','/')

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
        self.mdFr = self.insertAudio(self.mdFr)
        self.mdEn = self.insertAudio(self.mdEn)
        self.findPageResources()
        self.getMenuTree()
        self.targetPath /= self.relPath
        self.useResourcesLocally()
        self.findTagsAndCategories()
        self.lookForComments()
        self.createHugoPageBundle()
        self.moveResources()
        self.setUris()

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
                self.relPath /= cleanPathElement(self.menuLevel1Fr)
                self.relPath /= cleanPathElement(self.menuLevel2Fr)
                if self.menuLevel3Fr:
                    self.relPath /= cleanPathElement(self.menuLevel3Fr)
                self.relPath /= title2Folder(self.titleFr)
                return
        # articles with no menu
        self.menuLevel1Fr = "index"
        self.relPath /= cleanPathElement(self.menuLevel1Fr)
        self.relPath /= title2Folder(self.titleFr)

    def lookForComments(self):
        with open(Path(DATA_PATH) / "dbdocs/index/ra.dtb", encoding="utf8") as f:
            index = [l.split('||') for l in f.readlines()]
        self.comments = [Comment(int(idx[0])) for idx in index if int(idx[1])==self.num] 
        self.comments.sort(key=lambda x: x.num)
        self.hasComments = len(self.comments) > 0
        self.mdFr += '\n{{< guppy-comment-block >}}\n'
        self.mdEn += '\n{{< guppy-comment-block >}}\n'
        for c in self.comments:
            self.mdFr += c.getMd()
            self.mdEn += c.getMd()
        self.mdFr += '{{< /guppy-comment-block >}}\n'
        self.mdEn += '{{< /guppy-comment-block >}}\n'

    def getHtaccess(self):
        h =  f'RewriteCond %{{QUERY_STRING}} "lng=fr.*&{self.oldUri}(&|$)"\n'
        h += f'RewriteRule ^articles.php /{self.newUri}? [QSD,R=301,L]\n'
        h += f'RewriteCond %{{QUERY_STRING}} "lng=en.*&{self.oldUri}(&|$)"\n'
        h += f'RewriteRule ^articles.php /en/{self.newUri}? [QSD,R=301,L]\n'
        return h

    def __str__(self):
        s = f"{self.num};{self.titleFr};{self.relPath};{len(self.resources)};"
        s += f"{'youtube'if self.hasYoutube else '       '};"
        s += f"{'links'if self.hasLink else '     '};"
        s += f"{'photorama'if self.hasPhotorama else '        '};"
        s += f"{'slideshow'if self.hasSlideshow else '         '};"
        s += f"{'audio'if self.hasAudio else '     '};"
        s += f"{'comments'if self.hasComments else '        '};"
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
        self.relPath /= 'blog'
        self.relPath /= title2Folder(self.titleFr)
        self.targetPath /= self.relPath
        self.useResourcesLocally()
        self.createHugoPageBundle()
        self.moveResources()

    def __str__(self):
        s = f"{self.num};{self.titleFr};{self.relPath};{len(self.resources)};"
        s += f"{'youtube'if self.hasYoutube else '       '};"
        s += f"{'links'if self.hasLink else '     '};"
        s += f"{'photorama'if self.hasPhotorama else '        '};"
        s += f"{'slideshow'if self.hasSlideshow else '         '};"
        s += f"{'audio'if self.hasAudio else '     '};"
        return(s)


class Download(GuppyDoc):
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
        self.dlFr =  self.incFile.fields["fieldd1"].txt
        self.dlEn =  self.incFile.fields["fieldd2"].txt
        file = self.addDownloadRessources(self.dlFr)
        self.mdFr += f'\n{{{{% download file="{file}" lang="fr" %}}}}\n'
        file = self.addDownloadRessources(self.dlEn)
        self.mdEn += f'\n{{{{% download file="{file}" lang="en" %}}}}\n'
        self.relPath /= 'downloads'
        self.relPath /= title2Folder(self.titleFr)
        self.targetPath /= self.relPath
        self.useResourcesLocally()
        self.addCategories()
        self.createHugoPageBundle()
        self.moveResources()

    def addDownloadRessources(self, f):
        fpath = f.split('||')[0]
        file = os.path.basename(fpath)
        path = os.path.dirname(fpath)
        self.resources.append(GuppyDoc.Resource(path, file))
        return file

    def addCategories(self):
        self.categories.append("Download")
        self.categories.append(self.incFile.fields["fielda1"].txt)
        self.categories.append(self.incFile.fields["fielda2"].txt)

    def __str__(self):
        s = f"{self.num};{self.titleFr};{self.relPath};{len(self.resources)};"
        s += f"{'youtube'if self.hasYoutube else '       '};"
        s += f"{'links'if self.hasLink else '     '};"
        s += f"{'photorama'if self.hasPhotorama else '        '};"
        s += f"{'slideshow'if self.hasSlideshow else '         '};"
        s += f"{'audio'if self.hasAudio else '     '};"
        return(s)


class Galery:
    class Photo:
        def __init__(self, dtbLine):
            elements = dtbLine.split('||')
            self.num = elements[0]
            self.file = elements[2]
        #    self.w = int(elements[7])
        #    self.h = int(elements[8])
            self.captionFr = elements[5].replace('"', '').strip()
            self.captionEn = elements[6].replace('"', '').strip()
        def getMd(self, lang):
            md = f'{{{{< figure link="{self.file}"\n'
            md += f'    caption="{self.captionFr if lang=="fr" else self.captionEn}" >}}}}\n'
            return md
        def moveResource(self, sourcePath, targetResourcePath):
            shutil.copyfile(sourcePath / self.file, targetResourcePath / self.file)

    def __init__(self, indexLine):
        elements = indexLine.split('||')
        self.categoryFr = cleanHtml(elements[0])
        self.categoryEn = cleanHtml(elements[1])
        self.titleFr = cleanHtml(elements[2])
        self.titleEn = cleanHtml(elements[3])
        self.num = int(elements[4])
        creadateMatch = re.search(r'(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', elements[5])
        if creadateMatch:
            self.date = f"{creadateMatch.group(1)}-{creadateMatch.group(2)}-{creadateMatch.group(3)}T{creadateMatch.group(4)}:{creadateMatch.group(5)}:00+01:00"
        self.sourcePath = Path(PHOTO_PATH) / f'gal_{self.num}'
        self.relPath = Path("galleries") / f"gal_{self.num:03}"
        self.targetPath = Path(CONTENT_PATH) / self.relPath
        assert os.path.isdir(self.sourcePath), f"The Galery folder does not exist : {self.sourcePath}"
        with open(self.sourcePath / f'gal_{self.num}.dtb', encoding="utf8") as f:
            self.photos = [Galery.Photo(l) for l in f.readlines()]
        if len(self.photos) >0:
            self.featuredImage = self.photos[0].file
        self.createHugoPageBundle()
        self.moveResources()

    def createHugoPageBundle(self):
        os.makedirs(self.targetPath, exist_ok=True)
        with open(self.targetPath / "index.md", encoding='utf-8', mode='w+') as f:
            f.write('+++\n')
            f.write(f'title = "{self.titleFr}"\n')
            f.write(f'description = "Galerie {self.titleFr}"\n')
            f.write(f'author = "Christophe Mineau"\n')
            f.write(f'date = {self.date}\n')
            if self.featuredImage:
                f.write(f'featured = "{self.featuredImage}"\n')
            f.write(f'draft = "false"\n')
            f.write(f'categories = [ "Gallerie"]\n')
            f.write(f'tags = ["{self.categoryFr}"]\n')
            f.write('+++\n')
            f.write(f'# Galerie {self.titleFr}\n')
            f.write(f'<p>Bienvenue dans la galerie {self.titleFr}.</p>\n') # include explicitely the <p></p> for Hugo to limit the summary to the prist found paragraph

            f.write('{{< detailed-gallery >}}\n')
            for p in self.photos:
                f.write(p.getMd('fr'))
            f.write('{{< /detailed-gallery >}}\n')
            f.write('\n\n****\nAll contents under Creative Commons BY-NC-SA license.\n')
        with open(self.targetPath / "index.en.md", encoding='utf-8', mode='w+') as f:
            f.write('+++\n')
            f.write(f'title = "{self.titleEn}"\n')
            f.write(f'description = "Galerie {self.titleEn}"\n')
            f.write(f'author = "Christophe Mineau"\n')
            f.write(f'date = {self.date}\n')
            if self.featuredImage:
                f.write(f'featured = "{self.featuredImage}"\n')
            f.write(f'draft = "false"\n')
            f.write(f'categories = ["Galery"]\n')
            f.write(f'tags = ["{self.categoryEn}"]\n')
            f.write('+++\n')
            f.write(f'# Galery {self.titleEn}\n')
            f.write(f'<p>Welcome to the galery {self.titleEn}.</p>\n')
            f.write('{{< detailed-gallery >}}\n')
            for p in self.photos:
                f.write(p.getMd('en'))
            f.write('{{< /detailed-gallery >}}\n')
            f.write('\n\n****\nAll contents under Creative Commons BY-NC-SA license.\n')

    def moveResources(self):
        for p in self.photos:
            p.moveResource(self.sourcePath, self.targetPath)

    def __str__(self):
        s = f"{self.num};{self.titleFr};{self.relPath};{len(self.photos)};"
        s += ";"*5
        return(s)

class Guestbook:
    def __init__(self):
        with open(Path(DATA_PATH) / "dbdocs/docid.dtb", encoding="utf8") as f:
            docs =  [l.split('||') for l in f.readlines()] 
        self.comments = [Comment(int(d[1])) for d in docs if d[0]=='gb']

    def getMd(self):
        md = '{{< guppy-comment-block >}}\n'
        for c in self.comments:
            md += c.getMd()
        md += '{{< /guppy-comment-block >}}\n\n'
        return md


################# main ###################

if __name__ == "__main__":

# navigate through the index folder
    with open(Path(DATA_PATH) / "dbdocs/index/ar.dtb", encoding="utf8") as f:
        articles = [Article(l) for l in f.readlines()]

    with open(Path(DATA_PATH) / "dbdocs/index/ne.dtb", encoding="utf8") as f:
        news = [News(l) for l in f.readlines()]

    with open(Path(DATA_PATH) / "dbdocs/index/dn.dtb", encoding="utf8") as f:
        downloads = [Download(l) for l in f.readlines()] 

    with open(Path(DATA_PATH) / "dbdocs/index/ph.dtb", encoding="utf8") as f:
        galeries = [Galery(l) for l in f.readlines()]

    # Set the correct links, relative to the site
    uriDict = getDocUris(articles + news + downloads + galeries)
    fixLinks(articles + news + downloads, uriDict)

    guesbook = Guestbook()

    print("*** Articles ***")
    for a in articles:
        print(a)

    print("*** News ***")
    for n in news:
        print(n)

    print("*** Downloads ***")
    for d in downloads:
        print(d)

    print("*** Galeries ***")
    for g in galeries:
        print(g)

    print("*** Guestbook ***")
    print(guesbook.getMd())

    # generate .htaccess rewrite rules
    with open(HTACCESS_PATH, "w") as h:
        h.write("# These are rewrite rules to redirect legacy Guppy urls to new Hugo ones\n")
        h.write("RewriteEngine on\n")
        for a in articles:
            h.write(a.getHtaccess()) 
    print(f"*** .htaccess inputs written to {HTACCESS_PATH} ***")
