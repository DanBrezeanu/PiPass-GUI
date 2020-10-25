#include "LoadingScreen.h"

#include <QLabel>
#include <QMovie>
#include <QTextBlock>
#include <QtWidgets>
#include <QMainWindow>

#include <QtDebug>

LoadingScreen::LoadingScreen(QWidget *parent)
      : QWidget(parent)   
{
    QVBoxLayout *vLayout = new QVBoxLayout(this);
    QGridLayout *gridLayout = new QGridLayout(this);
    QLabel *connTextLabel = new QLabel("<b>Waiting for device connection</b>");

    movieLabel = new QLabel(this);
    movie = new QMovie(":/gifs/loading-animation-300px.gif");
    movieLabel->setFixedSize(150, 150);
    movie->setScaledSize(movieLabel->size());
    movieLabel->setMovie(movie);


    connTextLabel->setFont(QFont("Arial", 16, 2));

    movie->start();


    gridLayout->addWidget(movieLabel, 0, 1, Qt::AlignHCenter | Qt::AlignVCenter);
    vLayout->addLayout(gridLayout);
    vLayout->addWidget(connTextLabel, 0,  Qt::AlignHCenter | Qt::AlignVCenter);
}

LoadingScreen::~LoadingScreen() {}
