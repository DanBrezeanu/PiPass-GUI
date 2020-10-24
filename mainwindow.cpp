#include "mainwindow.h"
#include "ui_mainwindow.h"

#include "DeviceDetection.h"

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


    QLabel *lbl = new QLabel(this);
    QMovie *movie = new QMovie(":/gifs/loading-animation-300px.gif");
    lbl->setFixedSize(200, 200);
    movie->setScaledSize(lbl->size());
    lbl->setMovie(movie);

    movie->start();
    this->setCentralWidget(lbl);

//    QVBoxLayout *mainLayout = new QVBoxLayout(this);
//    mainLayout->addWidget(lbl);

//    this->setCentralWidget(mainLayout);
//    ui->->addWidget(newButton, rowNumber, colNumber);


    connect(&detection_thread, &DeviceDetection::deviceAttached, this, &MainWindow::finishLoading);
    connect(&detection_thread, &DeviceDetection::deviceDeattached, this, &MainWindow::startLoading);
    detection_thread.start();
}

void MainWindow::finishLoading(QString portName) {
    qDebug() << portName;
}

void MainWindow::startLoading() {
    qDebug() << "Device lost\n";
}

MainWindow::~MainWindow()
{
    delete ui;
}

