import PySide
from PySide import QtGui, QtCore
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtCore import QPointF

from node import Node
from node_types import VideoTestGenNode, V4L2SourceNode, Switcher4Node, ScreenOutputNode
from graph_context_menu import GraphContextMenu

# =================================================================
# TODO THIS SHOULD SEND SIGNALS WHEN ADDING, LINKING, AND DELETEING
# =================================================================
class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        self.scene = QtGui.QGraphicsScene()

        super(GraphWidget, self).__init__(self.scene)
        self.initUI()

    def initUI(self):
        self.setSceneRect(self.rect())

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setInteractive(True)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

        self.brushes = {}
        self.brushes['background'] = QtGui.QBrush(QtGui.QColor(57,57,57), QtCore.Qt.SolidPattern)
        self.setBackgroundBrush(self.brushes['background'])

        # v1 = VideoTestGenNode('vid1')
        # self.scene.addItem(v1)

        # v2 = VideoTestGenNode('vid2')
        # v2.setPos(QPointF(0,80))
        # self.scene.addItem(v2)

        # s1 = Switcher4Node('switcher1')
        # s1.setPos(QPointF(200,0))
        # self.scene.addItem(s1)

        # out1 = ScreenOutputNode('out1')
        # out1.setPos(QPointF(400,0))
        # self.scene.addItem(out1)

        # out2 = ScreenOutputNode('out2')
        # out2.setPos(QPointF(400,80))
        # self.scene.addItem(out2)

    def resizeEvent(self, event):
        self.setSceneRect(self.rect())

    def wheelEvent(self, event):
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        scaleFactor = 1.15
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0/scaleFactor, 1.0/scaleFactor)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            items = self.scene.selectedItems()
            for item in items:
                item.delete()

    def contextMenuEvent(self, event):
        menu = GraphContextMenu(self, self.mapToScene(event.pos()))
        menu.exec_(event.globalPos())

    def addNodeFromMenu(self, nodeClass, position):
        if nodeClass == ScreenOutputNode:
            name, ok = QtGui.QInputDialog.getText(self, "Create Screen Display",
                "Name:", text=self.freeName("display"))

            if ok:
                self.addNode(ScreenOutputNode(name), position)

        if nodeClass == Switcher4Node:
            name, ok = QtGui.QInputDialog.getText(self, "Create 4-Input Switcher",
                "Name:", text=self.freeName("switcher"))

            if ok:    
                self.addNode(Switcher4Node(name), position)

        if nodeClass == VideoTestGenNode:
            name, ok = QtGui.QInputDialog.getText(self, "Create Video Test Generator",
                "Name:", text=self.freeName("videotestgen"))

            if ok:  
                self.addNode(VideoTestGenNode(name), position)

        if nodeClass == V4L2SourceNode:
            name, ok = QtGui.QInputDialog.getText(self, "Create V4L2 Source",
                "Name:", text=self.freeName("v4l2source"))

            if ok:
                self.addNode(V4L2SourceNode(name), position)                                      

    def addNode(self, node, position=QPointF(0,0)):
        node.setPos(self.mapFromScene(position))
        self.scene.addItem(node)

    def freeName(self, name):
        node_names = [item.name for item in self.scene.items() if isinstance(item, Node)]
        n = 1

        while (name + str(n)) in node_names:
            n = n+1

        return name + str(n)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    testWidget = GraphWidget()
    testWidget.show()
    testWidget.setGeometry(300, 300, 600, 600)
    sys.exit(app.exec_())