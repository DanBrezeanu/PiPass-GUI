#ifndef LOADINGSCREEN_H
#define LOADINGSCREEN_H

#include <QWidget>
#include <QLabel>
#include <QMovie>
#include <QVBoxLayout>

class LoadingScreen: public QWidget
{
    Q_OBJECT
public:
    LoadingScreen(QWidget *parent = nullptr);
    ~LoadingScreen();

private:
    QLabel *movieLabel;
    QMovie *movie;

};

#endif // LOADINGSCREEN_H
