#include <cstdio>
#include <fstream>
#include <vector>
#include <queue>
#include <string>
#include <iostream>
#include <algorithm>

#define MAX_NODES 100

/* Each node is represented as having in/outs maxing at 4 in total.
  0 indicates no signal is avaliable
 -1 indicates no neighbor
*/

struct Node {

	int id = -1;
	int layer = -1;
	
	int in[4]  		= {0, 0, 0, 0};
	int out[4] 		= {0, 0, 0, 0};
	int signal[4]	= {0, 0, 0, 0};
	int consumed[4] = {0, 0, 0, 0};

	int in_size 	= 0;
	int out_size 	= 0;

};

// Global Variables
int nodes, edges;
std::vector<Node> graph;
std::string instance;

void expandEdge(int w, int &prev) {

	while(w--) {
		
		// Create a buffer and conect input from previus node -> current buffer
		Node n;
		n.id = nodes;
		n.in[0] = prev;
		n.in_size++;

		graph.push_back(n);
		
		// Connect previus node output to current buffer node
		graph[prev].out[graph[prev].out_size] = nodes;
		graph[prev].out_size++;
		
		prev = nodes;
		nodes++;
	}

}
void setNodeLevels() {
	
	std::queue<int> q;
	bool visited[nodes] = {false};
	
	// Initializing input level as 0
	for(int i=0; i<graph.size(); i++) {
		if(graph[i].in_size == 0) {
			graph[i].layer = 0;
			q.push(i);
		}
	}

	while( !q.empty() ) {
		
		// Assuming a DiGraph, so no need for visited array. 
		// Otherwise it WILL get stuck in a loop

		int pos = q.front(); q.pop();
		Node u = graph[pos];
		
		for(int i=0; i<u.out_size;  i++) {
			int u_neighbor = u.out[i];
			graph[u_neighbor].layer = std::max(graph[u_neighbor].layer, graph[u.id].layer + 1); 
			q.push(u_neighbor);
		}
	}

}

void read_input(const char *fileName) {

	std::ifstream file(fileName, std::ifstream::in);
	if( !file.is_open() ) {
		printf( "Error opening file! Check if the first parameter provided is a valid path to a file ex.:\n"
				"UNIX:\t\tpath/to/file.txt\n"
				"WINDOWS:\tC:\\path\\to\\file.txt\n"
				"path provided:\t%s\n", fileName);
		exit(EXIT_FAILURE);
	}

	bool isWeightedGraph = instance.find("weighted") != std::string::npos;
	
	file >> nodes >> edges;
	graph.resize(nodes);
	
	if(isWeightedGraph) {
		
		int u,v,w;
		while(file >> u >> v >> w) {
		
			// Parent node
			int prev = u;
			graph[u].id = u;
			
			// Expanding edge weight into nodes
			expandEdge(w, prev);
			graph[prev].out[graph[prev].out_size] = v;
			graph[prev].out_size++;
			if(graph[prev].out_size >= 4) {
				printf("Aborting because node %d has more edges(%d/4) than the architecture allows \n", 
						graph[prev].id, graph[prev].out_size);
				exit(EXIT_FAILURE);
			}

			// Child node 
			graph[v].id = v;
			graph[v].in[graph[v].in_size] = prev;
			graph[v].in_size++;
			if(graph[v].in_size >= 4) {
				printf("Aborting because node %d has more edges(%d/4) than the architecture allows \n", 
						graph[v].id, graph[v].in_size);
				exit(EXIT_FAILURE);
			}
		
		}
	}

	else {
		
		int u,v;
		while(file >> u >> v) {
		
			// Connects u to v and updates @u neighbor and output list size.
			graph[u].id = u;
			graph[u].out[graph[u].out_size] = v;
			graph[u].out_size++;
			
			// Making it an undirected graph, connects v to u and updates @v neighbor and input list
			graph[v].id = v;
			graph[v].in[graph[v].in_size] = u;
			graph[v].in_size++;
		
		}
	}

	setNodeLevels();
	file.close();

}

void print_graph(int iteration) {

	// Removing file directory 
	size_t extension = instance.find_last_of("/\\");
	instance = instance.substr(extension+1);
	
	// Removing .txt
	extension = instance.find_last_of(".");
	instance = instance.substr(0,extension);

	std::string fileName( "/home/lucas/Dropbox/IC/async/dot/"+ instance + ".dot");
	std::ofstream output(fileName, std::ofstream::out);

	output << "digraph G {\n";
	for(int i=0; i<graph.size(); i++)
		for(int j=0; j<graph[i].out_size; j++){
				
				std::string edge_label( std::to_string(graph[i].signal[j]) );
				
				edge_label = "[label=\"(" + edge_label + ")\"]";
				
				output << graph[i].id << " -> " << graph[i].out[j] << " " << edge_label << "\n";
		}
	output << "}";
	output.close();


}
