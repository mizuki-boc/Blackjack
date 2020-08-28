class A:
    def function_A(self):
        print("call function_A")

class B:
    def function_B(self):
        print("call function_B")
    def call_A(self):
        a.function_A()

if __name__ == "__main__":
    a = A()
    a.function_A()


    b = B()
    b.function_B()

    b.call_A()

