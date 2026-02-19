import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 600
    height: 500
    title: "Clock"
    flags: Qt.FramelessWindowHint | Qt.Window
    property string currTime: "00:00:00"
    property QtObject backend

    Rectangle {
        anchors.fill: parent

        Image {
            anchors.fill: parent
            source: "../images/background.webp"
            fillMode: Image.PreserveAspectCrop
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"

            Text {
                text: currTime
                font.pixelSize: 24
                color: "white"
                anchors {
                    bottom: parent.bottom
                    bottomMargin: 12
                    left: parent.left
                    leftMargin: 12
                }
            }
        }
    }

    Connections {
        target: backend

        function onUpdated(msg) {
            currTime = msg
        }
    }
}
