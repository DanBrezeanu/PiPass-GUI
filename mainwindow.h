#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include "DeviceDetection.h"

#include <QMainWindow>
#include <QString>

QT_BEGIN_NAMESPACE
namespace Ui {
    class MainWindow;
    class LoadingScreen;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    DeviceDetection detection_thread;
    QWidget *loadingSplashScreen;
    void startApplication();

private slots:
    void finishLoading(QString portName);
    void startLoading();

};
#endif // MAINWINDOW_H
