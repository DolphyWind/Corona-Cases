import requests
from bs4 import BeautifulSoup, SoupStrainer
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
from io import BytesIO
import platform

worldometers_url = "https://www.worldometers.info"
main_url = "https://www.worldometers.info/coronavirus/"
header_font = QtGui.QFont("Roboto", 24)
cases_font = QtGui.QFont("Siege UI", 16)

def reformat(abc: str):
    newStr = ""
    a = abc[::-1]
    for i in range(len(a)):
        if i % 3 == 0 and i != 0:
            newStr += ','
        newStr += a[i]
    return newStr[::-1]

# The window that shows spesific country's info
class SubWindow(QtWidgets.QWidget):

    def __init__(self, countryName:str, countryurl:str, countryinfo:list):
        super().__init__()

        # Creating and positioning the window
        self.window_size = (600, 600)
        self.setGeometry(100, 100, self.window_size[0], self.window_size[1])
        self.setWindowTitle("Corona Cases of " + countryName)
        self.center()

        # Creating layouts
        self.headerVLayout = QtWidgets.QVBoxLayout()
        self.headerHLayout = QtWidgets.QHBoxLayout()
        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainHLayout = QtWidgets.QHBoxLayout()
        self.casesVLayout = QtWidgets.QVBoxLayout()
        self.casesHLayout = QtWidgets.QHBoxLayout()

        # Initializing some base values
        self.countryname = countryName
        self.countryURL = countryurl
        self.countryInfo = countryinfo

        # Creating header text
        self.header = QtWidgets.QLabel(self.countryname)
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.header.setFont(header_font)

        # This text will show up on buttom to respect www.worldometers.com
        self.providedby = QtWidgets.QLabel("These data provided from " + main_url)
        self.providedby.setAlignment(QtCore.Qt.AlignCenter)

        # Crating the back button
        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.setFont(cases_font)
        self.closeButton.clicked.connect(self.close)

        # Creating the flag image for selected country
        self.flagpixmap = self.requestForImage()
        self.flag = QtWidgets.QLabel()
        self.flag.setPixmap(self.flagpixmap.scaled(160, 160, QtCore.Qt.KeepAspectRatio))
        self.flag.setAlignment(QtCore.Qt.AlignHCenter)

        # Adding a window icon
        icon = QtGui.QIcon()
        icon.addPixmap(self.flagpixmap)
        self.setWindowIcon(icon)


        # Creating texts for showing up corona cases, deaths etc. of selected country
        self.ActiveText = QtWidgets.QLabel("Active Cases")
        self.Active = QtWidgets.QLabel(countryinfo[0] + "\n")
        self.DeathsText = QtWidgets.QLabel("Deaths")
        self.Deaths = QtWidgets.QLabel(countryinfo[1] + "\n")
        self.RecoveredText = QtWidgets.QLabel("Recovered")
        self.Recovered = QtWidgets.QLabel(countryinfo[2] + "\n")
        self.TotalText = QtWidgets.QLabel("Total Cases")
        self.Total = QtWidgets.QLabel(countryinfo[3] + "\n")

        # Setting up fonts
        self.ActiveText.setFont(cases_font)
        self.Active.setFont(cases_font)
        self.DeathsText.setFont(cases_font)
        self.Deaths.setFont(cases_font)
        self.RecoveredText.setFont(cases_font)
        self.Recovered.setFont(cases_font)
        self.TotalText.setFont(cases_font)
        self.Total.setFont(cases_font)

        # Setting up colors
        self.Active.setStyleSheet("color: #AAAAAA")
        self.Deaths.setStyleSheet("color: red")
        self.Recovered.setStyleSheet("color: #8ACA2B")

        # Layouts
        self.headerVLayout.addWidget(self.header)
        self.headerVLayout.addStretch(2)
        self.headerVLayout.addWidget(self.flag)
        self.headerVLayout.addStretch(3)

        self.headerHLayout.addStretch()
        self.headerHLayout.addLayout(self.headerVLayout)
        self.headerHLayout.addStretch()

        self.casesVLayout.addWidget(self.ActiveText)
        self.casesVLayout.addWidget(self.Active)
        self.casesVLayout.addWidget(self.DeathsText)
        self.casesVLayout.addWidget(self.Deaths)
        self.casesVLayout.addWidget(self.RecoveredText)
        self.casesVLayout.addWidget(self.Recovered)
        self.casesVLayout.addWidget(self.TotalText)
        self.casesVLayout.addWidget(self.Total)

        self.casesHLayout.addLayout(self.casesVLayout)
        self.casesHLayout.addStretch()

        self.mainVLayout.addLayout(self.headerHLayout)
        self.mainVLayout.addStretch()
        self.mainVLayout.addLayout(self.casesHLayout)
        self.mainVLayout.addStretch()
        self.mainVLayout.addWidget(self.closeButton)
        self.mainVLayout.addStretch()
        self.mainVLayout.addWidget(self.providedby)

        self.mainHLayout.addStretch()
        self.mainHLayout.addLayout(self.mainVLayout)
        self.mainHLayout.addStretch()

        self.setLayout(self.mainHLayout)

        # Setting up a timer so values will reload themselves on each minute
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.Update)
        self.timer.setInterval(60 * 1000)
        self.timer.start()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def requestForImage(self):
        req = requests.get(main_url + self.countryURL)
        body = req.content
        soup = BeautifulSoup(body, features='lxml')
        imagesrc = soup.find_all("img")[1]['src']
        imreq = requests.get(worldometers_url + imagesrc)
        image = Image.open(BytesIO(imreq.content))
        qim = ImageQt(image)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    def Update(self):
        self.countryInfo = self.country_request()
        self.Active.setText(self.countryInfo[0] + '\n')
        self.Deaths.setText(self.countryInfo[1] + '\n')
        self.Recovered.setText(self.countryInfo[2] + '\n')
        self.Total.setText(self.countryInfo[3] + '\n')

    def country_request(self):
        req = None
        try:
            req = requests.get(main_url + self.countryURL)
        except requests.ConnectionError:
            QtWidgets.QMessageBox.about(self, "Error!", "Please check your internet connection")
            self.close()
            exit(0)
        body = req.content

        soup = BeautifulSoup(body, features="lxml", parse_only=SoupStrainer("span"))
        country_spans = soup.find_all("span")

        total_cases = country_spans[4].text
        total_deaths = country_spans[5].text
        total_recovered = country_spans[6].text
        active_cases = int(total_cases.replace(',', '')) - int(total_recovered.replace(',', '')) - int(total_deaths.replace(',', ''))
        active_cases = reformat(str(active_cases))
        return [active_cases, total_deaths, total_recovered, total_cases]


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        # Creating the window
        self.window_size = (600, 800)
        self.setGeometry(100, 100, self.window_size[0], self.window_size[1])
        self.setWindowTitle("Corona Cases")
        self.setWindowIcon(QtGui.QIcon("corona.png"))
        self.center()

        # Getting the corona values
        self.informations = self.Mainrequest()
        self.datas = self.informations[0]
        self.countries = self.informations[1]

        # Creating the layouts
        self.mainVBox = QtWidgets.QVBoxLayout()
        self.headerHBox = QtWidgets.QHBoxLayout()
        self.headerVBox = QtWidgets.QVBoxLayout()
        self.casesVBox = QtWidgets.QVBoxLayout()
        self.casesHBox = QtWidgets.QHBoxLayout()
        self.viewHBox = QtWidgets.QHBoxLayout()
        self.viewVBox = QtWidgets.QVBoxLayout()
        self.viewHBox_child = QtWidgets.QHBoxLayout()

        # Header Text
        self.header = QtWidgets.QLabel("Corona Cases")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.header.setFont(header_font)

        # Corona virus image
        self.image = QtWidgets.QLabel()
        self.image.setPixmap(QtGui.QPixmap("corona.png"))

        # This text will show up on buttom to respect www.worldometers.com
        self.providedby = QtWidgets.QLabel("These data provided from " + main_url)
        self.providedby.setAlignment(QtCore.Qt.AlignCenter)

        # Creating texts for showing up corona cases, deaths etc.
        self.ActiveText = QtWidgets.QLabel("Active Cases")
        self.Active = QtWidgets.QLabel(self.datas[0] + "\n")
        self.DeathsText = QtWidgets.QLabel("Deaths")
        self.Deaths = QtWidgets.QLabel(self.datas[1] + "\n")
        self.RecoveredText = QtWidgets.QLabel("Recovered")
        self.Recovered = QtWidgets.QLabel(self.datas[2] + "\n")
        self.TotalText = QtWidgets.QLabel("Total Cases")
        self.Total = QtWidgets.QLabel(self.datas[3] + "\n")

        # Setting up the fonts
        self.ActiveText.setFont(cases_font)
        self.Active.setFont(cases_font)
        self.DeathsText.setFont(cases_font)
        self.Deaths.setFont(cases_font)
        self.RecoveredText.setFont(cases_font)
        self.Recovered.setFont(cases_font)
        self.TotalText.setFont(cases_font)
        self.Total.setFont(cases_font)

        # Setting up the colors
        self.Active.setStyleSheet("color: #AAAAAA")
        self.Deaths.setStyleSheet("color: red")
        self.Recovered.setStyleSheet("color: #8ACA2B")

        # Setting up a tooltip for ActiveText so users can see more detailed information
        self.ActiveText.setToolTip("In mild condition: {}\nSerious or Critical: {}".format(self.datas[4], self.datas[5]))

        # Creating the view by country part
        self.ViewByCountryLabel = QtWidgets.QLabel("View by country:")

        # Creating a combobox
        self.selectCountry = QtWidgets.QComboBox()
        # Sorting the country names
        countries_list = list()
        for i in self.countries.keys():
            countries_list.append(i)
        countries_list.sort()
        self.selectCountry.addItems(countries_list)

        # Creating a button to view corona cases of specified country
        self.viewButton = QtWidgets.QPushButton("View")
        self.viewButton.clicked.connect(self.viewByCountry)

        # Setting up the fonts
        self.ViewByCountryLabel.setFont(cases_font)
        self.selectCountry.setFont(cases_font)
        self.viewButton.setFont(cases_font)

        # Layouts
        self.viewHBox_child.addWidget(self.ViewByCountryLabel)
        self.viewHBox_child.addWidget(self.selectCountry)

        self.viewVBox.addLayout(self.viewHBox_child)
        self.viewVBox.addWidget(self.viewButton)

        self.viewHBox.addStretch()
        self.viewHBox.addLayout(self.viewVBox)
        self.viewHBox.addStretch()

        self.casesVBox.addWidget(self.ActiveText)
        self.casesVBox.addWidget(self.Active)
        self.casesVBox.addStretch()
        self.casesVBox.addWidget(self.DeathsText)
        self.casesVBox.addWidget(self.Deaths)
        self.casesVBox.addStretch()
        self.casesVBox.addWidget(self.RecoveredText)
        self.casesVBox.addWidget(self.Recovered)
        self.casesVBox.addStretch()
        self.casesVBox.addWidget(self.TotalText)
        self.casesVBox.addWidget(self.Total)

        self.casesHBox.addLayout(self.casesVBox)
        self.casesHBox.addStretch()

        self.headerVBox.addWidget(self.header)
        self.headerVBox.addWidget(self.image)

        self.headerHBox.addStretch()
        self.headerHBox.addLayout(self.headerVBox)
        self.headerHBox.addStretch()

        self.mainVBox.addLayout(self.headerHBox)
        self.mainVBox.addLayout(self.casesHBox)
        self.mainVBox.addStretch()
        self.mainVBox.addLayout(self.viewHBox)
        self.mainVBox.addStretch()
        self.mainVBox.addWidget(self.providedby)

        self.mainHBox = QtWidgets.QHBoxLayout()
        self.mainHBox.addStretch()
        self.mainHBox.addLayout(self.mainVBox)
        self.mainHBox.addStretch()

        # Setting up a timer so values will update themselves on each minute
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.Update)
        self.timer.setInterval(60 * 1000)
        self.timer.start()

        self.setLayout(self.mainHBox)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def Mainrequest(self):
        req = None
        try:
            req = requests.get(main_url)
        except requests.ConnectionError:
            QtWidgets.QMessageBox.about(self, "Error!", "Please check your internet connection")
            self.close()
            exit(0)
        body = req.content

        soup = BeautifulSoup(body, features="lxml", parse_only=SoupStrainer('span'))
        spans = soup.find_all("span")

        total_cases = spans[4].text
        total_deaths = spans[5].text
        total_recovered = spans[6].text
        in_mild_condition = spans[8].text
        serious_or_critical = spans[9].text

        Currently_infected = int(in_mild_condition.replace(',', '')) + int(serious_or_critical.replace(',', ''))
        Currently_infected = reformat(str(Currently_infected))

        soup = BeautifulSoup(body, features="lxml", parse_only=SoupStrainer('a'))
        countries = soup.find_all("a", {"class": "mt_a"})
        hrefs_list = soup.find_all("a", {"class": "mt_a"}, href=True)
        hrefs = dict()

        for i in range(len(countries)):
            countries[i] = countries[i].text
            hrefs[countries[i]] = hrefs_list[i]['href']
        data = [Currently_infected, total_deaths, total_recovered, total_cases, in_mild_condition, serious_or_critical]
        return (data, hrefs)

    def country_request(self, country:str):
        req = None
        try:
            req = requests.get(main_url + self.countries[country])
        except requests.ConnectionError:
            QtWidgets.QMessageBox.about(self, "Error!", "Please check your internet connection")
            self.close()
            exit(0)
        body = req.content

        soup = BeautifulSoup(body, features="lxml", parse_only=SoupStrainer("span"))
        country_spans = soup.find_all("span")

        total_cases = country_spans[4].text
        total_deaths = country_spans[5].text
        total_recovered = country_spans[6].text
        active_cases = int(total_cases.replace(',', '')) - int(total_recovered.replace(',', '')) - int(total_deaths.replace(',', ''))
        active_cases = reformat(str(active_cases))

        self.subwindow = SubWindow(country, self.countries[country], [active_cases, total_deaths, total_recovered, total_cases])
        self.subwindow.show()

    def viewByCountry(self):
        country_name = str(self.selectCountry.currentText())
        self.country_request(country_name)

    def Update(self):
        data = self.Mainrequest()[0]
        self.Active.setText(data[0] + '\n')
        self.Deaths.setText(data[1] + '\n')
        self.Recovered.setText(data[2] + '\n')
        self.Total.setText(data[3] + '\n')

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Creating an app id to show icons in taskbar on windows os
    if platform.system() == 'Windows':
        import ctypes
        app_id = 'yunusemre0037.corona_cases.corona.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    main()