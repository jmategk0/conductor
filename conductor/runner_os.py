import conductor

if __name__ == "__main__":

    ops = conductor.OperationWrapper(debug=True)
    my_groups = ops.list_files(verbose=True)
    print(my_groups)
