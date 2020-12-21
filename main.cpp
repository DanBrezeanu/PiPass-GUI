#include "mainwindow.h"

#include <QApplication>
#include <QDesktopWidget>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QDesktopWidget dw;
    MainWindow w;
    w.setFixedSize(dw.width() * 0.7, dw.height() * 0.7);
    w.show();
    return a.exec();
}
