# parallelism

Distributes workload among several machines using flask servers. 

All machines should run the bouncer.py script, and a master starts the process with the bouncer.start() function.
The function to be run is defined in each spoke, can be asymmetrical. Originally used to run distributed genetic algorithm optimization scripts.

Not secure, should only be used in local networks.
