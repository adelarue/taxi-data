# build_LP.jl
# Once Manhattan problem is loaded, builds instance of LP necessary
# Authored by Arthur J Delarue on 6/9/15

function build_LP()
	println("**** Creating LP instance ****")
	# Create JuMP model
	m = Model(solver=GurobiSolver(TimeLimit=100))

	# Add one variable for each road
	# Either label them (i,j) if conditional formulation works
	@defVar(m, t[i=nodes,j=out[i]])# >= 0)#times[i,j])
	
	# Define objective function
	@setObjective(m, Min, sum{ t[i,j], i=nodes, j=out[i] })

	println("**** Constraints ****")
	# Add all the constraints
	l = 0
	println(maximum(travel_times))
	for i in nodes, j in nodes
		if travel_times[i,j] > 0
			pathNodes = [j]
			k = j
			while k != i
				k = sp.previous[i,k]
				push!(pathNodes, k)
			end
			reverse!(pathNodes)
			@addConstraint(m, sum{ t[pathNodes[a],pathNodes[a+1]], a=1:(length(pathNodes)-1) } >= travel_times[i,j])
		end
	end

	for i in nodes, j in out[i]
		@addConstraint(m, t[i,j] >= times[i,j])
	end


	status = solve(m)
	st = getValue(t)
	println(status)
end

build_LP()
