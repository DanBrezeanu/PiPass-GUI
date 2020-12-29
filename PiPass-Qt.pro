QT       += core gui serialport

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++11

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    Command.cpp \
    DeviceConnection.cpp \
    DeviceDetection.cpp \
    LoadingScreen.cpp \
    PasswordScreen.cpp \
    WaitingScreen.cpp \
    main.cpp \
    mainwindow.cpp

HEADERS += \
    Command.h \
    DeviceConnection.h \
    DeviceDetection.h \
    LoadingScreen.h \
    PasswordScreen.h \
    WaitingScreen.h \
    mainwindow.h

FORMS += \
    mainwindow.ui

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

RESOURCES += \
    files.qrc \
    images.qrc

DISTFILES += \
    setPermissionsDevice.sh
