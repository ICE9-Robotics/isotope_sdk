import time

# v = {i*10: i for i in range(100)}
# v1 = [i for i in range(100)]
# v2 = [i*10 for i in range(100)]

# t = time.perf_counter()
# if 100 in v: 
#     del v[100]
#     del v[10]

# td = time.perf_counter() - t

# t = time.perf_counter()
# try:
#     i = v2.index(100)
#     del v2[i]
#     del v1[i]
#     del v2[2]
#     del v1[2]
# except ValueError:
#     pass

# td2 = time.perf_counter() - t


# print(td, td2, (td2-td)/td)
import threading

my_dict = {i: i for i in range(10)}

def do():
    for i in range(10):
        if i in my_dict:
            my_dict[i*10] = i*10
    print("done")
    
    
t = threading.Thread(target=do)
t.start()
for i in range(10):
    while i not in my_dict:
        pass
    my_dict.pop(i)
print("done too")
t.join()
print(my_dict)
    