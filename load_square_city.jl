# load_square_city.jl
# Test file for LP, working on small square city
# Authored by Arthur J Delarue on 6/9/15

include("../taxi-simulation/Cities/squareCity.jl")

city = SquareCity(3)
graph = city.network
roads = edges(graph)
nodes = vertices(graph)
times = ones(9,9)
for i = 1:9
	times[i,i] = 0
end

sp = city.sp
out = [copy(out_neighbors(graph,i)) for i in nodes]

travel_times = zeros(9,9)
travel_times[1,8] = sp.traveltime[1,8]
travel_times[4,3] = sp.traveltime[4,3]
travel_times[7,6] = sp.traveltime[7,6]
travel_times[9,2] = sp.traveltime[9,2]
travel_times[6,8] = sp.traveltime[6,8]
