#include "Command.h"
#include "DeviceConnection.h"

#include <QObject>
#include <QDebug>

Command::Command() {
    this->mType = this->mSender = this->mLength =
    this->mIsReply = this->mReplyCode = this->mCRC = 0;

    this->mOptions = nullptr;
}

Command::Command(QByteArray buf)
{
    int idx = 0;

    this->mType = (uint8_t)buf[idx++];
    this->mSender = (uint8_t)buf[idx++];

    memcpy(&(this->mLength), buf.constData() + idx, sizeof(uint16_t));
    idx += 2;

    if (this->mLength) {
        this->mOptions = new QByteArray(buf.constData() + 4, this->mLength);
        idx += this->mLength;
    }
    else
        this->mOptions = NULL;

    this->mIsReply = !!buf[idx++];
    this->mReplyCode = buf[idx++];

    memcpy(&(this->mCRC), buf.constData() + idx, sizeof(uint16_t));

    if (!checkCRC())
        throw InvalidCRC();
}

Command::Command(uint8_t type, uint8_t errorCode, bool isReply) {
    this->mType = type;
    this->mReplyCode = errorCode;
    this->mIsReply = isReply;
    this->mSender = Command::Type::SENDER_APP;

    this->mLength = 0;
    this->mOptions = NULL;

    updateCRC();
}


Command *Command::type(uint8_t type) {
    this->mType = type;
    updateCRC();

    return this;
}

Command *Command::sender(uint8_t sender) {
    this->mSender = sender;
    updateCRC();

    return this;
}

Command *Command::length(uint16_t length) {
    this->mLength = length;
    updateCRC();

    return this;
}

Command *Command::options(QByteArray *options) {
    this->mOptions = new QByteArray(*options);
    updateCRC();

    return this;
}

Command *Command::options(uint8_t *options, int size) {
    this->mOptions = new QByteArray((char *)options, size);
    updateCRC();

    return this;
}

Command *Command::isReply(bool isReply) {
    this->mIsReply = isReply;
    updateCRC();

    return this;
}

Command *Command::replyCode(uint8_t replyCode) {
    this->mReplyCode = replyCode;
    updateCRC();

    return this;
}

uint8_t Command::getType() const {
    return this->mType;
}

uint8_t Command::getSender() const {
    return this->mSender;
}

uint16_t Command::getLength() const {
    return this->mLength;
}

QByteArray *Command::getOptions() const {
    return this->mOptions;
}

bool Command::getIsReply() const {
    return this->mIsReply;
}

uint8_t Command::getReplyCode() const {
    return this->mReplyCode;
}

char *Command::toCharArray(int &size) const {
    char *bytes = new char[DeviceConnection::PACKET_SIZE];
    int idx = 0;

    memcpy(bytes + idx, &this->mType, sizeof(this->mType));
    idx += sizeof(this->mType);

    memcpy(bytes + idx, &this->mSender, sizeof(this->mSender));
    idx += sizeof(this->mSender);

    memcpy(bytes + idx, &this->mLength, sizeof(this->mLength));
    idx += sizeof(this->mLength);

    if (this->mLength && this->mOptions) {
        memcpy(bytes + idx, this->mOptions->toStdString().c_str(), this->mLength);
        idx += this->mLength;
    }

    memcpy(bytes + idx, &this->mIsReply, sizeof(this->mIsReply));
    idx += sizeof(this->mIsReply);

    memcpy(bytes + idx, &this->mReplyCode, sizeof(this->mReplyCode));
    idx += sizeof(this->mReplyCode);

    memcpy(bytes + idx, &this->mCRC, sizeof(this->mCRC));
    idx += sizeof(this->mCRC);

    size = idx;

    return bytes;
}

QByteArray Command::toQByteArray() const {

    int size = 0;
    char *charArray = this->toCharArray(size);
    return QByteArray(charArray, size);
}


uint16_t Command::calculateCRC() {
    uint16_t crc = 0;

    crc += this->mType;
    crc += this->mSender;
    crc = (uint32_t)(crc + this->mLength) % UINT16_MAX;
    if (this->mLength && this->mOptions)
        for (auto& byte: *this->mOptions)
            crc = (uint32_t)(crc + (uint8_t)byte) % UINT16_MAX;

    crc = (uint32_t)(crc + this->mIsReply) % UINT16_MAX;
    crc = (uint32_t)(crc + this->mReplyCode) % UINT16_MAX;

    return crc;
}

bool Command::checkCRC() {
    return (calculateCRC() == this->mCRC);
}

void Command::updateCRC() {
    this->mCRC = calculateCRC();
}


