import networkx as nx
import csv

from lib.draw import drawGraph


#create X from edge to respect the paper S is a subSet of X
def makeXForAlgo(listoOfNodes,Graph):
	X = []
	for node in listoOfNodes:
		#uso > 0 di zero perché devo prendermi solo le metriche 
		# da cui parte almeno 1 arco
		if len(Graph.out_edges(node)) > 0:
			X.append(node)

	return set(X)

#create S
def makeSForAlgo(listoOfNodes,Graph):
	S = []
	for node in listoOfNodes:
		tmpList = []
		for el in Graph.in_edges(node):
			tmpList.append(el[0])
		S.append(tmpList)
	return S

def greedyMinSetCover(X,S):
	I = set({})
	while X != set():
		valMax = 0
		index = 0
		for s in S:
			d = len(set(s).intersection(X))
			if d > valMax:
				valMax = d
				index = S.index(s)
		
		#print(valMax,index)
	
		I = I.union(set({index}))
		X = X.difference(set(S[index]))
		
	return I

def exeMinSetCoverV1(MGM):
	listOfMetrics = []
	listOfClusters = []
	listOfInputs = []

	for node in MGM.nodes():
		if 'M' in node:
			listOfMetrics.append(node)
		elif 'CL' in node:
			listOfClusters.append(node)
		elif 'I' in node:
			listOfInputs.append(node)
	
	subMGM = MGM.subgraph(listOfMetrics+listOfClusters)
   
	#SICCOME POSSO AVERE METRICHE CHE NON SONO COLLEGATE A NULLA
	#PRENDO SOLO LE METRICHE CON UN ARCO USCENTE
	#PERCIò creo X e S

	S = makeSForAlgo(listOfClusters,subMGM)
	X = makeXForAlgo(listOfMetrics,subMGM)
	
	I = greedyMinSetCover(X, S)

	listOfCovCluster = [listOfClusters[el] for el in I]

	print('[V1] MIN CLUSTERS COV: {}'.format(len(listOfCovCluster)), '\t/\tALL CLASTERS: {}'.format(len(listOfClusters)))

	eff = (len(listOfCovCluster)/len(listOfClusters))*100

	#print('Col {}% di cluster riesco a coprire il 100% di metriche che hanno almeno un arco uscente '.format(str(eff)))
	
	covGraph_v1 = MGM.subgraph(listOfMetrics+listOfCovCluster)

	return listOfCovCluster,covGraph_v1

def exeMinSetCoverV2(MGM,listOfCovCluster):
	listOfMetrics = []
	listOfClusters = []
	listOfInputs = []

	for node in MGM.nodes():
		if 'M' in node:
			listOfMetrics.append(node)
		elif 'CL' in node:
			listOfClusters.append(node)
		elif 'I' in node:
			listOfInputs.append(node)
	
	subMGM = MGM.subgraph(listOfMetrics+listOfCovCluster+listOfInputs)

	
	listOfCovInput = []
	for covCluster in listOfCovCluster:
		for el in subMGM.out_edges(covCluster):
			listOfCovInput.append(el[1])
	
	listOfCovInput    =   list(set(listOfCovInput))

	covGraph_v2 = MGM.subgraph(listOfMetrics+listOfCovCluster+listOfCovInput)
	
	print('[V2] MIN INPUTS COV: {}'.format(len(listOfCovInput)), '\t\t/\tALL INPUTS: {}'.format(len(listOfInputs)))

	return listOfCovInput,covGraph_v2

def getMinimumCostEdge(listOfWeightEdgeAttr, source):
	minW = 999999
	minTarget = None
	for edgeAttr in listOfWeightEdgeAttr:
		tmp_min = listOfWeightEdgeAttr[(edgeAttr[0],edgeAttr[1])]
		if source == edgeAttr[0] and tmp_min < minW:
			minW		=	tmp_min
			minTarget	=	edgeAttr[1]
			
	return minTarget

def exeMinSetCoverV3(MGM, listOfCovCluster, listOfCovInput):
	listOfMetrics = [x for x in MGM.nodes if 'M' in x]
	listOfSources = [x for x in MGM.nodes if 'S' in x]

	subMGM 		= 	MGM.subgraph(listOfMetrics+listOfCovCluster+listOfCovInput+listOfSources)

	listOfWeightEdgeAttr		=	nx.get_edge_attributes(subMGM, 'weight')

	listOfMinCostSources		=	[ getMinimumCostEdge(listOfWeightEdgeAttr,inputCov) for inputCov in listOfCovInput if getMinimumCostEdge(listOfWeightEdgeAttr,inputCov) is not None]
	
	covGraph_v3 = MGM.subgraph(listOfMetrics+listOfCovCluster+listOfCovInput+listOfMinCostSources)
	
	print('[V3] MIN SOURCE COST: {}'.format(len(listOfMinCostSources)), '\t/\tALL SOURCE: {}'.format(len(listOfSources)))

	return listOfMinCostSources,covGraph_v3
	
def MGMminSetCover(MGM,outputFile,draw=True,saveFig=True,color=True,show=False):
	print('START TASK: MGMminSetCover()')
	outputFile_BASE	=	outputFile.split('.')[0]+"_START."+outputFile.split('.')[1]

	outputFile_v1	=	outputFile.split('.')[0]+"_v1."+outputFile.split('.')[1]
	listOfCovCluster,covGraph_v1	=	exeMinSetCoverV1(MGM)


	outputFile_v2	=	outputFile.split('.')[0]+"_v2."+outputFile.split('.')[1]
	listOfCovInput,covGraph_v2    =   exeMinSetCoverV2(MGM,listOfCovCluster)
	

	outputFile_COMPLETE	=	outputFile.split('.')[0]+"_COVERED."+outputFile.split('.')[1]
	listOfMinCostSources,covGraph_v3	=	exeMinSetCoverV3(MGM,listOfCovCluster,listOfCovInput)

	if draw:
		drawGraph(MGM, outputFile_BASE,saveFig=saveFig,catColor=color,show=show)
		drawGraph(covGraph_v1, outputFile_v1,saveFig=saveFig,catColor=color,show=show)
		drawGraph(covGraph_v2, outputFile_v2,saveFig=saveFig,catColor=color,show=show)
		drawGraph(covGraph_v3, outputFile_COMPLETE,saveFig=saveFig,catColor=color,show=show)
	
	print('END TASK: MGMminSetCover()')

def getListOfClusters(MGM,listOfInput):
	#this function respect that a CLUSTER set is a sub sef of nodes
	listOfCluster	=	[]
	for inpt in listOfInput:
		clusters	= [edge[0] for edge in MGM.in_edges(inpt)]	
		for cluster in clusters:
			outEdges	=	[edge[1] for edge in MGM.out_edges(cluster)]
			if set(outEdges).issubset(set(listOfInput)):
				listOfCluster.append(cluster)
	
	return list(set(listOfCluster))


def minSetCovByINPUT(MGM, listOfInput, outputFile):
	listOfCluster	= 	getListOfClusters(MGM,listOfInput)
	listOfMetrics	=	list(set([edge[0] for edge in MGM.in_edges(listOfCluster) ]))
	listOfSources	=	[edge[1] for edge in MGM.out_edges(listOfInput) ]

	subGraph	=	MGM.subgraph(listOfMetrics+listOfCluster+listOfInput+listOfSources)

	MGMminSetCover(subGraph,outputFile)

	results	=	('With: {} inputs I covered: {} metrics\n\n').format(len(listOfInput), len(listOfMetrics))	
	print(results)



def minSetCovBySOURCE(MGM, listOfSources, outputFile):
	listOfInput		=	list(set([edge[0] for source in listOfSources for edge in MGM.in_edges(source) ]))
	listOfCluster	=	getListOfClusters(MGM,listOfInput)
	listOfMetrics	=	list(set([edge[0] for edge in MGM.in_edges(listOfCluster) ]))
	
	subGraph	=	MGM.subgraph(listOfMetrics+listOfCluster+listOfInput+listOfSources)

	MGMminSetCover(subGraph,outputFile)
	results	=	('With: {} sources I covered: {} metrics\n\n').format(len(listOfSources), len(listOfMetrics))	
	print(results)