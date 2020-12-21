#include "DeviceConnection.h"

#include <QSerialPort>
#include <QSerialPortInfo>
#include <QDebug>
#include <QTime>

#include "Command.h"

#include <stdint.h>

DeviceConnection::DeviceConnection(QString portName)
{
    serial = new QSerialPort();
    serial->setPortName(portName);
    serial->setBaudRate(QSerialPort::Baud9600);
    serial->setDataBits(QSerialPort::Data8);
    serial->setParity(QSerialPort::NoParity);
    serial->setStopBits(QSerialPort::OneStop);
    serial->setFlowControl(QSerialPort::NoFlowControl);
    if (serial->open(QIODevice::ReadWrite)) {
        qInfo() << "Connected!";
    } else {
        qInfo() << "Not connected!";
    }

    connect(serial, &QSerialPort::readyRead, this, &DeviceConnection::readAndDecodeData);
}

void DeviceConnection::readAndDecodeData()
{
   QByteArray data = serial->readAll();

   try {
       this->cmd = new Command(data);
   }  catch (InvalidCRC) {
       this->cmd = new Command((uint8_t)data[0], Command::Code::ERROR);
       sendCommand();
       return;
   }

   switch (this->cmd->getType()) {
   case Command::Type::ASK_FOR_PASSWORD:
       if (!this->cmd->getIsReply())
           emit DeviceConnection::askedForPassword();
       break;
   case Command::Type::ASK_FOR_PIN:
       if (!this->cmd->getIsReply())
           emit DeviceConnection::askedForPin();
       break;
   }

}

void DeviceConnection::sendCommand() {
    if (this->cmd == NULL)
        return;

    int cmdSize;
    char *cmdBytes = this->cmd->toCharArray(cmdSize);

    qInfo() << cmdSize;
    qint64 ret = serial->write(cmdBytes, DeviceConnection::PACKET_SIZE);
    qInfo() << ret;
}

void DeviceConnection::sendAppHello() {
    this->cmd = (new Command())
            ->type(Command::Type::APP_HELLO)
            ->sender(Command::Type::SENDER_APP)
            ->length(0)
            ->isReply(false)
            ->replyCode(Command::Code::SUCCESS);

    sendCommand();
}

void DeviceConnection::sendPassword(QString password) {
    this->cmd = (new Command())
            ->type(Command::Type::ASK_FOR_PASSWORD)
            ->sender(Command::Type::SENDER_APP)
            ->length(password.size())
            ->options(new QByteArray(password.toUtf8()))
            ->isReply(true)
            ->replyCode(Command::Code::SUCCESS);

    sendCommand();
}

void DeviceConnection::sendPin(QString pin) {
    this->cmd = (new Command())
            ->type(Command::Type::ASK_FOR_PIN)
            ->sender(Command::Type::SENDER_APP)
            ->length(pin.size())
            ->options(new QByteArray(pin.toUtf8()))
            ->isReply(true)
            ->replyCode(Command::Code::SUCCESS);

    sendCommand();
}

