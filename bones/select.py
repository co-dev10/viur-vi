# -*- coding: utf-8 -*-
from vi import html5
from vi.config import conf
from vi.priorityqueue import boneSelector

from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget


class SelectMultipleEditWidget(BaseEditWidget):
	style = ["vi-value-container", "option-group"]

	# language=HTML
	entryTemplate = html5.parseHTML("""
		<label class="check">
			<input type="checkbox" class="check-input" name="{{key}}">
			<span class="check-label">{{value}}</span>
		</label>
	""")

	def createWidget(self):
		for key, value in self.bone.boneStructure["values"]:
			self.appendChild(
				self.entryTemplate,
				key=key,
				value=value
			)

	def updateWidget(self):
		if self.bone.readonly:
			self.disable()
		else:
			self.enable()

		# fixme: required?

	def unserialize(self, value=None):
		if value is None:
			value = []

		for entry in self.children():
			check = entry.children(0)
			check["checked"] = check["name"] in value

	def serialize(self):
		value = []

		for entry in self.children():
			if entry.children(0)["checked"]:
				value.append(entry.children(0)["name"])

		return value


class SelectSingleEditWidget(BaseEditWidget):
	# language=HTML
	entryTemplate = html5.parseHTML("""
		<option value="{{key}}">{{value}}</option>
	""")

	def createWidget(self):
		widget = html5.Select()
		widget.addClass("select")

		# Add empty entry to allow "select nothing"
		first = widget.appendChild(
			self.entryTemplate,
			key="",
			value=conf["emptyValue"]
		)[0]

		# Make this first entry disabled when required
		if self.bone.required:
			first.disable()

		# Create entries for key+value pairs
		for key, value in self.bone.boneStructure["values"]:
			widget.appendChild(
				self.entryTemplate,
				key=key,
				value=value
			)

		return widget

	def updateWidget(self):
		if self.bone.readonly:
			self.widget.disable()
		else:
			self.widget.enable()

		# fixme: required?

	def unserialize(self, value=None):
		for entry in self.widget.children():
			if entry["value"] == str(value) or "":
				entry["selected"] = True
				return

		# If no match found, select first entry
		first = self.widget.children(0)
		if first:
			first["selected"] = True

	def serialize(self):
		for entry in self.widget.children():
			if entry["selected"]:
				return entry["value"]

		return None


class SelectViewWidget(BaseViewWidget):

	def unserialize(self, value=None):
		self.value = value
		self.appendChild(
			html5.TextNode(self.bone.valuesDict.get(value, value) if value else conf["emptyValue"]),
			replace=True
		)


class SelectMultipleBone(BaseBone):
	editWidgetFactory = SelectMultipleEditWidget
	multiEditWidgetFactory = None
	viewWidgetFactory = SelectViewWidget

	"""
	Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure):
		super().__init__(moduleName, boneName, skelStructure)
		self.valuesDict = {k: v for k, v in self.boneStructure["values"]}  #fixme this could be obsolete when core renders dict...

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return (skelStructure[boneName]["type"] == "select" or skelStructure[boneName]["type"].startswith("select.")) \
				and skelStructure[boneName].get("multiple")


boneSelector.insert(1, SelectMultipleBone.checkFor, SelectMultipleBone)


class SelectSingleBone(SelectMultipleBone):
	editWidgetFactory = SelectSingleEditWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return (skelStructure[boneName]["type"] == "select" or skelStructure[boneName]["type"].startswith("select.")) \
				and not skelStructure[boneName].get("multiple")


boneSelector.insert(1, SelectSingleBone.checkFor, SelectSingleBone)