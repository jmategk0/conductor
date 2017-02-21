import conductor

if __name__ == "__main__":

    ops = conductor.OperationWrapper(debug=True)
    my_groups = ops.list_my_groups()
    print(my_groups)

