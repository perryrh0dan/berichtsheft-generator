from src import Report
import json

report = Report(
    #General
    name = "Pöhlmann, Thomas",
    committerEmails = ["thomas.poehlmann@spcon.local","thomaspoehlmann@spcon.de","thomas.poehlmann@spcon.de"],
    #gitPaths = ["C:\Dev\outagecomm"],
    gitPaths = ["C:/Dev/plantex","C:\Dev\outagecomm"],
    startDate = "01-03-2017",
    endDate = "01-06-2018",
    department = "Anwendungsentwicklung",
    startTrainingYear = 1,
    newTrainingYear = "01-09-2017",
    specialDates = json.load(open('additionalFiles/specialDates.json')),
    pathNamingList = {"vacationmanagement":"Urlaubsverwaltung","projectmanagement":"Projektverwaltung","outagecomm":"OutageComm"},

    #Special
    font = "Helvetica",
    commitsPerBranch = 500
) 

Report.create(report)