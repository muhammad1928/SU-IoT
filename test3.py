import time
def func1():
    for i in range(3):
        print(f"func1: {i}")
    time.sleep(1)
    func2()

def func2():
    for i in range(3):
        print(f"func2: {i}")
    time.sleep(1)
    func3()

def func3():
    for j in range(3):
        if j <= 3:
            print(f"func3: {j}")
            time.sleep(1)  
        else:  
            func4()
            print(f"func3: {j}")

def func4():
    print(f"func4:")
    time.sleep(1)
    
func1()