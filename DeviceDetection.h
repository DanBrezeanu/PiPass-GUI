#ifndef DEVICE_DETECTION_H
#define DEVICE_DETECTION_H

#include <QObject>
#include <QThread>



class DeviceDetection: public QThread
{
    Q_OBJECT

public:
    static const quint16 VENDOR_ID  = 0x1D6B;
    static const quint16 PRODUCT_ID = 0x0104;

public:
    explicit DeviceDetection(QObject *parent = nullptr);
    void searchDevice();
    void checkDeviceAlive();
    ~DeviceDetection();

private:
    void run() override;

signals:
    void deviceAttached(QString portName);
    void deviceDeattached();
};

#endif // DEVICE_DETECTION_H
