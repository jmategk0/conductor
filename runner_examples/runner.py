import conductor

if __name__ == "__main__":
    # Note: You must run this script with sudo.
    filename = "/shell_commands/setup_ubuntu_desktop_1604.txt"

    print("Starting install....")
    ops = conductor.OperationWrapper(debug=True)
    ops.install(filename)
    print("Done!")
