import sys
import datetime
from tkinter import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
import mysql.connector
from datetime import datetime

#============Database=====================
from PyQt5.uic.properties import QtCore

mydb = mysql.connector.connect(host = "localhost", user = "root", passwd = "", database = "cc15(2)")
mycursor = mydb.cursor()
prioritycount = 0
guest_prioritycount = 0
current_account = {"school_id": "", "account_name": ""}

#===========FullScreen====================
my_window=Tk()

class Login(QDialog):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("Login.ui",self)
        self.LoginButton.clicked.connect(self.Loginfunction)
        self.PasswordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.CreateAccountButton.clicked.connect(self.gotoCreate)
        self.GuestButton.clicked.connect(self.gotoGuest)

    def Loginfunction(self):
        UsernameLabel=self.UsernameLine.text()
        PasswordLabel=self.PasswordLine.text()

        checkstudent = "SELECT * FROM student WHERE username = '" + UsernameLabel + "'AND password = '" + PasswordLabel + "'"
        checkfaculty = "SELECT * FROM faculty WHERE username = '" + UsernameLabel + "'AND password = '" + PasswordLabel + "'"

        mycursor.execute(checkstudent)
        student_result = mycursor.fetchone()
        mycursor.execute(checkfaculty)
        faculty_result = mycursor.fetchone()

        if student_result != None:
            QtWidgets.QMessageBox.information(self, "Success", "Greetings! " + UsernameLabel + " You are now login.")
            current_account["account_name"] = student_result[0] + " " + student_result[1]
            mycursor.execute("INSERT INTO logbook (username, date, time) VALUES (%s, %s, %s)", (UsernameLabel, datetime.now().strftime("%d %B %Y"), datetime.now().strftime("%I:%M %p")))
            mydb.commit()
            self.GotoStudent(student_result)

        elif faculty_result != None:
            QtWidgets.QMessageBox.information(self, "Success", "Welcome back! " + UsernameLabel)
            current_account["account_name"] = faculty_result[0] + " " + faculty_result[1]
            mycursor.execute("INSERT INTO logbook (username, date, time) VALUES (%s, %s, %s)", (UsernameLabel, datetime.now().strftime("%d %B %Y"), datetime.now().strftime("%I:%M %p")))
            mydb.commit()
            self.GotoFaculty(faculty_result)

        elif UsernameLabel and PasswordLabel == 'admin':
            QtWidgets.QMessageBox.information(self, "Success", "You have logged in as Admin")
            self.GotoAdmin()

        else:
            QtWidgets.QMessageBox.information(self, "Error", "No Account exist!")
            
        current_account["school_id"] = UsernameLabel

    def gotoGuest(self):
        g = Guest()
        widget.addWidget(g)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def GotoStudent(self, checkstudent):
        smf = StudentMainFrame(checkstudent)
        widget.addWidget(smf)
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def gotoCreate(self):
        ca=CreateAccount()
        widget.addWidget(ca)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def GotoAdmin(self):
        amf = AdminMainFrame()
        widget.addWidget(amf)
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def GotoFaculty(self, checkfaculty):
        fmf = FacultyMainFrame(checkfaculty)
        widget.addWidget(fmf)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class CreateAccount(QDialog):
    def __init__(self):
        super(CreateAccount,self).__init__()
        loadUi("CreateAccount.ui",self)
        self.SignupButton.clicked.connect(self.CreateAccountfunction)
        self.PasswordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ConfirmPasswordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.LogButton.clicked.connect(self.gotologin)

    def CreateAccountfunction(self):
        CreateFirstName=self.FirstNameLine.text()
        CreateLastName=self.LastNameLine.text()
        UsernameLabel=self.UsernameLine.text()
        GenderLabel = 0
        if self.radioButtonMale.isChecked():
            GenderLabel = 'Male'
        elif self.radioButtonFemale.isChecked():
            GenderLabel = 'Female'
        PhoneNumberLabel=self.PhoneNumberLine.text()
        BirthDateLabel=self.BirthDateLine.text()
        DepartmentLabel=str(self.CourseComboBox.currentText())

        if self.PasswordLine.text()==self.ConfirmPasswordLine.text():
            PasswordLabel=self.PasswordLine.text()
            QtWidgets.QMessageBox.information(self,"Congrats", "You have successfully created an Account")
            mycursor.execute(
                "INSERT INTO student (first_name, last_name, sex, phone_number, birth_date, department, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (CreateFirstName, CreateLastName, GenderLabel, PhoneNumberLabel, BirthDateLabel, DepartmentLabel,UsernameLabel, PasswordLabel))
            mydb.commit()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Password is not the Same!')

    def gotologin(self):
        la=Login()
        widget.addWidget(la)
        widget.setCurrentIndex(widget.currentIndex()+1)


class Guest(QMainWindow):
    def __init__(self):
        super(Guest,self).__init__()
        loadUi("Guest.ui",self)
        self.BackButton2.clicked.connect(self.BackButton)
        self.GenerateButton.clicked.connect(self.GenerateFunction)
        self.SubmitButton.clicked.connect(self.submit)
        self.set_details()
        self.set_appointment()

    def set_appointment(self):
        mycursor.execute("SELECT first_name, last_name, username FROM faculty")
        name_list = mycursor.fetchall()
        self.FacultyComboBox.clear()
        for name in name_list:
            self.FacultyComboBox.addItem(name[0] + " " + name[1] + ", email: " + name[2])
    
    def set_details(self):
        mycursor.execute("SELECT current_serve_number FROM guest_now_serving")
        self.a.setText(str(mycursor.fetchone()[0]))

    def GenerateFunction(self):
        mycursor.execute("SELECT count FROM guest_queue")
        number = int(mycursor.fetchone()[0])
        global guest_prioritycount

        if guest_prioritycount < 1:
            self.GuestPrio.setText(str(number).zfill(3))
            mycursor.execute("UPDATE guest_queue SET count = %s", (number+1,)) #OTEN YEY
            mydb.commit()
            guest_prioritycount = 2
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Only 1 Priority Number per User")

    def BackButton(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def submit(self):
        global guest_prioritycount
        NameLabel=self.NameLine.text()
        EmailLabel=self.EmailLine.text()
        PhoneNumberLabel=self.PhoneNumberLine.text()
        FacultyLabel=str(self.FacultyComboBox.currentText())
        ReasonLabel=str(self.ReasonComboBox.currentText())
        PriorityNumberLabel=self.PriorityNumberLine.text()

        if PriorityNumberLabel:
            QtWidgets.QMessageBox.information(self, "Congrats", "You have successfully created an Appointment")
            mycursor.execute(
                "INSERT INTO guest_appointment (name, email, phone_number, faculty, reason, priority_number) VALUES (%s, %s, %s, %s, %s, %s)",
                (NameLabel, EmailLabel, PhoneNumberLabel, FacultyLabel, ReasonLabel, PriorityNumberLabel))
            mydb.commit()
            self.NameLine.setText("")
            self.EmailLine.setText("")
            self.PhoneNumberLine.setText("")
            self.FacultyComboBox.setCurrentIndex(0)
            self.ReasonComboBox.setCurrentIndex(0)
            self.PriorityNumberLine.setText("")
            guest_prioritycount = 0
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Please put a Priority Number.')

class StudentMainFrame(QMainWindow):
    def __init__(self, data):
        super(StudentMainFrame,self).__init__()
        loadUi("StudentMainFrame.ui",self)
        self.HomeButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.HomePage))
        self.HomeButton.clicked.connect(self.home_details)
        self.SetAppointmentButton.clicked.connect(self.set_appointment)
        self.ViewAppointmentButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.ViewAppointmentPage))
        self.ViewAppointmentButton.clicked.connect(self.ViewAppointment)
        self.LogoutButton.clicked.connect(self.LogoutFunction)
        self.GenerateNowButton.clicked.connect(self.generatefunction)
        self.ClearButton.clicked.connect(self.ResetFunction)
        self.SubmitButton.clicked.connect(self.submitfunction)
        self.setinfo(data[0], data[1],data[2],data[3],str(data[4]),data[5])
        self.home_details()
    
    def set_appointment(self):
        self.stackedWidget.setCurrentWidget(self.SetAppointmentPage)
        mycursor.execute("SELECT first_name, last_name, username FROM faculty")
        name_list = mycursor.fetchall()
        self.TeacherComboBox.clear()
        for name in name_list:
            self.TeacherComboBox.addItem(name[0] + " " + name[1] + ", email: " + name[2])
    
    def home_details(self):
        mycursor.execute("SELECT current_serve_number FROM student_now_serving")
        self.label_3.setText(str(mycursor.fetchone()[0]))

    def setinfo(self, fname, lname, gender, contact, bday, department):
        self.F_Label.setText(fname)
        self.L_Label.setText(lname)
        self.G_Label.setText(gender)
        self.C_Label.setText(contact)
        self.B_Label.setText(bday)
        self.D_Label.setText(department)

    def generatefunction(self):
        mycursor.execute("SELECT count FROM student_queue")
        number = int(mycursor.fetchone()[0])
        global prioritycount

        if prioritycount < 1:
            self.Prio.setText(str(number).zfill(3))
            mycursor.execute("UPDATE student_queue SET count = '%s'", (number+1,))
            mydb.commit()
            prioritycount = 2
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Only 1 Priority Number per User")

    def ResetFunction(self):
        self.TeacherComboBox.setCurrentIndex(0)
        self.AppointmentComboBox.setCurrentIndex(0)
        self.PriorityNumberLine.setText("")

    def submitfunction(self):
        global prioritycount
        FacultytoSetLabel=str((self.TeacherComboBox.currentText()).split()[3])
        ReasonLabel=str(self.AppointmentComboBox.currentText())
        PriorityNumberLabel=self.PriorityNumberLine.text()
        date = self.StudentCalendar.selectedDate()

        if PriorityNumberLabel:
            mycursor.execute("SELECT priority_number FROM student_appointment WHERE priority_number = %s",(PriorityNumberLabel,))
            listahan = mycursor.fetchone()
            if listahan == None:
                QtWidgets.QMessageBox.information(self, "Congrats", "You have successfully created an Appointment")
                mycursor.execute(
                    "INSERT INTO student_appointment (student, email, date_of_appointment, faculty, reason, priority_number) VALUES (%s, %s, %s, %s, %s, %s)",
                    (current_account["account_name"], current_account["school_id"], date.toPyDate(), FacultytoSetLabel,
                     ReasonLabel, PriorityNumberLabel))
                mydb.commit()
                self.TeacherComboBox.setCurrentIndex(0)
                self.AppointmentComboBox.setCurrentIndex(0)
                self.PriorityNumberLine.setText("")
                prioritycount = 0
            else:
                QtWidgets.QMessageBox.warning(
                    self, 'Error', 'Please recheck Priority Number.')
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Please put a Priority Number.')

    def ViewAppointment(self):
        self.AppointmentWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.AppointmentWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.AppointmentWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.AppointmentWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.AppointmentWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.AppointmentWidget.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.AppointmentWidget.verticalHeader().hide()
        mycursor.execute(
        "SELECT id, first_name, last_name, date_of_appointment, faculty, reason, priority_number FROM student_appointment LEFT JOIN student ON email = username WHERE email = %s ORDER BY id DESC", (current_account["school_id"],))
        result = mycursor.fetchall()

        self.AppointmentWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            if row_data is None:
                row_data[1]
            name = row_data[1] + " " + row_data[2]

            self.AppointmentWidget.insertRow(row_number)
            self.AppointmentWidget.setItem(row_number, 0, QTableWidgetItem(str(row_data[0])))
            self.AppointmentWidget.setItem(row_number, 1, QTableWidgetItem(str(name)))
            self.AppointmentWidget.setItem(row_number, 2, QTableWidgetItem(str(row_data[3])))
            self.AppointmentWidget.setItem(row_number, 3, QTableWidgetItem(str(row_data[4])))
            self.AppointmentWidget.setItem(row_number, 4, QTableWidgetItem(str(row_data[5])))
            self.AppointmentWidget.setItem(row_number, 5, QTableWidgetItem(str(row_data[6])))


    def LogoutFunction(self):
        login = Login()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Are you sure you want to Logout?")
        msgBox.setWindowTitle("Confirmation")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex() + 1)

student_enrollment_count = 0
guest_enrollment_count = 0
class AdminMainFrame(QMainWindow):
    def __init__(self):
        super(AdminMainFrame,self).__init__()
        loadUi("AdminMainFrame.ui",self)
        self.LogoutButton.clicked.connect(self.gotologin)
        #=============== Priority ====================
        self.PriorityButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.PriorityPage))
        #===================================
        self.LogBookButton.clicked.connect(self.set_logbook)
        self.AppointmentLogsButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.AppointmentPage))
        self.AppointmentLogsButton.clicked.connect(self.ViewLogs)
        self.GuestButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.GeneratedNumberPage))
        self.GuestButton.clicked.connect(self.ViewGuest)
        #=============== Student ==============================
        self.StudentAccountButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.StudentPage))
        self.StudentAccountButton.clicked.connect(self.ViewStudent)
        #=============== Faculty ==============================
        self.FacultyAccountButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.FacultyPage))
        self.FacultyAccountButton.clicked.connect(self.ViewFaculty)
        #=============== Student Prio ==========================
        self.Studentpreviousbutton.clicked.connect(self.StudentPrev)
        self.Studentresetbutton.clicked.connect(self.StudentReset)
        self.Studentnextbutton.clicked.connect(self.StudentNext)
        self.student_currentqueue()
        #=============== Guest Prio ==========================
        self.Guestpreviousbutton.clicked.connect(self.GuestPrev)
        self.Guestresetbutton.clicked.connect(self.GuestReset)
        self.Guestnextbutton.clicked.connect(self.GuestNext)
        self.guest_currentqueue()
        #=============== Student Add Account ====================
        self.AddAccountButton2.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.StudentAddAccountPage))
        self.StudentBackButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.StudentPage))
        self.StudentCreateButton.clicked.connect(self.StudentCreate)
        self.DeleteButton_3.clicked.connect(self.delete_student_from_this_worldu)
        #=============== Faculty Add Account ====================
        self.AddAccountButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.FacultyAddAccountPage))
        self.FacultyBackButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.FacultyPage))
        self.FacultyCreateButton.clicked.connect(self.FacultyCreate)
        self.DeleteButton.clicked.connect(self.delete_faculty_from_this_worldu)
    
    def GuestReset(self):
        mycursor.execute("UPDATE guest_queue SET count = 1")
        mydb.commit()

    def guest_currentqueue(self):
        global guest_enrollment_count
        mycursor.execute("SELECT priority_number FROM guest_appointment")
        self.guest_appointment_list = mycursor.fetchall()
        if self.guest_appointment_list == []:
            self.lineEdit_2.setText("None")
        else:
            self.lineEdit_2.setText(str(self.guest_appointment_list[0][0]))
        mycursor.execute("UPDATE guest_now_serving SET current_serve_number = %s", (self.lineEdit_2.text(),))
        mydb.commit()

    def GuestPrev(self):
        global guest_enrollment_count
        guest_enrollment_count -= 1

        if self.guest_appointment_list == [] or guest_enrollment_count == -1:
            guest_enrollment_count = 0
            self.lineEdit_2.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))
        else:
            self.lineEdit_2.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))
        
        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.lineEdit_2.text(),))
        mydb.commit()

    def GuestNext(self):
        global guest_enrollment_count
        guest_enrollment_count += 1

        if self.guest_appointment_list == []:
            self.lineEdit_2.setText("None")
        else:
            try:
                self.lineEdit_2.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))
            except:
                guest_enrollment_count = len(self.guest_appointment_list) -1
                self.lineEdit_2.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.lineEdit_2.text(),))
        mydb.commit()
    
    def delete_student_from_this_worldu(self):
        username = self.StudentWidget.item(self.StudentWidget.currentRow(), 2).text()
        mycursor.execute("DELETE FROM student WHERE username = %s", (username,))
        mydb.commit()

        self.stackedWidget.setCurrentWidget(self.StudentPage)
        self.set_logbook()
    
    def delete_faculty_from_this_worldu(self):
        username = self.FacultyWidget.item(self.FacultyWidget.currentRow(), 2).text()
        mycursor.execute("DELETE FROM faculty WHERE username = %s", (username,))
        mydb.commit()

        self.stackedWidget.setCurrentWidget(self.FacultyPage)
        self.set_logbook()

    def set_logbook(self):
        self.stackedWidget.setCurrentWidget(self.LogBookPage)
        self.LogBookWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.LogBookWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.LogBookWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.LogBookWidget.verticalHeader().hide()

        mycursor.execute("""
        SELECT 
            student.first_name, 
            student.last_name, 
            faculty.first_name, 
            faculty.last_name, 
            date, 
            time, 
            student.username
        FROM 
            logbook 
            LEFT JOIN 
                student 
                ON student.username = logbook.username
            LEFT JOIN
                faculty
                ON faculty.username = logbook.username""")
        logbook_list = mycursor.fetchall()

        self.LogBookWidget.setRowCount(0)
        for row_number, row_data in enumerate(logbook_list):
            if row_data[6] is None:
                self.LogBookWidget.insertRow(row_number)

                if row_data[2] is None and row_data[3] is None:
                    name = "None"
                else:
                    name = row_data[2] + " " + row_data[3]

                self.LogBookWidget.setItem(row_number, 0, QTableWidgetItem(name))
            else:
                self.LogBookWidget.insertRow(row_number)

                if row_data[0] is None and row_data[1] is None:
                    name = "None"
                else:
                    name = row_data[0] + " " + row_data[1]

                self.LogBookWidget.setItem(row_number, 0, QTableWidgetItem(name))
            self.LogBookWidget.setItem(row_number, 1, QTableWidgetItem(row_data[4]))
            self.LogBookWidget.setItem(row_number, 2, QTableWidgetItem(row_data[5]))



    def student_currentqueue(self):
        global student_enrollment_count
        mycursor.execute("SELECT priority_number FROM student_appointment")
        self.student_appointment_list = mycursor.fetchall()
        if self.student_appointment_list == []:
            self.lineEdit.setText("None")
        else:
            self.lineEdit.setText(str(self.student_appointment_list[0][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.lineEdit.text(),))
        mydb.commit()

    def StudentPrev(self):
        global student_enrollment_count
        student_enrollment_count -= 1

        if self.student_appointment_list == [] or student_enrollment_count == -1:
            student_enrollment_count = 0
            self.lineEdit.setText(str(self.student_appointment_list[student_enrollment_count][0]))
        else:
            self.lineEdit.setText(str(self.student_appointment_list[student_enrollment_count][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.lineEdit.text(),))
        mydb.commit()

    def StudentReset(self):
        mycursor.execute("UPDATE student_queue SET count = 1")
        mydb.commit()

    def StudentNext(self):
        global student_enrollment_count
        student_enrollment_count += 1

        if self.student_appointment_list == []:
            self.lineEdit.setText("None")
        else:
            try:
                self.lineEdit.setText(str(self.student_appointment_list[student_enrollment_count][0]))
            except:
                student_enrollment_count = len(self.student_appointment_list) -1
                self.lineEdit.setText(str(self.student_appointment_list[student_enrollment_count][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.lineEdit.text(),))
        mydb.commit()

    def ViewGuest(self):
        mycursor.execute(
        "SELECT * FROM guest_appointment")
        result = mycursor.fetchall()
        self.GuestLogWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            #print(row_number)
            self.GuestLogWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                # print(column_number)
                self.GuestLogWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def ViewLogs(self):
        mycursor.execute(
        "SELECT * FROM student_appointment")
        result = mycursor.fetchall()
        self.AppointmentLogsWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            #print(row_number)
            self.AppointmentLogsWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                # print(column_number)
                self.AppointmentLogsWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def ViewStudent(self):
        mycursor.execute(
        "SELECT first_name, last_name, username, sex, password FROM student")
        result = mycursor.fetchall()

        self.StudentWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentWidget.verticalHeader().hide()

        self.StudentWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.StudentWidget.insertRow(row_number)
            self.StudentWidget.setItem(row_number, 0, QTableWidgetItem(row_data[0]))
            self.StudentWidget.setItem(row_number, 1, QTableWidgetItem(row_data[1]))
            self.StudentWidget.setItem(row_number, 2, QTableWidgetItem(row_data[2]))
            self.StudentWidget.setItem(row_number, 3, QTableWidgetItem(row_data[3]))
            self.StudentWidget.setItem(row_number, 4, QTableWidgetItem(row_data[4]))

    def StudentCreate(self):
        CreateFirstName = self.FirstNameLine.text()
        CreateLastName = self.LastNameLine.text()
        UsernameLabel = self.UsernameLine.text()
        GenderLabel = 0
        if self.radioButtonMale.isChecked():
            GenderLabel = 'Male'
        elif self.radioButtonFemale.isChecked():
            GenderLabel = 'Female'
        PhoneNumberLabel = self.PhoneNumberLine.text()
        BirthDateLabel = self.BirthDateLine.text()
        DepartmentLabel = str(self.CourseComboBox.currentText())
        if self.PasswordLine.text()==self.ConfirmPasswordLine.text():
            PasswordLabel=self.PasswordLine.text()
            QtWidgets.QMessageBox.information(self,"Congrats", "You have successfully created an Account")

            mycursor.execute(
                "INSERT INTO student (first_name, last_name, sex, phone_number, birth_date, department, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (CreateFirstName, CreateLastName, GenderLabel, PhoneNumberLabel, BirthDateLabel, DepartmentLabel,
                 UsernameLabel, PasswordLabel))
            mydb.commit()
            self.stackedWidget.setCurrentWidget(self.StudentPage)
            self.ViewStudent()

        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Password is not the Same!')

    def ViewFaculty(self):
        mycursor.execute(
        "SELECT first_name, last_name, username, sex, password FROM faculty")
        result = mycursor.fetchall()

        self.FacultyWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.FacultyWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.FacultyWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.FacultyWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.FacultyWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.FacultyWidget.verticalHeader().hide()

        self.FacultyWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.FacultyWidget.insertRow(row_number)
            self.FacultyWidget.setItem(row_number, 0, QTableWidgetItem(row_data[0]))
            self.FacultyWidget.setItem(row_number, 1, QTableWidgetItem(row_data[1]))
            self.FacultyWidget.setItem(row_number, 2, QTableWidgetItem(row_data[2]))
            self.FacultyWidget.setItem(row_number, 3, QTableWidgetItem(row_data[3]))
            self.FacultyWidget.setItem(row_number, 4, QTableWidgetItem(row_data[4]))

    def FacultyCreate(self):
        CreateFirstName_2 = self.FirstNameLine_2.text()
        CreateLastName_2 = self.LastNameLine_2.text()
        UsernameLabel_2 = self.UsernameLine_2.text()
        GenderLabel_2 = 0
        if self.radioButtonMale_2.isChecked():
            GenderLabel_2 = 'Male'
        elif self.radioButtonFemale_2.isChecked():
            GenderLabel_2 = 'Female'
        PhoneNumberLabel_2 = self.PhoneNumberLine_2.text()
        BirthDateLabel_2 = self.BirthDateLine_2.text()
        DepartmentLabel_2 = str(self.CourseComboBox_2.currentText())
        if self.PasswordLine_2.text()==self.ConfirmPasswordLine_2.text():
            PasswordLabel_2=self.PasswordLine_2.text()
            QtWidgets.QMessageBox.information(self,"Congrats", "You have successfully created an Account")
            mycursor.execute(
                "INSERT INTO faculty (first_name, last_name, sex, department, phone_number, birth_date, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (CreateFirstName_2, CreateLastName_2, GenderLabel_2, DepartmentLabel_2, PhoneNumberLabel_2, BirthDateLabel_2, UsernameLabel_2, PasswordLabel_2))
            mydb.commit()
            self.stackedWidget.setCurrentWidget(self.FacultyPage)

        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Password is not the Same!')


    def gotologin(self):
        login = Login()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Are you sure you want to Logout?")
        msgBox.setWindowTitle("Confirmation")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex() + 1)

student_enrollment_count = 0
guest_enrollment_count = 0
class FacultyMainFrame(QMainWindow):
    def __init__(self, data):
        super(FacultyMainFrame, self).__init__()
        loadUi("FacultyMainFrame.ui",self)
        self.LogoutButton.clicked.connect(self.gotologin)
        self.ViewPrioButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.PriorityPage))
        self.StudentAppointmentsButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.AppointmentsPage))
        self.StudentAppointmentsButton.clicked.connect(self.getstudentdata)
        self.GuestAppointmentsButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.GuestPage))
        self.GuestAppointmentsButton.clicked.connect(self.getguestdata)
        ##################### Student Prio ###################################
        self.StudentPreviousButton.clicked.connect(self.studentprev)
        self.StudentResetButton.clicked.connect(self.studentreset)
        self.StudentNextButton.clicked.connect(self.studentnext)
        ##################### Guest Prio ###################################
        self.GuestPreviousButton.clicked.connect(self.guestprev)
        self.GuestResetButton.clicked.connect(self.guestreset)
        self.GuestNextButton.clicked.connect(self.guestnext)
        ###################### Info ########################################
        self.setinfo(data[0], data[1], data[2], data[3], data[4], str(data[5]), data[6])
        self.student_currentqueue()
        self.guest_currentqueue()
###################### Student Function #######################################

    def student_currentqueue(self):
        global student_enrollment_count
        mycursor.execute("SELECT priority_number FROM student_appointment")
        self.student_appointment_list = mycursor.fetchall()
        if self.student_appointment_list == []:
            self.StudentPrio.setText("None")
        else:
            self.StudentPrio.setText(str(self.student_appointment_list[0][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.StudentPrio.text(),))
        mydb.commit()

    def studentprev(self):
        global student_enrollment_count
        student_enrollment_count -= 1

        if self.student_appointment_list == [] or student_enrollment_count == -1:
            student_enrollment_count = 0
            self.StudentPrio.setText(str(self.student_appointment_list[student_enrollment_count][0]))
        else:
            self.StudentPrio.setText(str(self.student_appointment_list[student_enrollment_count][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.StudentPrio.text(),))
        mydb.commit()

    def studentreset(self):
        mycursor.execute("UPDATE student_queue SET count = 1")
        mydb.commit()

    def studentnext(self):
        global student_enrollment_count
        student_enrollment_count += 1

        if self.student_appointment_list == []:
            self.StudentPrio.setText("None")
        else:
            try:
                self.StudentPrio.setText(str(self.student_appointment_list[student_enrollment_count][0]))
            except:
                student_enrollment_count = len(self.student_appointment_list) -1
                self.StudentPrio.setText(str(self.student_appointment_list[student_enrollment_count][0]))

        mycursor.execute("UPDATE student_now_serving SET current_serve_number = %s", (self.StudentPrio.text(),))
        mydb.commit()
###################### Guest Function #######################################
    def guest_currentqueue(self):
        global guest_enrollment_count
        mycursor.execute("SELECT priority_number FROM guest_appointment")
        self.guest_appointment_list = mycursor.fetchall()

        if self.guest_appointment_list == []:
            self.GuestPrio.setText("None")
        else:
            self.GuestPrio.setText(str(self.guest_appointment_list[0][0]))

        mycursor.execute("UPDATE guest_now_serving SET current_serve_number = %s", (self.GuestPrio.text(),))
        mydb.commit()

    def guestprev(self):
        global guest_enrollment_count
        guest_enrollment_count -= 1

        if self.guest_appointment_list == [] or guest_enrollment_count == -1:
            guest_enrollment_count = 0
            self.GuestPrio.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))
        else:
            self.GuestPrio.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))

        mycursor.execute("UPDATE guest_now_serving SET current_serve_number = %s", (self.GuestPrio.text(),))
        mydb.commit()

    def guestreset(self):
        mycursor.execute("UPDATE guest_queue SET count = 1")
        mydb.commit()

    def guestnext(self):
        global guest_enrollment_count
        guest_enrollment_count += 1

        if self.guest_appointment_list == []:
            self.GuestPrio.setText("None")
        else:
            try:
                self.GuestPrio.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))
            except:
                guest_enrollment_count = len(self.guest_appointment_list) -1
                self.GuestPrio.setText(str(self.guest_appointment_list[guest_enrollment_count][0]))

        mycursor.execute("UPDATE guest_now_serving SET current_serve_number = %s", (self.GuestPrio.text(),))
        mydb.commit()
###############################################################################

    def setinfo(self, fname, lname, gender, department, contact, bday, email):
        self.F_Label.setText(fname)
        self.L_Label.setText(lname)
        self.G_Label.setText(gender)
        self.D_Label.setText(department)
        self.C_Label.setText(contact)
        self.B_Label.setText(bday)
        self.E_Label.setText(email)

    def getstudentdata(self):
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.verticalHeader().hide()
        mycursor.execute(
            "SELECT id, first_name, last_name, date_of_appointment, faculty, reason, priority_number FROM student_appointment LEFT JOIN student ON student = username WHERE faculty = %s ORDER BY id DESC", (current_account["school_id"],))
        result = mycursor.fetchall()
        self.StudentAppointmentsWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.StudentAppointmentsWidget.insertRow(row_number)
            if row_data[1] is None:
                fname = "None"
            if row_data[2] is None:
                lname = "None"
            name = fname + " " + lname
            self.StudentAppointmentsWidget.setItem(row_number, 0, QTableWidgetItem(str(row_data[0])))
            self.StudentAppointmentsWidget.setItem(row_number, 1, QTableWidgetItem(str(name)))
            self.StudentAppointmentsWidget.setItem(row_number, 2, QTableWidgetItem(str(row_data[3])))
            self.StudentAppointmentsWidget.setItem(row_number, 3, QTableWidgetItem(str(row_data[4])))
            self.StudentAppointmentsWidget.setItem(row_number, 4, QTableWidgetItem(str(row_data[5])))
            self.StudentAppointmentsWidget.setItem(row_number, 5, QTableWidgetItem(str(row_data[6])))

    def getguestdata(self):
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.StudentAppointmentsWidget.verticalHeader().hide()
        mycursor.execute(
            "SELECT * FROM guest_appointment")
        result = mycursor.fetchall()

        self.GuestAppointmentsWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):

            self.GuestAppointmentsWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):

                self.GuestAppointmentsWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def gotologin(self):
        login = Login()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Are you sure you want to Logout?")
        msgBox.setWindowTitle("Confirmation")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex() + 1)


app=QApplication(sys.argv)
mainwindow=Login()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.show()
#widget.showMaximized()
app.exec_()