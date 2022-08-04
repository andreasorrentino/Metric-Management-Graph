import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy as sp

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

categories		= 	config['GRAPH']['categories'].split(',')
categoryColors	=	config['GRAPH']['categoryColors'].split(',')



def drawGraph(G,outputFileName,pos,catColor=False,saveFig=True,fontSize=5,nodeSize=400):

	plt.figure(figsize=(21,30), frameon=False)

	options = {
		"font_size": fontSize,
		"node_size": nodeSize,
		"node_color": "white",
		"edgecolors": "black",
		"linewidths": 1,
		"width": 1
	}
	
	nx.draw_networkx(G, pos, **options)
	
	labels = nx.get_edge_attributes(G,'weight')
	nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)



	if catColor:
		coloredNode = [[],[],[],[]]
		dictNodeCat	=	nx.get_node_attributes(G, 'category')
		for node in dictNodeCat:
			for category in categories:
				if category == dictNodeCat[node]:
					index	=	categories.index(category)
					coloredNode[index].append(node)
		
		nx.draw_networkx_nodes(G, pos, nodelist=coloredNode[0], node_color="tab:blue")
		nx.draw_networkx_nodes(G, pos, nodelist=coloredNode[1], node_color="tab:red")
		nx.draw_networkx_nodes(G, pos, nodelist=coloredNode[2], node_color="tab:green")
		nx.draw_networkx_nodes(G, pos, nodelist=coloredNode[3], node_color="tab:gray")
		labels = {n: n for n in G if 'M' in n}
		nx.draw_networkx_labels(G, pos, labels,font_color="white",font_size=fontSize)





	# Set margins for the axes so that nodes aren't clipped
	ax = plt.gca()
	ax.margins()

	plt.axis("off")
	if saveFig:
		plt.savefig(outputFileName)
	plt.show()