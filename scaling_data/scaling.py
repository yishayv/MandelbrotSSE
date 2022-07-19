#!/usr/bin/env python2
#
# Process and plot logs generated by two test executions:
#
# - One with normal benchmarking (i.e. option '-b')
# - One with option "-p 100" set, in addition to '-b'.
#
# The second one tells my code to reuse NOTHING from the previous
# frame; and recompute each and every pixel. This means we no longer
# run the Xaos algorithm - we use the pure AVX ('-v', default)
# algorithm, so we become completely CPU bound.
#
# By default, '-p' is set to 0.75, which means only 0.75%
# pixels are actually computed; the rest (99.25%) are copied
# from the previous frame, making the process memory-bandwidth-bound,
# and not CPU-bound. This is why by default we run so fast;
# but that also explains why we don't scale linearly with
# more cores - memory bandwidth is, still, the final frontier.
#
# /u/JanneJM asked me about this in the Reddit/programming
# thread (https://bit.ly/3AXdqG2), so I managed to run the code
# in a machine with 52 cores, with this command:
#
## First execution: '-p' set to default, 0.75. We expect this to be
## memory bound, and not scale linearly with more cores:
#
# for ((i=1; i<=$(nproc); i++)); do 
#    printf "%02d thread(s): " $i 
#    OMP_NUM_THREADS=$i SDL_VIDEODRIVER=dummy ./src/mandelSSE -b 256 192 |& grep Frames/ 
# done | tee log.txt
#
## Second execution: '-p' set to 100%!
## This is completely CPU bound, so it should scale linearly with more cores:
#
# for ((i=1; i<=$(nproc); i++)); do 
#    printf "%02d thread(s): " $i 
#    OMP_NUM_THREADS=$i SDL_VIDEODRIVER=dummy ./src/mandelSSE -b -p 100 256 192 |& grep Frames/ 
# done | tee log2.txt
#
# This script processes the two log files, and shows the difference :-)

from matplotlib import pyplot as plt

## agg backend is used to create plot as a .png file
# mpl.use('agg')

data_without_p_set = [
    float(line.split()[-1])
    for line in open("log.txt").readlines()
]
data_with_p_set = [
    float(line.split()[-1])
    for line in open("log2.txt").readlines()
]
assert len(data_with_p_set) == len(data_without_p_set)
cores_used = list(range(1,len(data_without_p_set)+1))

# Create a figure instance
fig = plt.figure(1, figsize=(9, 6))

# Create an axes instance
ax = fig.add_subplot(111)

plt.plot(cores_used, data_without_p_set, label="with '-b'")
plt.plot(cores_used, data_with_p_set, label="with '-b -p 100'")
plt.legend(loc='lower right')

## Remove top axes and right axes ticks
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()

# Set axis labels
ax.set_xlabel(
    "Number of cores used (via OMP_NUM_THREADS)",
    fontdict={'fontsize': 13})
ax.set_ylabel(
    "Achieved frames per second",
    fontdict={'fontsize': 13})

# Save the figure
fig.savefig('scaling.png', bbox_inches='tight')
