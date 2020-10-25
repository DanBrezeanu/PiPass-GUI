#include "DeviceDetection.h"

#include <QSerialPort>
#include <QSerialPortInfo>
#include <QDebug>

DeviceDetection::DeviceDetection(QObject *parent) :
    QThread(parent)
{
}

void DeviceDetection::run()
{
    while(true) {
        searchDevice();
        checkDeviceAlive();
    }
}

void DeviceDetection::searchDevice()
{
    while (true) {
        const auto infos = QSerialPortInfo::availablePorts();
        for (const QSerialPortInfo &info : infos)
            if (info.hasProductIdentifier() and info.hasVendorIdentifier())
                if (info.productIdentifier() == DeviceDetection::PRODUCT_ID and
                 info.vendorIdentifier() == DeviceDetection::VENDOR_ID) {
                    emit deviceAttached(info.portName());
                    return;
                }

        QThread::msleep(500);
    }
}

void DeviceDetection::checkDeviceAlive()
{
    bool isDeviceAlive;

    while (true) {
        isDeviceAlive = false;

        const auto infos = QSerialPortInfo::availablePorts();
        for (const QSerialPortInfo &info : infos)
            if (info.hasProductIdentifier() and info.hasVendorIdentifier())
                if (info.productIdentifier() == DeviceDetection::PRODUCT_ID and
                 info.vendorIdentifier() == DeviceDetection::VENDOR_ID) {
                    isDeviceAlive = true;
                    break;
                }

        if (!isDeviceAlive) {
            emit deviceDeattached();
            return;
        }
        QThread::msleep(500);
    }
}

DeviceDetection::~DeviceDetection() {}
