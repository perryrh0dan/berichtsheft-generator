import re
from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate,PageTemplate,Frame,Paragraph)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import (black,purple,white,yellow)
from dateutil import rrule
from datetime import datetime, timedelta

class Page:

    def __init__(self,name, nr, trainingYear, department, startDate, firstBigBox, secondBigBox, firstSmallBox, secondSmallBox, font, fileCanvas):
        self.left = 60
        self.right = 535
        self.name = name
        self.nr = nr
        self.trainingYear = trainingYear
        self.department = department
        self.startDate = startDate
        self.firstBigBox = firstBigBox
        self.secondBigBox = secondBigBox
        self.firstSmallBox = firstSmallBox
        self.secondSmallBox = secondSmallBox
        self.font = font
        self.fontBold = font + "-Bold"
        self.fileCanvas = fileCanvas
        
        self.styleParagraph = ParagraphStyle(
                'default',
                fontName=self.font,
                fontSize=10,
                leading=12,
                leftIndent=10,
                rightIndent=0,
                firstLineIndent=0,
                alignment=TA_LEFT,
                spaceBefore=0,
                spaceAfter=0,
                bulletFontName=self.font,
                bulletFontSize=10,
                bulletIndent=0,
                bulletText="-",
                textColor= black,
                backColor=white,
                wordWrap=None,
                borderWidth= 0,
                borderPadding= 0,
                borderColor= None,
                borderRadius= None,
                allowWidows= 1,
                allowOrphans= 0,
                textTransform=None,  # 'uppercase' | 'lowercase' | None
                endDots=None,         
                splitLongWords=1,
            )
        self.styleTitle = ParagraphStyle(
                'title',
                fontName=self.font,
                fontSize=10,
                leading=12,
            )
    
    def create(self):
        self.canvas = self.fileCanvas
        self.canvas.setLineWidth(.3)
        self.canvas.setFont(self.font, 12)
        self.createHeader(800,740,'first')
        self.createTextPanel(730,540,"Betriebliche Tätigkeit","big",self.firstBigBox)
        self.createTextPanel(530,450,"Unterweisungen, Schulungen","small",self.firstSmallBox)
        self.createHeader(440,390,'second')     
        self.createTextPanel(380,190,"Betriebliche Tätigkeit","big",self.secondBigBox)
        self.createTextPanel(180,100,"Unterweisungen, Schulungen","small",self.secondSmallBox) 
        self.createFooter(90,40)
        self.canvas.showPage()

    def createHeader(self, top, bottom, type):
        self.canvas.line(self.left,top,self.right,top)
        self.canvas.line(self.left,top,self.left,bottom)
        self.canvas.line(self.right,top,self.right,bottom)
        self.canvas.line(self.left,bottom,self.right,bottom)
        self.canvas.setFont(self.fontBold, 12)
        lineOne = top - 12
        if(type == 'first'):
            lineTwo = top - 24
            lineThree = top - 45
            self.canvas.drawString(62,lineOne,"Name, Vorname:")
            self.canvas.drawString(62,lineTwo,"Ausbildungsnachweis")
            self.canvas.setFont(self.font, 10)
            self.canvas.drawString(200,lineOne,self.name)
            self.canvas.drawString(200,lineTwo,"Nr." + str(self.nr))
            self.canvas.drawString(250,lineTwo,"für die Woche vom " + self.startDate.strftime("%d.%m.%Y"))
            self.canvas.drawString(468,lineTwo,"bis " + (self.startDate+timedelta(days=4)).strftime("%d.%m.%Y"))
            self.canvas.drawString(62,lineThree, "Abteilung oder Arbeitsgebiet: " + self.department)
            self.canvas.drawString(350,lineThree, "Ausbildungsjahr: " + str(self.trainingYear[0]))
        elif(type == 'second'):
            lineTwo = top - 33
            self.canvas.drawString(62,lineOne,"Ausbildungsnachweis")
            self.canvas.setFont(self.font, 10)
            self.canvas.drawString(200,lineOne,"Nr." + str(self.nr + 1))
            self.canvas.drawString(250,lineOne,"für die Woche vom " + (self.startDate+timedelta(days=7)).strftime("%d.%m.%Y"))
            self.canvas.drawString(468,lineOne,"bis " + (self.startDate+timedelta(days=11)).strftime("%d.%m.%Y"))
            self.canvas.drawString(62,lineTwo, "Abteilung oder Arbeitsgebiet: " + self.department)
            self.canvas.drawString(350,lineTwo, "Ausbildungsjahr: " + str(self.trainingYear[1]))
            
    def createTextPanel(self, top, bottom, title, type, content):
        self.canvas.line(self.left,top,self.right,top) #topline
        self.canvas.line(self.left,top,self.left,bottom) #leftline
        self.canvas.line(self.right,top,self.right,bottom) #rightline
        self.canvas.line(self.left,bottom,self.right,bottom) #bottomline
        self.canvas.line(self.left,bottom,self.right,bottom) #bottomline
        self.canvas.line(self.left,top-13,self.right,top-13) #title
        self.canvas.drawString(self.left + 2,top - 10,title)
        mainFrame = Frame(self.left,bottom,self.right - self.left,top-bottom - 12,2,6,2,6)
        textBlock = []
        r = re.compile(r'#[0-9]+')
        if ('special' in content):
            newLine = r.sub(r'',content['special'][0]).lstrip(' ')
            if(len(content['special']) > 1):
                newLine = newLine + ':'
                textBlock.append(Paragraph(newLine, self.styleTitle))
                for con in content['special'][1:]:
                    newLine = r.sub(r'',con).lstrip(' ')
                    textBlock.append(Paragraph(newLine, self.styleParagraph))
            else:
               textBlock.append(Paragraph(newLine, self.styleParagraph)) 

        elif (len(content) > 0):
            for key, value in content.items():
                newLine = "Projekt " + r.sub(r'',key).lstrip(' ') + ":"
                textBlock.append(Paragraph(newLine, self.styleTitle))
                for commit in value:
                    newLine = r.sub(r'',commit).lstrip(' ')
                    textBlock.append(Paragraph(newLine, self.styleParagraph))
        mainFrame.addFromList(textBlock,self.canvas)         

    def createFooter(self, top, bottom):
        self.canvas.line(self.left,top,self.right,top)
        self.canvas.line(self.left,top,self.left,bottom)
        self.canvas.line(self.right,top,self.right,bottom)
        self.canvas.line(self.left,bottom,self.right,bottom)
        self.canvas.line((self.right + self.left)/2,top,(self.right + self.left)/2,bottom)
        self.canvas.line(self.left,bottom + 13,self.right,bottom + 13)
        self.canvas.drawString(self.left + 2, top - 15,(self.startDate+timedelta(days=11)).strftime("%d.%m.%Y"))
        self.canvas.drawString((self.left + self.right)/2 + 2, top - 15,(self.startDate+timedelta(days=11)).strftime("%d.%m.%Y"))
        self.canvas.drawString(self.left + 2, bottom + 3,"Unterschrift Auszubildender:")        
        self.canvas.drawString((self.left + self.right)/2 + 2, bottom + 3,"Unterschrift Ausbilder:")
