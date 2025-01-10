def func1():
    print("Hello from func1")
    func2()

def func2():
    print("Hello from func2")
    while True:
        for i in range(2):
            print(i)
            func2()
            if i == 2:
                break
    func3()

def func3():
    print("Hello from func3")

func1()
lights = {
    "lightlevel0": "#cccccc",
    "lightlevel1": "#fff394",
    "lightlevel2": "#ffd500",
}

print(lights["lightlevel1"])