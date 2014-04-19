from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks, returnValue

class SQIP_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(SQIP_GUI, self).__init__(parent)
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.clients.connection import connection
        cxn = connection()
        yield cxn.connect()
        self.create_layout(cxn)
    
    def create_layout(self, cxn):
        optics_widget = self.makeOpticsWidget(reactor, cxn)
        voltage_widget = self.makeVoltageWidget(reactor, cxn)
        histogram = self.make_histogram_widget(reactor, cxn)
        drift_tracker = self.make_drift_tracker_widget(reactor, cxn)
        script_scanner = self.make_script_scanner_widget(reactor, cxn)
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(optics_widget,'&Optics')
        self.tabWidget.addTab(voltage_widget,'&Electrode Voltages')
        self.tabWidget.addTab(histogram, '&Readout Histogram')
        self.tabWidget.addTab(drift_tracker, '&SD Drift Tracker')
        self.tabWidget.addTab(script_scanner, '&Script Scanner')
        self.createGrapherTab()
        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        
    def make_script_scanner_widget(self, reactor, cxn):
        from common.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        widget = script_scanner_gui(reactor, cxn)
        return widget
        
    
    def make_drift_tracker_widget(self, reactor, cxn):
        from common.clients.drift_tracker.drift_tracker import drift_tracker
        widget = drift_tracker(reactor, cxn)
        return widget
    
    def make_histogram_widget(self, reactor, cxn):
        from common.clients.readout_histogram import readout_histogram
        widget = readout_histogram(reactor, cxn)
        return widget
    
    def makeTranslationStageWidget(self, reactor):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        widget.setLayout(gridLayout)
        return widget
    
    def makeOpticsWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        #from common.clients.DAC_CONTROL import DAC_Control as voltageWidget
        from common.clients.CAVITY_CONTROL import cavityWidget
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        from common.clients.PMT_CONTROL import pmtWidget
        from common.clients.SWITCH_CONTROL import switchWidget
        from common.clients.DDS_CONTROL import DDS_CONTROL
        from common.clients.LINETRIGGER_CONTROL import linetriggerWidget
        gridLayout = QtGui.QGridLayout()
        #gridLayout.addWidget(voltageWidget(reactor),            0,0,1,1)
        gridLayout.addWidget(cavityWidget(reactor),             0,0,1,1)#0,1,3,2)
        gridLayout.addWidget(multiplexerWidget(reactor),        0,1,3,2)#0,3,3,1)
        gridLayout.addWidget(switchWidget(reactor, cxn),        3,0,1,1)
        gridLayout.addWidget(pmtWidget(reactor),                0,3,3,1)#3,1,1,1)
        gridLayout.addWidget(linetriggerWidget(reactor, cxn),   3,3,1,1)#3,2,1,1)
        gridLayout.addWidget(DDS_CONTROL(reactor, cxn),         3,1,1,1)#3,3,1,1)
        widget.setLayout(gridLayout)
        return widget
    
    def makeVoltageWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.clients.DAC_CONTROL import DAC_Control as voltageWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(voltageWidget(reactor),        0,0,1,1)
        widget.setLayout(gridLayout)
        return widget
    
    @inlineCallbacks
    def createGrapherTab(self):
        grapher = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapher, '&Grapher')
    
    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)


    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import common.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    sqipGUI = SQIP_GUI(reactor)
    sqipGUI.setWindowTitle('Sqip GUI')
    sqipGUI.show()
    reactor.run()