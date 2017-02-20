import os
import logging
import logging.config


def command_string_builder(commands_dict, prepend, append="", flags_list="", argument_delimiter="-"):

    """

    :param commands_dict:
    :param prepend: 
    :param append:
    :param flags_list:
    :param argument_delimiter:
    :return:
    """

    argument_list = []
    for key in commands_dict:
        formatted_key = "{delim}{key_value} ".format(delim=argument_delimiter, key_value=key)
        argument_string = "{formatted_key}{value} ".format(formatted_key=formatted_key, value=str(commands_dict[key]))
        argument_list.append(argument_string)

    formatted_command_string = "".join(argument_list)

    if flags_list:
        my_flags = []
        for item in flags_list:
            formatted_flag = "{delim}{flag_value} ".format(delim=argument_delimiter, flag_value=item)
            my_flags.append(formatted_flag)
        flags_string = "".join(my_flags)
        formatted_command_string = "{arg_list}{flags}".format(flags=flags_string, arg_list=formatted_command_string)

    # prepend
    formatted_command_string = "{prepend} {arg_list}".format(prepend=prepend, arg_list=formatted_command_string)

    if append:
        formatted_command_string = "{arg_list} {append}".format(append=append, arg_list=formatted_command_string)

    return formatted_command_string


class OperationWrapper(object):

    def __init__(self, debug=False, log_filename=""):
        self.print_command_strings = debug
        if self.print_command_strings:
            logging.basicConfig(filename=log_filename, level=logging.INFO)
            self.logger = logging.getLogger(__name__)

    def load_commands_from_text_file(self, filename):
        """
        Reads the contents of a text file and loads each line into a list element.

        :param filename: Name of with with a list of shell commands on each line.
        :return: A list containing strings where each string is a shell command without newlines.
        """
        with open(filename, 'r') as command_file:
            commands = command_file.read().splitlines()

        return commands

    def start_blocking_process(self, command_string):
        """
        Execute a shell commend. The function will not exit until the shell command has completed.

        :param command_string: A shell command represented as a string.
        :return: The shell output of the command as a string.
        """

        if self.print_command_strings:
            self.logger.info(command_string)

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
