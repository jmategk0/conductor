import os


class OperationWrapper(object):

    def __init__(self, debug=False):
        self.print_command_strings = debug

    def load_commands_from_text_file(self, filename):
        """
        Reads the contents of a text file and loads each line into a list element.

        :param filename: Name of with with a list of shell commands on each line.
        :return: A list containing strings where each string is a shell command without newlines.
        """
        with open(filename, 'r') as command_file:
            commands = command_file.read().splitlines()

        if self.print_command_strings:
            for command in commands:
                print(command)

        return commands

    def start_blocking_process(self, command_string):
        """
        Execute a shell commend. The function will not exit until the shell command has completed.

        :param command_string: A shell command represented as a string.
        :return: The shell output of the command as a string.
        """

        if self.print_command_strings:
            print(command_string)

        process = os.popen(command_string)
        process_response = process.read()
        process.close()

        return process_response

    def make_directory(self, full_dir_path):
        """

        Make a new file directory.

        :param full_dir_path: path what the dir should be created.
        :return: None.
        """
        mk_dir_command = "mkdir {dir}".format(dir=full_dir_path)
        self.start_blocking_process(command_string=mk_dir_command)

    def run_list_of_commands(self, list_of_command_strings):
        """
        Execute each shell command sequentially by iterating though the list of commands.

        :param list_of_command_strings: A list containing strings where each string is a shell command without newlines.
        :return: None.
        """

        for command in list_of_command_strings:
            self.start_blocking_process(command_string=command)

    def install(self, command_filename):
        """
        Read the contents of command_filename and then run each install command sequentially.

        :param command_filename:Name of with with a list of shell commands on each line.
        :return: None.
        """
        command_list = self.load_commands_from_text_file(command_filename)
        self.run_list_of_commands(command_list)


if __name__ == "__main__":
    # Note: You must run this script with sudo.
    print("Starting install....")
    ops = OperationWrapper(debug=True)
    ops.install("commands.txt")
    print("Done!")
