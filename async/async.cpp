#include "core.h"

void propagateFrom(const Node &u) {
	
	for(int i=0; i<u.out_size; i++){
			
		int child_idx = 0;
		int parent_idx = 0;
		Node v = graph[u.out[i]];
		
		// Find child index and parent index
		while(u.out[child_idx] != v.id) child_idx++; 
		while(v.in[parent_idx] != u.id) parent_idx++;

		// If node already recieved the parents signal or its child is waiting for sync from all inputs
		if(u.signal[child_idx] == 0 || v.signal[parent_idx] != 0) continue;

		// Consume signal from parent @u
		graph[v.id].signal[parent_idx] = u.signal[child_idx];
		graph[v.id].consumed[parent_idx] = true;

		// In case there are more output wires than input wires, fill the rest (non-parented wires)
		// Maybe capping max fill will be necessary for other architectures (assuming max of 4 wires)
		int fill = v.out_size - v.in_size;
		if(fill > 0)
			for(int j=v.in_size; j<v.out_size; j++) {
				graph[v.id].signal[j] = u.signal[child_idx];
				graph[v.id].consumed[j] = true;
			}

		// This child already consumed it's signal
		graph[u.id].signal[child_idx] = 0;
		
		// If there are less outputs than inputs there won't be enough childs to reset the parent, in that case...
		if(u.out_size < u.in_size) {
			for(int k=u.out_size; k<u.in_size; k++) {
				graph[u.id].signal[k] = 0;
				graph[u.id].consumed[k] = false;
			}
		}
	}


}

void simulate() {
	
	// Determining which nodes are I/O
	std::vector<int> start;
	std::vector<int> end;
	bool isInput[nodes] = {false};
	
	int it = 1;
	int clk = 1;
	int maxLayer = -1;
	int throughput = 0;
	int latency = 0;
	bool isLatency = true;

	// Finding I/O nodes and populating the input initial value
	for(int i=0; i<graph.size(); i++) {
		
		if(graph[i].in_size	== 0) {
			
			start.push_back(i);
			isInput[i] = true;
			for(int j=0; j<graph[i].out_size; j++) {
				graph[i].signal[j] = clk;
				for(int k=0; k<4; k++) graph[i].consumed[k] = true;
			}
		}
		else if(graph[i].out_size == 0) end.push_back(i);

		maxLayer = std::max(maxLayer, graph[i].layer);
	}
	
	std::sort(end.begin(), end.end(), std::greater<int>());

	print_graph(0);

	// Do a reverse BFS
	while( it < 100) {
		
		std::queue<int> q;
		std::queue<int> qTemp;
		int l = maxLayer;

		bool visited[nodes] = {false};
		
		// BFS seeds
		for(int i=0; i<end.size(); i++) q.push(end[i]);
		
		while(!q.empty()) {
		
			int pos = q.front(); q.pop();
			bool processed = (visited[pos] || isInput[pos]);
			
			// Postpone processing nodes on upper layers (reaching faster on them disturbs propagation order)
			if(graph[pos].layer != l) {
				qTemp.push(pos);
				processed = true;
			}
			
			if(!processed) {

				visited[pos] = true;
				Node u = graph[pos];

				for(int i=0; i<u.in_size; i++) qTemp.push(u.in[i]);

				bool propagate = true;
				for(int i=0; i<u.in_size; i++)
					if(!u.consumed[i]) { propagate = false;	break; }
				
				if(propagate) 
					propagateFrom(u);
			}

			if(q.empty()) {
				std::swap(q, qTemp);
				l--;
			}

		}

		// Feeding from inputs
		for(int i=0; i<start.size(); i++)
			propagateFrom(graph[start[i]]);

		// Update clk if all outputs were distributed by a given input node
		clk++;
		for(int i=0;i<start.size(); i++){
			
			bool stall = false;
			Node n = graph[start[i]];

			for(int j=0; j<n.out_size; j++)
				if(n.signal[j] != 0) { stall = true; break;	}

			if(!stall) {
				for(int k=0; k<n.out_size; k++){
					graph[n.id].signal[k] = clk;
					graph[n.id].consumed[k] = true;
				}
			}
		}

		// Check if all outputs are synced and propagate
		bool output = true;
		for(int i=0; i<end.size(); i++)
			for(int j=0; j<graph[end[i]].in_size; j++)
				if(!graph[end[i]].consumed[j]) { output = false; break; }

		if(output) {
			isLatency = false;
			throughput++;

			// Reset outputs
			for(int i=0; i<end.size(); i++)
				for(int j=0; j<graph[end[i]].in_size; j++) {
					graph[end[i]].consumed[j] = false;
					graph[end[i]].signal[j] = 0;
				}
		}

		if(isLatency) latency++;
		it++;
	}
	
	printf("%.3lf\n", throughput/((it-1-latency)*1.0) );
}


int main(int argc, char** argv) {

	instance = argv[1];
	read_input(argv[1]);

	printf("%s\t", instance.c_str() );
	simulate();

}
