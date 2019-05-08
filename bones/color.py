# -*- coding: utf-8 -*-
import html5
from vi.priorityqueue import editBoneSelector, viewDelegateSelector
from vi.config import conf

class ColorViewBoneDelegate( object ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( ColorViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render( self, data, field ):
		if field in data.keys():
			can = html5.Div()
			can["style"]["width"]="60px"
			adiv = html5.Div()
			adiv["style"]["width"]="10px"
			adiv["style"]["height"]="10px"
			adiv["style"]["background-Color"]=str( data[field])
			adiv["style"]["float"]="left"
			adiv["style"]["margin-top"]="6px"
			adiv["style"]["margin-right"]="3px"

			lbl = html5.Label(str( data[field]))
			can.appendChild(adiv)
			can.appendChild(lbl)
			return(can)
		return( html5.Label( conf[ "empty_value" ] ) )

class ColorEditBone( html5.Input ):

	def __init__(self, moduleName, boneName,readOnly, *args, **kwargs ):
		super( ColorEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self["type"]="color"
		if readOnly:
			self["disabled"]=True


	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return ColorEditBone(moduleName, boneName, readOnly)

	##read
	def unserialize(self, data, extendedErrorInformation=None):
		if self.boneName in data.keys():
			self._setValue(data[self.boneName])

	##save
	def serializeForPost(self):
		return { self.boneName: str(self._getValue())}

	##UNUSED
	def serializeForDocument(self):
		return self.serializeForPost()

def CheckForColorBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "color"

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForColorBone, ColorEditBone)
viewDelegateSelector.insert( 3, CheckForColorBone, ColorViewBoneDelegate)
