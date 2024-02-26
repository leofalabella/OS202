import numpy as np
from numpy import random
from mpi4py import MPI

#dimension du array
dim = 10000
end_value = 1000

comm = MPI.COMM_WORLD.Dup()
rank = comm.Get_rank()
size = comm.Get_size()


if rank == 0:
    #generate a random array
    unsorted = np.array(random.randint(1, end_value, size=(dim), dtype=int))
    print('Rank: ', rank, ', Initial array: ', unsorted)
else:
    unsorted = np.zeros(dim, dtype=int)
comm.Bcast(unsorted)

cond = True

div = dim//size
subdiv = div//size
z = size

# setting pivots
recv = np.empty((div), dtype=int)
comm.Scatter(unsorted, recv, root=0) #share target list among cores
   
sample_pivot = np.array(random.choice(recv, z+1, replace=False)) #get a sample from each core

pivots_counts = np.array([z+1 for _ in range(size)])
pivots_displ = np.array([(z+1)*k for k in range(size)])
possible_pivots = np.zeros(sum(pivots_counts), dtype=int)
comm.Gatherv(sample_pivot, [possible_pivots, pivots_counts, pivots_displ, MPI.INTEGER8], root=0) #gather samples

if rank == 0:
    list_pivot = random.choice(possible_pivots, z-1, replace=False) #grab a list from all the samples
    list_pivot = np.sort(list_pivot) #sort 
    list_pivot = np.append(list_pivot, end_value) #add 0 and end value
    list_pivot = np.insert(list_pivot, 0, 0)
else:
    list_pivot = np.zeros(z+1, dtype=int)
comm.Bcast(list_pivot)


#distribute list to buckets
buckets = [[] for k in range(z)]
for elem in unsorted:
    i = 0
    while i < z+1: #i lesser than number of pivots
        if elem >= list_pivot[i] and elem <= list_pivot[i+1]:
            buckets[i].append(elem) #if elem is contained by the bucker interval append it
            break
        else:
            i+=1

# organizing data, so we can Scatterv it properly to each process
data_organized = []
counts = []
displacement = 0
displs = []
for ii in range(len(buckets)):
    counts.append(len(buckets[ii]))
    displs.append(displacement)
    for jj in range(counts[-1]):
        data_organized.append(buckets[ii][jj])
        displacement += 1

data_organized = np.array(data_organized)
counts = np.array(counts)
displs = np.array(displs)


local_unsorted = np.empty(counts[rank], dtype=int)
comm.Scatterv([data_organized, counts, displs, MPI.INTEGER8], local_unsorted, root=0)

print(counts)
# print(rank, 'local unsorted', local_unsorted)

local_sorted = np.sort(local_unsorted)

data_sorted = np.zeros(sum(counts), dtype=int)
# print(rank, "local_sorted", local_sorted)
# print("%s gathering" % rank)
comm.Gatherv(local_sorted, [data_sorted, counts, displs, MPI.INTEGER8], root=0)

if rank == 0:
    print("Data sorted", data_sorted)
