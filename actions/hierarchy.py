# -*- coding: utf-8 -*-
from flare import html5

from vi.config import conf
from vi.i18n import translate
from flare.network import NetworkService
from vi.pane import Pane
from vi.priorityqueue import actionDelegateSelector
from vi.widgets.edit import EditWidget
from flare.button import Button


class AddAction(Button):
	"""
		Adds a new node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__( translate("Add"), icon="icons-add", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--primary"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		pane = Pane(translate("Add"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_hierarchy", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		node = self.parent().parent().currentKey
		if not node:
			node = self.parent().parent().rootNode

		edwg = EditWidget(self.parent().parent().module, EditWidget.appHierarchy,
						  	skelType = "node",
		                    node=node,
		                    context=self.parent().parent().context)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction(Button):
	"""
		Edits a node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( translate("Edit"), icon="icons-edit", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--edit"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(EditAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )
		self.parent().parent().selectionActivatedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		self.parent().parent().selectionActivatedEvent.unregister( self )
		super(EditAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if len( selection ) > 0:
			if self.isDisabled:
				self.isDisabled = False
			self[ "disabled" ] = False
		else:
			if not self.isDisabled:
				self[ "disabled" ] = True
				self.isDisabled = True

	def onSelectionActivated(self, table, selection):
		if len(selection)>0:
			self.openEditor(selection[0].data["key"])

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="edit"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		selection = self.parent().parent().selection
		if not selection:
			return

		for s in selection:
			self.openEditor( s.data["key"] )

	def openEditor(self, key):
		pane = Pane(translate("Edit"), closeable=True)
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget(self.parent().parent().module,
						  EditWidget.appHierarchy,
						  skelType="node",
						  key=key,
		                  context=self.parent().parent().context)
		pane.addWidget( edwg )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )

class CloneAction(Button):
	"""
		Allows cloning an entry (including its subentries) in a hierarchy application.
	"""

	def __init__(self, *args, **kwargs):
		super( CloneAction, self ).__init__( translate("Clone"), icon="icons-clone", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--clone"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(CloneAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(CloneAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if selection:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="clone"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "clone" in conf["modules"][module]["disabledFunctions"]
		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().selection
		if not selection:
			return

		for s in selection:
			self.openEditor( s.data[ "key" ] )

	def openEditor(self, key):
		pane = Pane(translate("Clone"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_hierarchy", "action_edit" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appHierarchy,
		                  node=self.parent().parent().rootNode, key=key,skelType="node",
		                    context=self.parent().parent().context,
		                    clone=True)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, CloneAction.isSuitableFor, CloneAction )


class DeleteAction(Button):
	"""
		Deletes a node from a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( translate("Delete"), icon="icons-delete", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--delete"
		self["disabled"]= True
		self.isDisabled = True

	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if selection:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True


	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="delete"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-delete" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "delete" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		selection = self.parent().parent().selection
		if not selection:
			return
		d = Confirm(translate("Delete {amt} Entries?",amt=len(selection)) ,title=translate("Delete them?"), yesCallback=self.doDelete, yesLabel=translate("Delete"), noLabel=translate("Keep") )
		d.deleteList = [x.data[ "key" ] for x in selection]
		d.addClass( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			NetworkService.request( self.parent().parent().module, "delete", {"key": x, "skelType":"node"}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ReloadAction(Button):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( translate("Reload"), icon="icons-reload", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--reload"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="reload"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		self.addClass("is-loading")
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class SelectRootNode(html5.Select):
	"""
		Selector for hierarchy root nodes.
	"""
	def __init__(self, module, handler, actionName, *args, **kwargs):
		super( SelectRootNode, self ).__init__( *args, **kwargs )
		self.addClass("select", "select--small", "bar-item")
		self.sinkEvent("onChange")
		self.hide()

	def onAttach(self):
		super(SelectRootNode, self).onAttach()
		self.parent().parent().rootNodeChangedEvent.register(self)

		if self.parent().parent().rootNode is None:
			self.update()

	def onDetach(self):
		self.parent().parent().rootNodeChangedEvent.unregister(self)
		super(SelectRootNode, self).onDetach()

	def update(self):
		self.removeAllChildren()
		NetworkService.request(self.parent().parent().module, "listRootNodes",
		                        successHandler=self.onRootNodesAvailable)

	def onRootNodeChanged(self, newNode):
		for option in self._children:
			if option["value"] == newNode:
				option["selected"] = True
				return

	def onRootNodesAvailable(self, req):
		res = NetworkService.decode(req)

		for node in res:
			option = html5.Option()
			option["value"] = node["key"]
			option.appendChild(node["name"])

			if node["key"] == self.parent().parent().rootNode:
				option["selected"] = True

			self.appendChild(option)

		if len(self.children()) > 1:
			self.show()
		else:
			self.hide()

	def onChange(self, event):
		newRootNode = self["options"].item(self["selectedIndex"]).value
		self.parent().parent().setRootNode(newRootNode)

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName == "selectrootnode" and (handler == "hierarchy" or handler.startswith("hierarchy."))

actionDelegateSelector.insert( 1, SelectRootNode.isSuitableFor, SelectRootNode )


class ListViewAction(Button):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ListViewAction, self ).__init__( translate("ListViewAction"), icon="icons-list", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--list"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="listview"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		#self.addClass("is-loading")
		self.parent().parent().toggleListView()

	def resetLoadingState(self):
		pass
		#if self.hasClass("is-loading"):
		#	self.removeClass("is-loading")

actionDelegateSelector.insert( 1, ListViewAction.isSuitableFor, ListViewAction )
