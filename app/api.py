import configparser
import time
import os
import networkx as nx

from app.lib.convertXlsToCSV import convertXlsToCSV

from app.lib.parser import getGraphFromCSV

from app.lib.tools import genPosNodes
from app.lib.tools import makeSubGraphByMetrics
from app.lib.tools import makeCategorySubGraph

from app.lib.draw import drawGraph

from app.lib.minSetCover import correctnessMGM
from app.lib.minSetCover import MGMminSetCover
from app.lib.minSetCover import minSetCovByINPUT
from app.lib.minSetCover import minSetCovBySOURCE
from app.lib.minSetCover import maxSetCovByATTR
from app.lib.minSetCover import minCapacitySetCover


class MGM():
	def __init__(self,config):
		try:
			self.config = configparser.ConfigParser()
			self.config.read(config)
			self.projectPath    =   self.config['PROJECT']['projectPath']
			self.projectName	=	self.config['PROJECT']['projectName']
			self.pathDbFiles    =   self.projectPath+self.config['DB']['pathDbFiles']
			self.xlsDbPathFile	=	self.pathDbFiles+self.config['DB']['xlsFileName']
			self.sheetNames		=	self.config['DB']['sheetsName'].split(',')

			#Tested and ok
			self.generateCsvFromDB()

			self.fileNodes		=	[self.pathDbFiles+a for a in self.config['GRAPH']['nodeNames'].split(',')]
			self.fileEdges		=	[self.pathDbFiles+a for a in self.config['GRAPH']['edgeNames'].split(',')]
			self.fileGraphName	=	self.projectPath+self.projectName+'.graphml'
			
			#Tested and ok
			self.G = self.getGraphFromCSV()

			#Gen pos of nodes
			self.delta			=	[int(x) for x in self.config['GRAPH']['delta'].split(',')]
			self.position		=	[int(x) for x in self.config['GRAPH']['position'].split(',')]
			self.postionOfNodes	=	self.genPosNodes()

			self.outputPath 	=	self.projectPath+'output/'
			os.makedirs(self.outputPath, exist_ok = True)

			
			self.outputFigGraph	=	self.outputPath+self.projectName+'-Main_Color.pdf'
			drawGraph(self.G, self.outputFigGraph, self.postionOfNodes, self.config, catColor=True)

			self.G_c	=	self.correctnessMGM(self.G,self.outputPath+self.projectName+'-CORRECT.pdf')

		except Exception as e:
			print(e)
			return None
	
	def generateCsvFromDB(self):
		try:
			convertXlsToCSV(self.sheetNames,self.xlsDbPathFile,self.pathDbFiles)
			return '200'
		except Exception as e:
			print(e)
			return 'error'
	
	
	def getGraphFromCSV(self):
		try:
			return getGraphFromCSV(self.fileNodes,self.fileEdges,self.fileGraphName)
		except Exception as e:
			print(e)
			return 'error'

	def genPosNodes(self):
		try:
			return genPosNodes(self.G, self.delta, self.position)
		except Exception as e:
			print(e)
			return 'error'
	
	def correctnessMGM(self,G,outputFile):
		try:
			return correctnessMGM(G, outputFile,self.postionOfNodes,self.config)
		except Exception as e:
			print(e)
			return 'error'

	def minSetCover(self,G):
		try:
			return MGMminSetCover(G, self.outputPath+self.projectName+'-minSetCov.pdf',self.postionOfNodes,self.config)
		except Exception as e:
			print(e)
			return 'error'
	
	def minSetCoverByMetric(self,G,metrics):
		try:
			subGraph    =   self.correctnessMGM(makeSubGraphByMetrics(G,metrics), self.outputPath+self.projectName+'-minSetCovByMetric.pdf')
			return MGMminSetCover(subGraph, self.outputPath+self.projectName+'-minSetCovByMetric.pdf',self.postionOfNodes,self.config)
		except Exception as e:
			print(e)
			return 'error'
	
	def minSetCoverByCategory(self,G,category):
		try:
			subGraph    =   self.correctnessMGM(makeCategorySubGraph(G,category), self.outputPath+self.projectName+'-minSetCovByCategory.pdf')
			return MGMminSetCover(subGraph, self.outputPath+self.projectName+'-minSetCovByCategory.pdf',self.postionOfNodes,self.config)
		except Exception as e:
			print(e)
			return 'error'
	
	def minSetCoverByInput(self,G,inputs):
		try:
			minSetCovByINPUT(G, inputs, self.outputPath+self.projectName+'-minSetCovByInputs.pdf',self.postionOfNodes,self.config)
			return 'ok'
		except Exception as e:
			print(e)
			return 'error'

	def minSetCoverBySource(self,G,sources):
		try:
			minSetCovBySOURCE(G, sources, self.outputPath+self.projectName+'-minSetCovBySources.pdf',self.postionOfNodes,self.config)
			return 'ok'
		except Exception as e:
			print(e)
			return 'error'
	
	def maxSetCovByAttributeOnEdge(self,G,maxValue,attr='weight'):
		try:
			maxSetCovByATTR(G,self.outputPath+self.projectName+'-minSetCovByAttributeOnEdge.pdf',maxValue,attr,self.postionOfNodes,self.config)
			return 'ok'
		except Exception as e:
			print(e)
			return 'error'
	
	def minCapacitySetCover(self,G):
		try:
			minCapacitySetCover(G,self.outputPath+self.projectName+'-minCapacitySetCover.pdf',self.postionOfNodes,self.config)
			return 'ok'
		except Exception as e:
			print(e)
			return 'error'