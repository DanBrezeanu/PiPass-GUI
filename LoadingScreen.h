#ifndef LOADINGSCREEN_H
#define LOADINGSCREEN_H

#include "ui_loadingscreen.h"

#include <QWidget>
#include <QLabel>
#include <QMovie>
#include <QVBoxLayout>

class LoadingScreen: public QWidget
{
    Q_OBJECT
public:
    LoadingScreen(QWidget *parent = nullptr);
    ~LoadingScreen();

private:
    QLabel *movieLabel;
    QMovie *movie;

};

#endif // LOADINGSCREEN_H
