#ifndef PASSWORDSCREEN_H
#define PASSWORDSCREEN_H

#include <QObject>
#include <QWidget>
#include <QtWidgets>

class PasswordScreen : public QWidget
{
    Q_OBJECT
public:
    explicit PasswordScreen(QWidget *parent = nullptr);

private:
    QLineEdit *passwordText;

private slots:
    void finishedEnteringPassword();


signals:
     void passwordEntered(QString password);

};

#endif // PASSWORDSCREEN_H
