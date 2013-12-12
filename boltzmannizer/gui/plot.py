from __future__ import division

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.cm import jet
from matplotlib.collections import PolyCollection
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas

# Allows us to use the 3D projection.
from mpl_toolkits.mplot3d import Axes3D

import numpy as N

import wx
from wx.lib.intctrl import IntCtrl


class PlotPanel2DByTemperature(wx.Panel):
	DEFAULT_MIN_TEMP = 0
	DEFAULT_MAX_TEMP = 2000
	NUM_TEMPS = 200

	def __init__(self, parent, min_temp=None):
		wx.Panel.__init__(self, parent)

		self.min_temp = min_temp if min_temp is not None else self.DEFAULT_MIN_TEMP
		self.max_temp = self.DEFAULT_MAX_TEMP

		self.data_cache = None

		# Panel.
		panel_box = wx.BoxSizer(wx.VERTICAL)

		## Canvas.
		self.figure = Figure()
		self.canvas = Canvas(self, -1, self.figure)
		self.axes = None
		panel_box.Add(self.canvas, 1, wx.EXPAND)

		self.SetSizer(panel_box)

	def plot_data(self, fs, bds, xlabel=None, ylabel=None):
		self.data_cache = {
				'fs': fs,
				'bds': bds,
				'xlabel': xlabel,
				'ylabel': ylabel,
				}

		if self.axes is not None:
			self.figure.delaxes(self.axes)
			self.axes = None

		self.axes = self.figure.add_subplot(111)

		if xlabel is not None:
			self.axes.set_xlabel(xlabel)

		if ylabel is not None:
			self.axes.set_ylabel(ylabel)

		do_legend = False

		for f, bd in zip(fs, bds):
			label, color = bd.filename, bd.color

			if not do_legend and label is not None:
				do_legend = True

			xs = self._gen_temps()
			ys = [f(x) for x in xs]

			self.axes.plot(xs, ys, label=label, color=color)

		if do_legend:
			# Put the legend in the top-right corner, outside the axes.
			self.axes.legend(bbox_to_anchor=(0, 0, 1, 1), bbox_transform=self.figure.transFigure)

		self.figure.tight_layout()
		self.canvas.draw()

	def plot_cached_data(self):
		dc = self.data_cache

		if dc is None:
			return

		self.plot_data(dc['fs'], dc['bds'], xlabel=dc['xlabel'], ylabel=dc['ylabel'])

	def set_max_temp(self, temp):
		self.max_temp = temp

		self.plot_cached_data()

	def _gen_temps(self):
		return N.linspace(self.min_temp, self.max_temp, self.NUM_TEMPS)


class PlotFrame2DByTemperature(wx.Frame):
	"""
	Frame for plotting Boltzmann distribution properties as functions of
	temperature in 2D.
	"""

	def __init__(self, name, close_callback=None, min_temp=None):
		wx.Frame.__init__(self, None, title=name, size=(600, 400))

		self.close_callback = close_callback

		# Frame.
		frame_box = wx.BoxSizer(wx.VERTICAL)

		## Plot.
		self.panel = PlotPanel2DByTemperature(self, min_temp=min_temp)
		frame_box.Add(self.panel, 1, wx.EXPAND)

		## Controls.
		control_box = wx.BoxSizer(wx.HORIZONTAL)

		### Temperature.
		temperature_box = wx.BoxSizer(wx.HORIZONTAL)

		temperature_label = wx.StaticText(self, label='Maximum temperature: ')
		temperature_box.Add(temperature_label)

		self.temperature_input = IntCtrl(self, value=self.panel.max_temp, min=self.panel.min_temp + 1, style=wx.TE_PROCESS_ENTER)
		temperature_box.Add(self.temperature_input)

		temperature_button = wx.Button(self, label='Set')
		temperature_box.Add(temperature_button)

		control_box.Add(temperature_box)

		frame_box.Add(control_box)

		self.SetSizerAndFit(frame_box)

		self.Bind(wx.EVT_TEXT_ENTER, self.OnSetTemperature, self.temperature_input)
		self.Bind(wx.EVT_BUTTON, self.OnSetTemperature, temperature_button)

		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		if self.close_callback is not None:
			self.close_callback()

		evt.Skip()

	def OnSetTemperature(self, evt):
		try:
			temp = int(self.temperature_input.Value)
		except ValueError:
			# Ignore malformed input.
			return

		if temp < self.panel.min_temp + 1:
			# Only allow reasonable temperatures.
			return

		self.panel.set_max_temp(temp)

	def plot_data(self, *args, **kwargs):
		self.panel.plot_data(*args, **kwargs)


class PlotPanel3DPopulation(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		# Panel.
		panel_box = wx.BoxSizer(wx.VERTICAL)

		## Canvas.
		self.figure = Figure()
		self.canvas = Canvas(self, -1, self.figure)
		self.axes = None
		panel_box.Add(self.canvas, 1, wx.EXPAND)

		self.SetSizer(panel_box)

	def plot_data(self, bd, cm=jet, xlabel=None, ylabel=None, zlabel=None):
		"""
		Plot energy level populations by temperature in 3D.

		bd: BoltzmannDistribution.
		cm: A matplotlib colormap.
		*label: Axis labels.
		"""

		if self.axes is not None:
			self.figure.delaxes(self.axes)
			self.axes = None

		self.axes = self.figure.gca(projection='3d')

		# Set up the data.
		xs = self._gen_temps()
		ys = bd.energies
		verts = []

		# All the energy level populations at all the temperatures.
		populations = N.column_stack(bd.ps(x) for x in xs)

		for p in populations:
			# Add the points on the ends so that there is a bottom edge along
			# the polygon.
			points = [(xs[0], 0)] + list(zip(xs, p)) + [(xs[-1], 0)]
			verts.append(points)

		x_min, x_max = min(xs), max(xs)
		y_min, y_max = min(ys), max(ys)

		if y_max == y_min:
			colors = [cm(0.0) for i in bd.levels]
		else:
			colors = [cm((ys[i] - y_min) / (y_max - y_min)) for i in bd.levels]

		poly = PolyCollection(verts, facecolors=colors, linewidth=1.0, edgecolor='white')
		poly.set_alpha(0.7)

		# The directions here look somewhat confused, but that's just due to
		# the way the polygons are stacked.
		self.axes.add_collection3d(poly, zs=ys, zdir='y')

		if x_max == x_min:
			self.axes.set_xlim3d(x_min - 1, x_max + 1)
		else:
			self.axes.set_xlim3d(x_min, x_max)

		if y_max == y_min:
			self.axes.set_ylim3d(y_min - 1, y_max + 1)
		else:
			self.axes.set_ylim3d(y_min, y_max)

		self.axes.set_zlim3d(0, 1)

		if xlabel is not None:
			self.axes.set_xlabel(xlabel)

		if ylabel is not None:
			self.axes.set_ylabel(ylabel)

		if zlabel is not None:
			self.axes.set_zlabel(zlabel)

		self.figure.tight_layout()

		# Make sure that we redraw as the user drags.
		#
		# Using a list because we don't have nonlocal here.
		mouse_down = [False]

		def on_press(evt):
			mouse_down[0] = True

		def on_move(evt):
			if mouse_down[0]:
				self.canvas.draw()

		def on_release(evt):
			mouse_down[0] = False

		cid = self.canvas.mpl_connect('button_press_event', on_press)
		cid = self.canvas.mpl_connect('motion_notify_event', on_move)
		cid = self.canvas.mpl_connect('button_release_event', on_release)

	def _gen_temps(self):
		return N.linspace(0, 2000, 200)


class PlotFrame3DPopulation(wx.Frame):
	"""
	Frame for plotting Boltzmann distribution populations in 3D.
	"""

	def __init__(self, name, close_callback=None):
		wx.Frame.__init__(self, None, title=name, size=(600, 400))

		self.close_callback = close_callback

		# Frame.
		frame_box = wx.BoxSizer(wx.VERTICAL)

		self.panel = PlotPanel3DPopulation(self)
		frame_box.Add(self.panel, 1, wx.EXPAND)

		self.SetSizerAndFit(frame_box)

		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		if self.close_callback is not None:
			self.close_callback()

		evt.Skip()

	def plot_data(self, *args, **kwargs):
		self.panel.plot_data(*args, **kwargs)
