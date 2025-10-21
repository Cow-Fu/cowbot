import QtQuick
import Qt.labs.platform

Window {
  id: main
  width: 200
  height: 200
  color: "green"
  visible: true

  Text {
    text: "Hello World"
  }
  SystemTrayIcon {
    visible: true

    onActivated: {
      main.show()
      main.raise()
      main.requestActivate()
    }

    menu: Menu {
      MenuItem {
        text: qsTr("Quit")
        onTriggered: Qt.quit()
      }
    }
  }
}
