import numpy as np
array = np.array([[-0, -0.80159163, 0],
                  [0.52181676, -0, 0],
                  [-0, -0, 0.29181864]])
array2 = list()
print(array2)
for x in range(0, len(array)):
    print(np.trim_zeros(array[x]))
    array2.append(np.trim_zeros(array[x]))
array2 = np.asarray(array2)
print(array2)
