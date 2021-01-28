from dateutil import rrule
from datetime import datetime, timedelta
from collections import namedtuple
from git import Repo
import re
import pytz
import sys
from pprint import pprint
from .page import Page
from .commit import Commit
import time
from reportlab.pdfgen import canvas
from random import shuffle

Range = namedtuple('Range', ['start', 'end'])

class Report:

    def __init__(self, name, committerEmails, gitPaths, startDate, endDate, department,startTrainingYear, newTrainingYear,specialDates, commitsPerBranch, font, pathNamingList):
        self.name = name
        self.committerEmails = committerEmails
        self.gitPaths = gitPaths
        self.startDate = startDate
        self.endDate = endDate
        self.department = department
        self.startTrainingYear = startTrainingYear
        self.newTrainingYear = datetime.strptime(newTrainingYear, '%d-%m-%Y')
        self.specialDates = specialDates
        self.commitsPerBranch = commitsPerBranch
        self.font = font
        self.pathNamingList = pathNamingList

    def checkStartDate(self, date):
        while(date.weekday() != 0):
            date = date + timedelta(days=1)
        return date

    def checkTrainingYear(self, date):
        if(date < self.newTrainingYear):
            if(date + timedelta(days=7) < self.newTrainingYear):
                return [self.startTrainingYear,self.startTrainingYear]
            else:
                return [self.startTrainingYear,self.startTrainingYear + 1]
        elif(date < datetime(self.newTrainingYear.year + 1,self.newTrainingYear.month, self.newTrainingYear.day)):
            if(date + timedelta(days=7) < datetime(self.newTrainingYear.year + 1,self.newTrainingYear.month, self.newTrainingYear.day)):
                return [self.startTrainingYear + 1,self.startTrainingYear + 1]
            else:
                return [self.startTrainingYear + 1,self.startTrainingYear + 2]
        else:
            return [self.startTrainingYear + 2, self.startTrainingYear + 2]

    def createPages(self, startObject, endObject):
        nr = 1
        interval = 2
        fileCanvas = canvas.Canvas("pdfs/" + self.startDate + "-" + self.endDate + ".pdf")
        for dt in rrule.rrule(rrule.WEEKLY, interval=interval, dtstart=startObject, until=endObject):
            print("creating week Nr: " + str(nr) + "-" + str(nr+1))
            trainingYear = self.checkTrainingYear(dt)
            firstBigBox = self.getCommitsByDate(dt)
            secondBigBox = self.getCommitsByDate(dt + timedelta(days=7))
            firstSmallBox = self.getTrainingsByDate(dt)
            secondSmallBox = self.getTrainingsByDate(dt + timedelta(days=7))         
            page = Page(self.name, nr, trainingYear, self.department, dt, firstBigBox, secondBigBox, firstSmallBox, secondSmallBox, self.font, fileCanvas)
            page.create()
            nr += 2
        fileCanvas.save()

    def getAllCommits(self):
        fullList = []
        for gitPath in self.gitPaths:
            print("checking out git repository:" + gitPath)
            repo = Repo(gitPath)
            print("start searching commits by: " + self.committerEmails[0] + " in all Branches")
            for index, branch in enumerate(repo.remotes.origin.refs):
                self.print_progress(index + 1, len(repo.remotes.origin.refs),"",branch.name)
                commits = list
                commits = list(repo.iter_commits(branch.name, max_count=self.commitsPerBranch)) #, max_count=59
                #print(" found " + str(len(commits)) + " commits")     
                for commit in commits:
                    try:
                        if(commit.committer):
                            if(commit.committer.email in self.committerEmails):
                                if(not "Merge" in commit.summary):
                                    result = Commit(commit.committed_datetime,commit.summary)
                                    path = self.checkPathForName(gitPath)                                    
                                    result.path = path
                                    fullList.append(result)
                    except ValueError:
                        pass
        return fullList

    def checkPathForName(self,path):
        for key, value in self.pathNamingList.items():
            if key in path:
                return value
        return "Plantex"

    def getCommitsByDate(self, date):
        commitsList = {}
        utc=pytz.UTC
        awareDate = utc.localize(date)
        for commit in self.commits:
            if(awareDate <= commit.date <= (awareDate + timedelta(days=4,hours=23))):
                if(len(commit.summary) >= 10):
                    if (not commit.path in commitsList):
                        commitsList[commit.path] = []
                    if (not commit.summary in commitsList[commit.path]):
                        commitsList[commit.path].append(commit.summary)
        for key, value in commitsList.items():
            commitsList[key] = self.sortCommitsByLength(value)
        specialList = []
        
        specialList = self.checkForSpecial('school',specialList, date)
        specialList = self.checkForSpecial('holidays',specialList, date)
        if (specialList != []):
            commitsList['special'] = specialList
        return commitsList

    def getTrainingsByDate(self, date):
        trainings = {}
        specialList = []
        specialList = self.checkForSpecial('trainings', specialList, date)
        if(specialList):
            trainings['special'] = specialList
        return trainings

    def checkForSpecial(self,type, commitsList, date):
        data = self.specialDates[type]
        for item in data['dates']:
            startHoli = datetime.strptime(item['start'],'%d.%m.%Y')
            endHoli = datetime.strptime(item['end'],'%d.%m.%Y')
            if(self.checkForDateOverlap(startHoli,endHoli,date,date + timedelta(days=4))):
                commitsList = []      
                commitsList.append(data['name'])    
                if('content' in item):
                    commitsList.append(item['content']) 
                    
        return commitsList

    def sortCommitsByLength(self, commits):
        if(commits):
            commits.sort(key = lambda s: (1/len(s)))
        shortList = commits[:10]
        shuffle(shortList)
        return shortList

    def checkForDateOverlap(self,firstStart,firstEnd,secondStart,secondEnd):
        r1 = Range(start=firstStart, end=firstEnd)
        r2 = Range(start=secondStart, end=secondEnd)
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)
        if(overlap > 0): 
            return True
        else:
            return False
            
    def print_progress(self, iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
        str_format = "{0:." + str(decimals) + "f}"
        percents = str_format.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        sys.stdout.write("\033[F") # Cursor up one line
        sys.stdout.write("\033[K") #clear line
        sys.stdout.write("%s |%s| %s%s %s" % (prefix, bar, percents, '%', suffix[0:30]))
        sys.stdout.flush()
        print()

    def create(self):
        startObject = datetime.strptime(self.startDate, '%d-%m-%Y')
        endObject = datetime.strptime(self.endDate, '%d-%m-%Y')
        startObject = self.checkStartDate(startObject)
        self.commits = self.getAllCommits()
        print("start creating pages")
        self.createPages(startObject, endObject)
        print("finished all pages")
