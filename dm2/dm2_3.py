#!/usr/bin/env python

import sys
import networkx as nx
from networkx.algorithms.flow.utils import *
from networkx.generators.classic import empty_graph
import random
from collections import deque
from itertools import islice
import pprint
import re

def draw_incident_matrix(G):
	nodes = G.nodes()
	edges = G.edges()
	n = len(nodes)
	e = len(edges)
	space = 0
	print ("\nINCIDENCE MATRIX")
	if(e > 10):
		space = 3
		print ("{0}".format(chr(32)*space)),
	else:
		space = 2
		print ("{0}".format(chr(32)*space)),
	for i in nodes:
		print ("v{0}".format(i)),
	k = 0
	while k < e:
		if(k<10):
			print ("\ne{0}{1}".format(k,chr(32)*(space-1))),
		else:
			print ("\ne{0}{1}".format(k,chr(32)*(space-2))),
		k += 1
		for x in nodes:
			if(x in edges[k-1]):
				if(x<9):
					print ("{0}{1}".format(1,chr(32))),
				else:
					print ("{0}{1}".format(1,chr(32)*2)),
			else:
				if(x<9):
					print ("{0}{1}".format(0,chr(32))),
				else:
					print ("{0}{1}".format(0,chr(32)*2)),
	print ("\n")


def preflow_push_impl(G, s, t, capacity, residual, global_relabel_freq,
					  value_only):
	"""Implementation of the highest-label preflow-push algorithm.
	"""
	if s not in G:
		raise nx.NetworkXError('node %s not in graph' % str(s))
	if t not in G:
		raise nx.NetworkXError('node %s not in graph' % str(t))
	if s == t:
		raise nx.NetworkXError('source and sink are the same node')

	if global_relabel_freq is None:
		global_relabel_freq = 0
	if global_relabel_freq < 0:
		raise nx.NetworkXError('global_relabel_freq must be nonnegative.')

	if residual is None:
		R = build_residual_network(G, capacity)
	else:
		R = residual

	detect_unboundedness(R, s, t)

	R_node = R.node
	R_pred = R.pred
	R_succ = R.succ

	# Initialize/reset the residual network.
	for u in R:
		R_node[u]['excess'] = 0
		for e in R_succ[u].values():
			e['flow'] = 0

	def reverse_bfs(src):
		"""Perform a reverse breadth-first search from src in the residual
		network.
		"""
		heights = {src: 0}
		q = deque([(src, 0)])
		while q:
			u, height = q.popleft()
			height += 1
			for v, attr in R_pred[u].items():
				if v not in heights and attr['flow'] < attr['capacity']:
					heights[v] = height
					q.append((v, height))
		return heights

	# Initialize heights of the nodes.
	heights = reverse_bfs(t)

	if s not in heights:
		# t is not reachable from s in the residual network. The maximum flow
		# must be zero.
		R.graph['flow_value'] = 0
		return R

	n = len(R)
	# max_height represents the height of the highest level below level n with
	# at least one active node.
	max_height = max(heights[u] for u in heights if u != s)
	heights[s] = n

	grt = GlobalRelabelThreshold(n, R.size(), global_relabel_freq)

	# Initialize heights and 'current edge' data structures of the nodes.
	for u in R:
		R_node[u]['height'] = heights[u] if u in heights else n + 1
		R_node[u]['curr_edge'] = CurrentEdge(R_succ[u])

	def push(u, v, flow):
		"""Push flow units of flow from u to v.
		"""
		R_succ[u][v]['flow'] += flow
		R_succ[v][u]['flow'] -= flow
		R_node[u]['excess'] -= flow
		R_node[v]['excess'] += flow

	# The maximum flow must be nonzero now. Initialize the preflow by
	# saturating all edges emanating from s.
	for u, attr in R_succ[s].items():
		flow = attr['capacity']
		if flow > 0:
			push(s, u, flow)

	# Partition nodes into levels.
	levels = [Level() for i in range(2 * n)]
	for u in R:
		if u != s and u != t:
			level = levels[R_node[u]['height']]
			if R_node[u]['excess'] > 0:
				level.active.add(u)
			else:
				level.inactive.add(u)

	def activate(v):
		"""Move a node from the inactive set to the active set of its level.
		"""
		if v != s and v != t:
			level = levels[R_node[v]['height']]
			if v in level.inactive:
				level.inactive.remove(v)
				level.active.add(v)

	def relabel(u):
		"""Relabel a node to create an admissible edge.
		"""
		grt.add_work(len(R_succ[u]))
		return min(R_node[v]['height'] for v, attr in R_succ[u].items()
				   if attr['flow'] < attr['capacity']) + 1

	def discharge(u, is_phase1):
		"""Discharge a node until it becomes inactive or, during phase 1 (see
		below), its height reaches at least n. The node is known to have the
		largest height among active nodes.
		"""
		height = R_node[u]['height']
		curr_edge = R_node[u]['curr_edge']
		# next_height represents the next height to examine after discharging
		# the current node. During phase 1, it is capped to below n.
		next_height = height
		levels[height].active.remove(u)
		while True:
			v, attr = curr_edge.get()
			if (height == R_node[v]['height'] + 1 and
				attr['flow'] < attr['capacity']):
				flow = min(R_node[u]['excess'],
						   attr['capacity'] - attr['flow'])
				push(u, v, flow)
				activate(v)
				if R_node[u]['excess'] == 0:
					# The node has become inactive.
					levels[height].inactive.add(u)
					break
			try:
				curr_edge.move_to_next()
			except StopIteration:
				# We have run off the end of the adjacency list, and there can
				# be no more admissible edges. Relabel the node to create one.
				height = relabel(u)
				if is_phase1 and height >= n - 1:
					# Although the node is still active, with a height at least
					# n - 1, it is now known to be on the s side of the minimum
					# s-t cut. Stop processing it until phase 2.
					levels[height].active.add(u)
					break
				# The first relabel operation after global relabeling may not
				# increase the height of the node since the 'current edge' data
				# structure is not rewound. Use height instead of (height - 1)
				# in case other active nodes at the same level are missed.
				next_height = height
		R_node[u]['height'] = height
		return next_height

	def gap_heuristic(height):
		"""Apply the gap heuristic.
		"""
		# Move all nodes at levels (height + 1) to max_height to level n + 1.
		for level in islice(levels, height + 1, max_height + 1):
			for u in level.active:
				R_node[u]['height'] = n + 1
			for u in level.inactive:
				R_node[u]['height'] = n + 1
			levels[n + 1].active.update(level.active)
			level.active.clear()
			levels[n + 1].inactive.update(level.inactive)
			level.inactive.clear()

	def global_relabel(from_sink):
		"""Apply the global relabeling heuristic.
		"""
		src = t if from_sink else s
		heights = reverse_bfs(src)
		if not from_sink:
			# s must be reachable from t. Remove t explicitly.
			del heights[t]
		max_height = max(heights.values())
		if from_sink:
			# Also mark nodes from which t is unreachable for relabeling. This
			# serves the same purpose as the gap heuristic.
			for u in R:
				if u not in heights and R_node[u]['height'] < n:
					heights[u] = n + 1
		else:
			# Shift the computed heights because the height of s is n.
			for u in heights:
				heights[u] += n
			max_height += n
		del heights[src]
		for u, new_height in heights.items():
			old_height = R_node[u]['height']
			if new_height != old_height:
				if u in levels[old_height].active:
					levels[old_height].active.remove(u)
					levels[new_height].active.add(u)
				else:
					levels[old_height].inactive.remove(u)
					levels[new_height].inactive.add(u)
				R_node[u]['height'] = new_height
		return max_height

	# Phase 1: Find the maximum preflow by pushing as much flow as possible to
	# t.

	height = max_height
	while height > 0:
		# Discharge active nodes in the current level.
		while True:
			level = levels[height]
			if not level.active:
				# All active nodes in the current level have been discharged.
				# Move to the next lower level.
				height -= 1
				break
			# Record the old height and level for the gap heuristic.
			old_height = height
			old_level = level
			u = next(iter(level.active))
			height = discharge(u, True)
			if grt.is_reached():
				# Global relabeling heuristic: Recompute the exact heights of
				# all nodes.
				height = global_relabel(True)
				max_height = height
				grt.clear_work()
			elif not old_level.active and not old_level.inactive:
				# Gap heuristic: If the level at old_height is empty (a 'gap'),
				# a minimum cut has been identified. All nodes with heights
				# above old_height can have their heights set to n + 1 and not
				# be further processed before a maximum preflow is found.
				gap_heuristic(old_height)
				height = old_height - 1
				max_height = height
			else:
				# Update the height of the highest level with at least one
				# active node.
				max_height = max(max_height, height)

	# A maximum preflow has been found. The excess at t is the maximum flow
	# value.
	if value_only:
		R.graph['flow_value'] = R_node[t]['excess']
		return R

	# Phase 2: Convert the maximum preflow into a maximum flow by returning the
	# excess to s.

	# Relabel all nodes so that they have accurate heights.
	height = global_relabel(False)
	grt.clear_work()

	# Continue to discharge the active nodes.
	while height > n:
		# Discharge active nodes in the current level.
		while True:
			level = levels[height]
			if not level.active:
				# All active nodes in the current level have been discharged.
				# Move to the next lower level.
				height -= 1
				break
			u = next(iter(level.active))
			height = discharge(u, False)
			if grt.is_reached():
				# Global relabeling heuristic.
				height = global_relabel(False)
				grt.clear_work()

	R.graph['flow_value'] = R_node[t]['excess']
	return R


def input_vertices():
	vertices = None
	print ("{:*^30}".format(""))
	while not isinstance(vertices,int):
		try:
			vertices = raw_input("Enter the number of vertices - ")
			if(vertices == "exit"):
				break
			vertices = int(vertices)
			return vertices
		except ValueError:
			print ("Not an integer value...\nfor exiting write - 'exit'")


def getList(in_list, message):
	while True:
		num_inp = raw_input("\n{} ".format(message))
		for string in num_inp.split(","):
			try:
				first = int(string)
				in_list.append(first)
			except ValueError:
				in_list = []
				print ("Not an integer value...")
				continue
		break


def read_data_from_file(f_name):
	f = open(f_name)
	kk = f.readlines()
	f.close()
	G = None
	G_list = []
	list_source = []
	list_sink = []
	for line in kk:
		if line.strip().startswith("#"):
			continue
		ll = line.strip().replace(" ","")
		res = ll.split("=")
		if len(res) < 2:
			continue
		name = res[0]
		val = res[1]

		if name == "Graph":
			size = 0
			val = val.replace("[","")
			vals = val.split("]")
			rx = re.compile("\((\d+),(\d+)\):(\d+)")
			for el in vals:
				re_res = re.search(rx,el)
				if re_res:
					in_point, outp_point, weight = map(int,re_res.groups())
					G_list.append((in_point,outp_point,weight))
					size = max(in_point, size)
					size = max (outp_point,size)
			if G_list == []:
				continue
			G = empty_graph(size)
			for i in G_list:
				G.add_edge(i[0],i[1],capacity=i[2])


		elif name == "Source":
			for string in val.split(","):
				try:
					first = int(string)
					list_source.append(first)
				except ValueError:
					list_source = []
		elif name == "Sink":
			for string in val.split(","):
				try:
					first = int(string)
					list_sink.append(first)
				except ValueError:
					list_sink = []


	if G == none or list_source == [] or list_sink == []:
		raise RuntimeError("invalid config file. State G={}, list_src={},list_sink={}".format(G,list_source, list_sink))
	return G, list_source, list_sink


if __name__ == "__main__":
	vertices = input_vertices()

	if len(sys.argv) <2:
		probability = random.randrange(2,8,1)
		probability /= 10.0
		G=nx.fast_gnp_random_graph(vertices,probability)
		list_src = []
		list_sink = []

		getList(list_src,"Enter sources list (separated with coma) -")
		getList(list_sink, "Enter sinks list (separated with coma) - ")
	else:
		G, list_src, list_sink = read_data_from_file (sys.argv[1] )



	print ("{:*^30}".format(""))
	print ("{:*^30}".format("Incident Matrix is"))
	draw_incident_matrix(G)
	print ("{:*^30}".format(""))
	print ("The edges are "+("{0}".format(G.edges())))
	print ("{:*^30}".format(""))
	print ("{:*^30}".format("The weighted edges of graph are "))
	for v,u in G.edges():
		cap=random.randrange(2,8,1)
		G.add_edge(v,u,capacity=cap)
		print ("[({0},{1}):{2}]".format(v,u,cap)),

	print ("")



	for src in list_src:
		G.add_edge("source",src)
	for sink in list_sink:
		G.add_edge("sink",sink)
		
	print ("{:*^30}".format(""))

	flow_value, flow_dict = nx.maximum_flow(G,"source","sink")

	print ("{:*^30}".format("Maximum value of flow - {}".format(flow_value)))
	print ("The value of flow that went through each edge ")
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(flow_dict)
	print ("{:*^30}".format(""))
		
