#ifndef COMMANDS_H
#define COMMANDS_H

#include <QObject>
#include <stdint.h>
#include <exception>

class Command
{
public:
    class Type {
    public:
        static const uint8_t SENDER_PIPASS = 0x01;
        static const uint8_t SENDER_APP    = 0x02;
        static const uint8_t SENDER_PLUGIN = 0x03;

        static const uint8_t APP_HELLO               = 0xB0;
        static const uint8_t NO_COMMAND              = 0x00;
        static const uint8_t LIST_CREDENTIALS        = 0xC0;
        static const uint8_t DELIVER_CREDENTIALS_HID = 0xC1;
        static const uint8_t DELIVER_CRED_PASSWD_HID = 0xC2;
        static const uint8_t DELIVER_CRED_USER_HID   = 0xC3;
        static const uint8_t DELIVER_CREDENTIALS_ACM = 0xC2;
        static const uint8_t DELETE_CREDENTIALS      = 0xC3;
        static const uint8_t STORE_CREDENTIALS       = 0xC4;
        static const uint8_t EDIT_CREDENTIALS        = 0xC5;

        static const uint8_t ENROLL_FINGERPRINT = 0xC5;
        static const uint8_t DELETE_FINGERPRINT = 0xC6;
        static const uint8_t LIST_FINGERPRINT   = 0xC7;

        static const uint8_t LOCK_DEVICE        = 0xC8;
        static const uint8_t WIPE_DEVICE        = 0xC9;

        static const uint8_t CHANGE_PIN         = 0xCA;
        static const uint8_t CHANGE_DIP_SWITCH  = 0xCB;

        static const uint8_t ASK_FOR_PASSWORD   = 0xCC;
        static const uint8_t ASK_FOR_PIN        = 0xCD;

        static const uint8_t DEVICE_AUTHENTICATED = 0xCE;
    };


    class Code {
    public:
        static const uint8_t SUCCESS = 0x00;
        static const uint8_t ERROR   = 0x01;
    };

    Command();
    Command(QByteArray buf);
    Command(uint8_t type, uint8_t errorCode, bool isReply = true);

    Command *type(uint8_t type);
    Command *sender(uint8_t sender);
    Command *length(uint16_t length);
    Command *options(QByteArray *options);
    Command *options(uint8_t *options, int size);
    Command *isReply(bool isReply);
    Command *replyCode(uint8_t replyCode);


    uint8_t getType() const;
    uint8_t getSender() const;
    uint16_t getLength() const;
    QByteArray *getOptions() const;
    bool getIsReply() const;
    uint8_t getReplyCode() const;


    QByteArray toQByteArray() const;
    char *toCharArray(int &size) const;


private:
    bool checkCRC();
    void updateCRC();
    uint16_t calculateCRC();

private:
    uint8_t mSender;
    uint8_t mType;
    uint16_t mLength;
    QByteArray *mOptions;
    bool mIsReply;
    uint8_t mReplyCode;
    uint16_t mCRC;
};


class InvalidCRC: public std::exception {};

#endif // COMMANDS_H
