#include "mainwindow.h"
#include "ui_mainwindow.h"

#include "DeviceDetection.h"
#include "LoadingScreen.h"
#include "PasswordScreen.h"
#include "DeviceConnection.h"
#include "Command.h"

#include <QLabel>
#include <QMovie>
#include <QDebug>
#include <QtWidgets>
#include <QObject>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    statusBar()->hide();
    this->setStyleSheet("background-color: #FFFFFF;");


    startApplication();

}

void MainWindow::finishLoading(QString portName) {
    loadingSplashScreen->deleteLater();

    connection = new DeviceConnection(portName);

    connect(connection, &DeviceConnection::askedForPassword, this, &MainWindow::showPasswordScreen);
    connect(connection, &DeviceConnection::askedForPin, this, &MainWindow::showPinScreen);

    connection->sendAppHello();

}

void MainWindow::startLoading() {
    loadingSplashScreen = new LoadingScreen(this);

    this->setCentralWidget(loadingSplashScreen);
}

void MainWindow::startApplication() {
    startLoading();

    connect(&detection_thread, &DeviceDetection::deviceAttached, this, &MainWindow::finishLoading);
    connect(&detection_thread, &DeviceDetection::deviceDeattached, this, &MainWindow::startLoading);

    detection_thread.start();
}

void MainWindow::showPasswordScreen() {
    passwordScreen = new PasswordScreen(this);

    connect(
        passwordScreen,
        SIGNAL(passwordEntered(QString)),
        connection,
        SLOT(sendPassword(QString))
    );

    this->setCentralWidget(passwordScreen);


}

void MainWindow::showPinScreen() {
    passwordScreen = new PasswordScreen(this);

    connect(
        passwordScreen,
        SIGNAL(passwordEntered(QString)),
        connection,
        SLOT(sendPin(QString))
    );

    this->setCentralWidget(passwordScreen);
}

//void MainWindow::hidePasswordScreen(QString password) {
//    delete passwordScreen;

//    connection->
//}

MainWindow::~MainWindow()
{
    delete ui;
}

