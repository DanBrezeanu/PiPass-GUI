#ifndef WAITINGSCREEN_H
#define WAITINGSCREEN_H

#include <QObject>
#include <QWidget>
#include <QtWidgets>

class WaitingScreen : public QWidget
{
    Q_OBJECT
public:
    explicit WaitingScreen(QWidget *parent = nullptr);

private:
    QLabel *movieLabel;
    QMovie *movie;

private slots:
    void finishedWaiting();


signals:
     void waitingForAuthenticationEnded();

};

#endif // WAITINGSCREEN_H
