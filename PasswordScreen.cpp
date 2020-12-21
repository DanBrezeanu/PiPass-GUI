#include "PasswordScreen.h"

#include <QLabel>
#include <QMovie>
#include <QTextBlock>
#include <QtWidgets>
#include <QMainWindow>

PasswordScreen::PasswordScreen(QWidget *parent) : QWidget(parent)
{
    QVBoxLayout *vLayout = new QVBoxLayout(this);

    passwordText = new QLineEdit(this);
    passwordText->setEchoMode(QLineEdit::Password);
    passwordText->setFont(QFont("Arial", 16, 2));

    QLabel *passwordLabel = new QLabel("Enter your password");
    passwordLabel->setFont(QFont("Arial", 16, 2));

    QPushButton *okButton = new QPushButton("OK", this);

    vLayout->addWidget(passwordLabel, 0, Qt::AlignHCenter);
    vLayout->addWidget(passwordText, 0, Qt::AlignHCenter);
    vLayout->addWidget(okButton, 0, Qt::AlignHCenter);

    connect(okButton, &QPushButton::pressed, this, &PasswordScreen::finishedEnteringPassword);
}

void PasswordScreen::finishedEnteringPassword() {
/* TODO: sanity check */

    emit passwordEntered(passwordText->text());
}
