#!/usr/bin/env python2

from functools import partial

import wx

from boltzmannizer.gui.plot import PlotFrame2DByTemperature, PlotFrame3DPopulation
from boltzmannizer.gui.utils import DataPanel
from boltzmannizer.science.boltzmann_distribution import BoltzmannDistribution
from boltzmannizer.tools.misc import Reserver


class BoltzmannDistributionGUI(BoltzmannDistribution):
	"""
	BoltzmannDistribution with some GUI-specific features.
	"""

	def __init__(self, color, *args, **kwargs):
		BoltzmannDistribution.__init__(self, *args, **kwargs)

		self.color = color

	@classmethod
	def from_file(cls, color, *args, **kwargs):
		bd = BoltzmannDistribution.from_file(*args, **kwargs)

		bd.color = color

		return bd


class MainFrame(wx.Frame):
	COLORS = ['blue', 'green', 'red', 'magenta', 'black', 'cyan', 'brown']
	# Yellow is awful, but we've run out of colors at this point!
	OVERFLOW_COLOR = 'yellow'

	def __init__(self):
		wx.Frame.__init__(self, None, title='Boltzmannizer', size=(600, 400))

		self.plot_functions = {
				'Energy': self._plot_values_energy,
				'Entropy': self._plot_values_entropy,
				'Heat capacity': self._plot_values_heat_capacity,
				}

		# Colors assigned to input files.
		#
		# We want each input file to have a color that's permanently associated
		# with it, but we want to use the nicer colors as much as possible.
		self.color_reserver = Reserver(self.COLORS, self.OVERFLOW_COLOR)

		# Keep track of child frames.
		self.plot_frames_2D = {}
		self.plot_frames_3D = {}

		# Menu.
		menuBar = wx.MenuBar()

		## File.
		menu = wx.Menu()

		### Add data.
		item = menu.Append(wx.ID_OPEN, '&Add data\tCtrl+O')
		self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, item)

		menuBar.Append(menu, '&File')

		## Edit.
		menu = wx.Menu()

		#### Select all.
		item = menu.Append(wx.ID_ANY, 'Select &all\tCtrl+A')
		self.Bind(wx.EVT_MENU, self.OnMenuEditSelectAll, item)

		menu.AppendSeparator()

		#### Remove.
		item = menu.Append(wx.ID_ANY, 'Remove')
		self.Bind(wx.EVT_MENU, self.OnMenuEditRemove, item)

		menuBar.Append(menu, '&Edit')

		## Plot.
		menu = wx.Menu()

		### Energy.
		item = menu.Append(wx.ID_ANY, '&Energy\tCtrl+E')
		self.Bind(wx.EVT_MENU, self.OnMenuPlotEnergy, item)

		### Entropy.
		item = menu.Append(wx.ID_ANY, 'E&ntropy\tCtrl+N')
		self.Bind(wx.EVT_MENU, self.OnMenuPlotEntropy, item)

		### Heat capacity.
		item = menu.Append(wx.ID_ANY, '&Heat capacity\tCtrl+H')
		self.Bind(wx.EVT_MENU, self.OnMenuPlotHeatCapacity, item)

		menu.AppendSeparator()

		### Populations.
		item = menu.Append(wx.ID_ANY, '&Populations\tCtrl+P')
		self.Bind(wx.EVT_MENU, self.OnMenuPlotPopulations, item)

		menu.AppendSeparator()

		### Close all.
		item = menu.Append(wx.ID_ANY, '&Close all\tCtrl+Shift+W')
		self.Bind(wx.EVT_MENU, self.OnMenuPlotCloseAll, item)

		menuBar.Append(menu, '&Plot')

		self.SetMenuBar(menuBar)

		# Frame.
		frame_box = wx.BoxSizer(wx.VERTICAL)

		## Data panel.
		def toggle_callback(key):
			self._redraw_plots()

		def remove_callback(bd):
			# Clear the color for someone else to use.
			self.color_reserver.free(bd.color)

		columns = [
				('Filename', None),
				('Levels', 50),
				('States', 50),
				('k_B', 150),
				]

		self.dp = DataPanel(self, columns,
				check_callback=toggle_callback,
				uncheck_callback=toggle_callback,
				remove_callback=remove_callback)
		frame_box.Add(self.dp, 1, wx.EXPAND)

		self.SetSizer(frame_box)

		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnMenuFileOpen(self, evt):
		wildcard = 'JSON (*.json)|*.json|All files|*'
		dialog = wx.FileDialog(self, 'Add data', wildcard=wildcard, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.MULTIPLE)

		if dialog.ShowModal() != wx.ID_OK:
			return

		for path in dialog.GetPaths():
			self._load_data(path)

	def OnMenuEditSelectAll(self, evt):
		self.dp.select_all()

	def OnMenuEditRemove(self, evt):
		self.dp.remove_selected()

	def OnMenuPlotEnergy(self, evt):
		self._plot_values_energy(partial(self._make_plot_2D, 'Energy', 0))

	def OnMenuPlotEntropy(self, evt):
		self._plot_values_entropy(partial(self._make_plot_2D, 'Entropy', 0))

	def OnMenuPlotHeatCapacity(self, evt):
		# Avoid division by zero by skipping over the zero temperature.
		self._plot_values_heat_capacity(partial(self._make_plot_2D, 'Heat capacity', 1))

	def OnMenuPlotPopulations(self, evt):
		for i in self.dp.selected:
			bd = self.dp.objects[i]

			xlabel = 'T'
			ylabel = 'E'

			if bd.units is not None:
				xlabel += ' / ' + bd.units['temperature']

			if bd.units is not None:
				ylabel += ' / ' + bd.units['energy']

			plot_frame = PlotFrame3DPopulation('Populations: {0}'.format(bd.filename))
			plot_frame.plot_data(bd, xlabel=xlabel, ylabel=ylabel, zlabel='P')
			plot_frame.Show()

			def remove_frame():
				if self:
					try:
						del self.plot_frames_3D[id(plot_frame)]
					except KeyError:
						pass

			plot_frame.close_callback = remove_frame

			self.plot_frames_3D[id(plot_frame)] = plot_frame

	def OnMenuPlotCloseAll(self, evt):
		self._close_all_plot_frames()

	def OnClose(self, evt):
		self._close_all_plot_frames()

		evt.Skip()

	def _plot_values_energy(self, callback):
		fs = []
		bds = []

		units_energy = []
		units_temperature = []

		for i in self.dp.checked:
			bd = self.dp.objects[i]

			if bd.units is not None:
				units_energy.append(bd.units['energy'])
				units_temperature.append(bd.units['temperature'])
			else:
				units_energy.append('')
				units_temperature.append('')

			fs.append(bd.energy)
			bds.append(bd)

		units_energy = self._combine_units(units_energy)
		units_temperature = self._combine_units(units_temperature)

		if units_temperature:
			xlabel = 'T / {0}'.format(units_temperature)
		else:
			xlabel = 'T'

		if units_energy:
			ylabel = 'E / {0}'.format(units_energy)
		else:
			ylabel = 'E'

		callback(fs, bds, xlabel=xlabel, ylabel=ylabel)

	def _plot_values_entropy(self, callback):
		fs = []
		bds = []

		units_energy = []
		units_temperature = []

		for i in self.dp.checked:
			bd = self.dp.objects[i]

			if bd.units is not None:
				units_energy.append(bd.units['energy'])
				units_temperature.append(bd.units['temperature'])
			else:
				units_energy.append('')
				units_temperature.append('')

			fs.append(bd.entropy)
			bds.append(bd)

		units_energy = self._combine_units(units_energy)
		units_temperature = self._combine_units(units_temperature)

		if units_temperature:
			xlabel = 'T / {0}'.format(units_temperature)
		else:
			xlabel = 'T'

		if units_energy and units_temperature:
			ylabel = 'S / ({0} / {1})'.format(units_energy, units_temperature)
		else:
			ylabel = 'S'

		callback(fs, bds, xlabel=xlabel, ylabel=ylabel)

	def _plot_values_heat_capacity(self, callback):
		fs = []
		bds = []

		units_energy = []
		units_temperature = []

		for i in self.dp.checked:
			bd = self.dp.objects[i]

			if bd.units is not None:
				units_energy.append(bd.units['energy'])
				units_temperature.append(bd.units['temperature'])
			else:
				units_energy.append('')
				units_temperature.append('')

			fs.append(bd.heat_capacity)
			bds.append(bd)

		units_energy = self._combine_units(units_energy)
		units_temperature = self._combine_units(units_temperature)

		if units_temperature:
			xlabel = 'T / {0}'.format(units_temperature)
		else:
			xlabel = 'T'

		if units_energy and units_temperature:
			ylabel = 'Cv / ({0} / {1})'.format(units_energy, units_temperature)
		else:
			ylabel = 'Cv'

		callback(fs, bds, xlabel=xlabel, ylabel=ylabel)

	def _make_plot_2D(self, name, min_temp, *args, **kwargs):
		"""
		Make a plot window showing the given quantity.
		"""

		if name in self.plot_frames_2D:
			return

		def remove_frame():
			if self:
				try:
					del self.plot_frames_2D[name]
				except KeyError:
					pass

		plot_frame = PlotFrame2DByTemperature(name, close_callback=remove_frame, min_temp=min_temp)
		plot_frame.plot_data(*args, **kwargs)
		plot_frame.Show()

		self.plot_frames_2D[name] = plot_frame

	def _load_data(self, path):
		"""
		Add the data in the file at the given path.
		"""

		color = self.color_reserver.allocate()

		try:
			bd = BoltzmannDistributionGUI.from_file(color, path)
		except Exception as exc:
			dlg = wx.MessageDialog(None, '{0}: {1}'.format(path, exc), 'Error loading file', wx.OK|wx.ICON_EXCLAMATION)
			dlg.ShowModal()
			dlg.Destroy()

			return

		# Make k_B more presentable, with units if they exist.
		k_B = [str(bd.k_B)]

		if bd.units is not None:
			k_B.append('{0}/{1}'.format(bd.units['energy'], bd.units['temperature']))

		levels, states = bd.num_levels

		index, key = self.dp.AddRow([bd.filename, levels, states, ' '.join(k_B)], bd)

	def _redraw_plots(self):
		for name, frame in self.plot_frames_2D.items():
			self._redraw_plot(name, frame)

	def _redraw_plot(self, name, frame):
		self.plot_functions[name](frame.plot_data)

	def _combine_units(self, units):
		"""
		Given a list of units, complain if they're not all the same.

		If all the values given are the same, returns that value. If at least
		one is different, returns '???'. If no values given, returns None.

		We do this because it doesn't make sense to display some units on a
		plot if the quantities displayed don't correspond to those units.
		"""

		cur = None

		for u in units:
			if cur is None:
				cur = u
			elif cur != u:
				cur = '???'

		return cur

	def _close_all_plot_frames(self):
		for frame in self.plot_frames_2D.values():
			if frame:
				frame.Close()

		for frame in self.plot_frames_3D.values():
			if frame:
				frame.Close()


class BoltzmannizerApp(wx.App):
	def OnInit(self):
		frame = MainFrame()
		frame.Show()

		return True


if __name__ == '__main__':
	from argparse import ArgumentParser

	# Parse the arguments.
	parser = ArgumentParser(description='The Boltzmannizer.')
	parser.add_argument('--debug', dest='debug', action='store_true',
			help="don't redirect output to a special GUI window")

	args = parser.parse_args()

	redirect = 0 if args.debug else 1

	# Run the application.
	app = BoltzmannizerApp(redirect=redirect)
	app.MainLoop()
