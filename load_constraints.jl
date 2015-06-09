# load_constraints.jl
# Gets city information from manhattan.jld object and travel time information from Travel time CSV
# Authored by Arthur J Delarue on 6/8/15

# Load city graph
println("**** Loading city graph ****")
useShortestPaths = true
# manhattan = SquareCity(3)
manhattan = Manhattan(sp=useShortestPaths)
roads = edges(manhattan.network)
nodes = vertices(manhattan.network)
graph = manhattan.network
times = manhattan.roadTime
if useShortestPaths
	sp = manhattan.sp
end
out = [copy(out_neighbors(graph,i)) for i in nodes]

# Load travel time data
println("**** Loading travel times ****")
dataFile = "Travel_times/travel_times_r20_wd_1214.csv"
data = readcsv(dataFile)
nodePairs = data[:,1]
average = data[:,2]

# Put travel time data in an array
travel_times = zeros(length(nodes),length(nodes))
for (i, element) in enumerate(nodePairs)
	node = split(element, ";")
	travel_times[int(node[1])+1, int(node[2])+1] = average[i]
	# Remember +1 because Python indexes from 0 but Julia from 1
end