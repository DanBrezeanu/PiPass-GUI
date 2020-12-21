#ifndef DEVICECONNECTION_H
#define DEVICECONNECTION_H

#include <QObject>
#include <QThread>
#include <QSerialPort>

#include "Command.h"

class DeviceConnection: public QObject
{
    Q_OBJECT
public:
    DeviceConnection(QString portName);

    void sendAppHello();

private:
     void sendCommand();

private:
     QSerialPort *serial;
     Command *cmd;

public:
     static const uint32_t PACKET_SIZE = 256;


private slots:
    void readAndDecodeData();

public slots:
    void sendPassword(QString password);
    void sendPin(QString pin);

signals:
    void askedForPin();
    void askedForPassword();


};

#endif // DEVICECONNECTION_H
