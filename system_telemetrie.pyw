"""
Matplotlib in QT5
Periodisches aktualisieren eines Graphen

"""
import sys
import random
import psutil
from PyQt5 import QtWidgets, QtCore, uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


def toSiBinary(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

def toSiDezimal(num, suffix="B"):
    for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1000.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1000.0
    return f"{num:.1f} Y{suffix}"


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        #fig = Figure(figsize=(width, height), dpi=dpi)
        fig = Figure(figsize=(200/dpi, 500/dpi), dpi=dpi)
        fig.tight_layout()
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class myGraph():

    def __init__(self, container):
        self.canvas = MplCanvas(self, width=5, height=4, dpi=72)

        # Dummy layout erzeugen um dort den graphen einzubetten
        lay = QtWidgets.QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.canvas)


class NetworkGraph(myGraph):

    def __init__(self, container):
        super().__init__(container)

        # leere Datenreihen erzeugen
        n_data = 120
        self.xdata = list(range(n_data))
        self.ydataIn = [0] * n_data
        self.ydataOut = [0] * n_data

        # We need to store a reference to the plotted line somewhere, so we can apply the new data to it.
        self._plot_ref_in, = self.canvas.axes.plot(self.xdata, self.ydataIn, color='green', marker='', linestyle='solid',
                                            linewidth=0.5, markersize=12)
        self._plot_ref_out, = self.canvas.axes.plot(self.xdata, self.ydataOut, color='red', marker='', linestyle='solid',
                                             linewidth=0.5, markersize=12)
        #self._plot_ref_in = None
        #self._plot_ref_out = None

        # startwerte für die übertragenen bytes
        netcounter = psutil.net_io_counters(pernic=False, nowrap=True)
        self.bytesInfirst = netcounter.bytes_recv
        self.bytesOutfirst = netcounter.bytes_sent

        # call updateGraph one time
        self.updateGraph()

    def updateGraph(self):

        #############################################################################
        # calculate values
        netcounter = psutil.net_io_counters(pernic=False, nowrap=True)
        bytesInLast = netcounter.bytes_recv
        bytesOutLast = netcounter.bytes_sent

        self.bytesIn = bytesInLast - self.bytesInfirst
        self.bytesOut = bytesOutLast - self.bytesOutfirst
        #print(bytesIn, bytesOut)

        # letzte messung wieder auf first setzen
        self.bytesInfirst = bytesInLast
        self.bytesOutfirst = bytesOutLast

        #############################################################################
        # Die Datenreihen setzen
        # Drop off the first y element
        self.ydataIn = self.ydataIn[1:]
        self.ydataOut = self.ydataOut[1:]
        # append a new one.
        #self.ydataIn.append(random.randint(0, 100))
        #self.ydataOut.append(random.randint(0, 100))
        self.ydataIn.append(self.bytesIn)
        self.ydataOut.append(self.bytesOut)

        #############################################################################
        # Die linien aktualisieren über die referenz
        #if self._plot_ref_in is None:
            #plot_ref_in = self.canvas.axes.plot(self.xdata, self.ydataIn, color='green', marker='', linestyle='solid', linewidth=0.5, markersize=12)
            #self._plot_ref_in = plot_ref_in[0]
        #else:
        self._plot_ref_in.set_ydata(self.ydataIn)

        ###
        #if self._plot_ref_out is None:
            #plot_ref_out = self.canvas.axes.plot(self.xdata, self.ydataOut, color='red', marker='', linestyle='solid', linewidth=0.5, markersize=12)
            #self._plot_ref_out = plot_ref_out[0]
        #else:
        self._plot_ref_out.set_ydata(self.ydataOut)

        #############################################################################
        # Einstellungen für den Graph
        self.canvas.axes.set_title('Network', fontsize='small', loc='center')
        # self.canvas.axes.set_xlabel('time (s)')
        #self.canvas.axes.set_ylabel('%')
        self.canvas.axes.get_xaxis().set_visible(False)
        #self.canvas.axes.get_yaxis().set_visible(False)
        self.canvas.axes.tick_params(axis='y', colors='white') # y-achsen beschriftung auf weiß setzen damit man sie nicht sieht. dadurch bleibt das grid erhalten
        maxValues = [max(self.ydataIn), max(self.ydataOut),10]
        #print(max(maxValues), max(self.ydataIn), max(self.ydataOut))
        self.canvas.axes.set_ylim(0, max(maxValues))
        self.canvas.axes.grid(True, linestyle='dashed')
        self.canvas.axes.legend(['Download', 'Upload'])

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


class CpuGraph(myGraph):

    def __init__(self, container):
        super().__init__(container)

        # leere Datenreihen erzeugen
        n_data = 120
        self.xdata = list(range(n_data))
        self.ydata = [0] * n_data

        # We need to store a reference to the plotted line somewhere, so we can apply the new data to it.
        self._plot_ref, = self.canvas.axes.plot(self.xdata, self.ydata, color='blue', marker='', linestyle='solid', linewidth=0.5, markersize=12)

        # call updateGraph one time
        self.updateGraph()

    def updateGraph(self):
        # Auslastung der CPU holen
        self.cpuPercent = psutil.cpu_percent(interval=None,percpu=False)
        #print(self.cpuPercent)

        # Die Daten setzen
        self.ydata = self.ydata[1:]  # Drop off the first y element
        self.ydata.append(self.cpuPercent)  # append a new one.

        # We have a reference, we can use it to update the data for that line.
        self._plot_ref.set_ydata(self.ydata)

        # Einstellungen für den Graph
        self.canvas.axes.set_title('CPU %', fontsize='small', loc='center')
        #self.canvas.axes.set_xlabel('time (s)')
        #self.canvas.axes.set_ylabel('%')
        self.canvas.axes.get_xaxis().set_visible(False)
        self.canvas.axes.set_ylim(0, 105)
        self.canvas.axes.grid(True, linestyle='dashed')

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/system_telemetrie.ui', self)

        #
        self.cpuGraph = CpuGraph(self.ContainerCpu)
        #self.cpuGraph = CpuGraph(self.TestWidget)
        self.networkGraph = NetworkGraph(self.ContainerNetwork)

        self.statusbar.showMessage("2023 © by Thomas Eses")


        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_half_second)
        self.timer.start()

        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(1000)
        self.timer2.timeout.connect(self.update_per_second)
        self.timer2.start()


    def update_half_second(self):
        self.cpuGraph.updateGraph()


    def update_per_second(self):
        # update CPU label
        cpuFrequenz = psutil.cpu_freq(percpu=False)
        self.labelCpu.setText(str(self.cpuGraph.cpuPercent) + "%   " + str(cpuFrequenz.current) + " MHz")

        # update Network
        self.networkGraph.updateGraph()

        # update Network Label
        bo = self.networkGraph.bytesOut
        self.labelUploadValue.setText(toSiBinary(bo) + "/s")
        self.labelUploadValueDez.setText(toSiDezimal(bo) + "/s")
        self.labelUploadValueBitDez.setText(toSiDezimal(bo * 8, "Bit") + "/s")
        #
        bi = self.networkGraph.bytesIn
        self.labelDownloadValue.setText(toSiBinary(bi) + "/s")
        self.labelDownloadValueDez.setText(toSiDezimal(bi) + "/s")
        self.labelDownloadValueBitDez.setText(toSiDezimal(bi * 8, "Bit") + "/s")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
sys.exit(app.exec_())


