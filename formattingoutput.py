import numpy as np
nr_it = 7
with open('output_tripgen_'+str(nr_it), 'r') as f:
    production = np.empty((nr_it, 8))
    attraction = np.empty((nr_it, 8))
    lines = f.readlines()
    for line in lines:
        line = line.split("\\r\\n")
        line.pop()
        #print("1:", line)
        k = 0
        w = 0
        for i in range(len(line)):
            #print("2:", line[i])
            line[i] = line[i].strip('[')
            line[i] = line[i].strip(']')
            line[i] = line[i].split()
            #print("3:", line[i])
            if i % 2 == 0:
                print(line[i])
                attraction[k] = np.array(line[i])
                print(attraction)
                k += 1
            else:
                production[w] = np.array(line[i])
                w += 1

production_means = np.mean(production, axis=0)
attraction_means = np.mean(attraction, axis=0)

print(production_means)
print(attraction_means)

print(sum(production_means))
print(sum(attraction_means))

percentage_prod = production_means/sum(production_means) * 100
percentage_att = attraction_means/sum(attraction_means) * 100
print("production", percentage_prod)
print("attraction", percentage_att)
print(sum(percentage_prod))
print(sum(percentage_att))





