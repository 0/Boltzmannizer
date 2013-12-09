from itertools import count
import sys

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	"""
	ListCtrl with checkboxes.
	"""

	def __init__(self, parent, resize_column=None, check_callback=None):
		wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

		if resize_column is not None:
			self.setResizeColumn(resize_column)

		self.check_callback = check_callback

	def OnCheckItem(self, index, flag):
		if self.check_callback is not None:
			self.check_callback(self, index, flag)


class DataPanel(wx.Panel):
	"""
	Panel containing some data displayed using a CheckListCtrl.
	"""

	def __init__(self, parent, columns, check_callback=None, uncheck_callback=None, remove_callback=None):
		wx.Panel.__init__(self, parent)

		self.check_callback = check_callback
		self.uncheck_callback = uncheck_callback
		self.remove_callback = remove_callback

		self._incrementor = count()

		# Keeping track of which rows are checked.
		#
		# Keys are keys (Not a tautology!); values don't matter.
		self._checked = {}

		# Mapping from arbitrary keys to row objects.
		self.objects = {}

		# Panel.
		panel_box = wx.BoxSizer()

		## Check list.
		self.lst = CheckListCtrl(self, resize_column=1, check_callback=self.OnCheckItem)
		panel_box.Add(self.lst, 1, wx.EXPAND)

		self.SetSizer(panel_box)

		for i, c in enumerate(columns):
			label, width = c

			if width is not None:
				self.lst.InsertColumn(i, label, width=width)
			else:
				self.lst.InsertColumn(i, label)

		self.Bind(wx.EVT_LIST_KEY_DOWN, self.OnListKeyDown, self.lst)

	@property
	def checked(self):
		"""
		Keys of the checked rows.
		"""

		return sorted(self._checked)

	@property
	def selected(self):
		"""
		Keys of the selected rows.
		"""

		cur = self.lst.GetFirstSelected()

		while cur >= 0:
			yield self.lst.GetItemData(cur)

			cur = self.lst.GetNextSelected(cur)

	def AddRow(self, data, obj):
		"""
		Add a row containing the values in data and store obj as being
		associated with the row.
		"""

		index = self.lst.InsertStringItem(sys.maxint, str(data[0]))

		for i, d in enumerate(data[1:], start=1):
			self.lst.SetStringItem(index, i, str(d))

		key = self._next_key()
		self.objects[key] = obj
		self.lst.SetItemData(index, key)

		# Start out checked.
		self.lst.CheckItem(index)

		return index, key

	def RemoveRow(self, index):
		"""
		Remove a row.
		"""

		self.lst.CheckItem(index, check=False)

		key = self.lst.GetItemData(index)
		obj = self.objects[key]

		try:
			del self.objects[key]
		except KeyError:
			pass

		self.lst.DeleteItem(index)

		if self.remove_callback is not None:
			self.remove_callback(obj)

	def OnCheckItem(self, lst, index, flag):
		key = lst.GetItemData(index)

		if flag:
			self._checked[key] = True

			if self.check_callback is not None:
				self.check_callback(key)
		else:
			try:
				del self._checked[key]
			except KeyError:
				pass
			else:
				if self.uncheck_callback is not None:
					self.uncheck_callback(key)

	def OnListKeyDown(self, evt):
		key = evt.GetKeyCode()

		if key == wx.WXK_DELETE:
			self.remove_selected()

	def select_all(self):
		for i in xrange(self.lst.GetItemCount()):
			self.lst.Select(i)

	def remove_selected(self):
		sel = self.lst.GetFirstSelected()

		while sel >= 0:
			self.RemoveRow(sel)

			sel = self.lst.GetFirstSelected()

	def _next_key(self):
		"""
		Generate a unique key.
		"""

		return next(self._incrementor)
