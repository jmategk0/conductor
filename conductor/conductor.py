import os
import logging
import logging.config


def command_string_builder(argument_dictionary, prepend, append="", flags_list="", argument_delimiter="-"):
    """
    This function dynamically builds a shell executable command string, so tht you don't have to manually build stings
     using the pythons string formatting tools. This function is lazy and somewhat inefficient.

    :param argument_dictionary: A dictionary of command line arguments. Should not have any "-" marks. keys are arg
     names.
    :param prepend: A string value attached to the start of the command sting. Normally the software name/path.
    :param append: A sting value added to the end of the command sting. Sometimes used for file paths.
    :param flags_list: A list of command lines flags without argument delimiters.
    :param argument_delimiter: By default arguments delimiters are defined as "-", here they may be changed to "--"
    or any other value needed by the command.

    :return: A fully formatted command string. Not in this implementation arguments will be placed in random order.
    """

    argument_list = []
    for key in argument_dictionary:

        formatted_key = "{delim}{key_value} ".format(
            delim=argument_delimiter,
            key_value=key)

        argument_string = "{formatted_key}{value} ".format(
            formatted_key=formatted_key,
            value=str(argument_dictionary[key]))

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

    def start_non_blocking_process(self, command_string):
        # TODO: Find a lazy way to start a non-blocking process with the multithreading lib? Or maybe async?
        raise NotImplementedError

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

    def change_permissions(self, permission_code, directory_name, enable_recursion):

        """

        :param permission_code: Code used for allocating file/directory permissions such as g+wrx. or 755.
        :param directory_name: The name of the file or directory you want to edit permissions on.
        :param enable_recursion: Enable recursion to apply the permission code to all files/folders within the directory

        :return: A formatted chmod command sting.
        """

        if enable_recursion:
            command = "chmod {code} {dir}".format(code=permission_code, dir=directory_name)
        else:
            command = "chmod {code} {dir} -R".format(code=permission_code, dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def change_group(self, group_name, directory_name, enable_recursion):

        """

        :param group_name: The name of the user group.
        :param directory_name: The name of the directory.
        :param enable_recursion: Enable recursion to apply the permission code to all files/folders within the directory
        :return: A formatted chgrp command
        """

        if enable_recursion:
            command = "chgrp {grp} {dir}".format(grp=group_name, dir=directory_name)
        else:
            command = "chgrp {grp} {dir} -R".format(grp=group_name, dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def change_owner(self, new_owner, directory_name, enable_recursion):
        """

        :param new_owner:
        :param directory_name:
        :param enable_recursion:
        :return:
        """

        if enable_recursion:
            command = "chown {own} {dir}".format(own=new_owner, dir=directory_name)
        else:
            command = "chgrp {own} {dir} -R".format(own=new_owner, dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def add_group(self, group_name):
        """

        :param group_name:
        :return:
        """
        command = "groupadd {name}".format(name=group_name)
        return self.start_blocking_process(command_string=command)

    def list_my_groups(self):
        """
        List the groups the current user belongs to.

        :return:
        """

        command = "groups"

        results = self.start_blocking_process(command_string=command)
        results = str(results).rstrip()
        return results.split(" ")

    def list_user_groups(self, username, verbose=False):
        """

        :param username:
        :param verbose:
        :return:
        """
        if verbose:
            command = "id {user}".format(user=username)
            raw_results = self.start_blocking_process(command_string=command)
            raw_results = str(raw_results).rstrip().split(" ")

            # parse uid
            uid = raw_results[0].replace("uid=", "").replace(")", "")
            uid_temp = uid.split("(")
            uid = {uid_temp[0]: uid_temp[1]}

            # parse gid
            gid = raw_results[1].replace("gid=", "").replace(")", "")
            gid_temp = gid.split("(")
            gid = {gid_temp[0]: gid_temp[1]}

            # parse groups
            groups_raw = raw_results[2].replace("groups=", "").replace(")", "").split(",")
            groups = {}
            for group in groups_raw:
                group_temp = group.split("(")
                groups[group_temp[0]] = group_temp[1]

            final_results = {"username": username, "uid": uid, "gid": gid, "groups": groups}
        else:
            string_to_remove = '{user} : '.format(user=username)
            command = "groups {user}".format(user=username)
            raw_results = self.start_blocking_process(command_string=command)
            raw_results = str(raw_results.rstrip())
            final_results = raw_results.replace(string_to_remove, "").split(" ")

        return final_results

    def add_new_user(self, username, user_home_directory, user_groups):
        """

        :param username:
        :param user_home_directory:
        :param user_groups:
        :return:
        """
        command = "useradd -d {home} -m {user} -G {groups}".format(
            home=user_home_directory,
            user=username,
            groups=user_groups)
        return self.start_blocking_process(command_string=command)

    def set_user_password(self, username, password):

        """

        :param username:
        :param password:
        :return:
        """
        command = "echo {user}:{password} | chpasswd".format(user=username, password=password)
        return self.start_blocking_process(command_string=command)

    def list_all_groups_on_system(self):
        """
        List all groups on the OS.

        :return:
        """
        command = "cat /etc/group"
        return self.start_blocking_process(command_string=command)

    def list_all_users(self):
        """

        :return:
        """
        command = "cat /etc/passwd"

        return self.start_blocking_process(command_string=command)

    def make_directory(self, full_dir_path):
        """

        Make a new file directory.

        :param full_dir_path: path what the dir should be created.
        :return: None.
        """

        mk_dir_command = "mkdir {dir}".format(dir=full_dir_path)
        self.start_blocking_process(command_string=mk_dir_command)

    def move_directory(self, from_directory, to_directory):
        """

        :param from_directory:
        :param to_directory:
        :return:
        """
        command = "mv {dir1} {dir2}".format(dir1=from_directory, dir2=to_directory)
        return self.start_blocking_process(command_string=command)

    def copy_directory(self, from_directory, to_directory):
        """

        :param from_directory:
        :param to_directory:
        :return:
        """
        command = "cp {dir1} {dir2}".format(dir1=from_directory, dir2=to_directory)
        return self.start_blocking_process(command_string=command)

    def remove_directory(self, directory_name):
        """

        :param directory_name:
        :return:
        """
        command = "rm {dir}".format(dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def print_working_directory(self):
        """

        :return:
        """

        command = "pwd"
        return self.start_blocking_process(command_string=command)

    def change_working_directory(self, directory_name):
        """

        :param directory_name:
        :return:
        """
        command = "cd {dir}".format(dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def head_file(self, filename, number_of_lines):
        """

        :param filename: Name of file to parse.
        :param number_of_lines:
        :return:
        """

        command = "head -n {lines} {file}".format(file=filename, lines=number_of_lines)
        return self.start_blocking_process(command_string=command)

    def tail_file(self, filename, number_of_lines):
        """

        :param filename:
        :param number_of_lines:
        :return:
        """

        command = "tail -n {lines} {file}".format(file=filename, lines=number_of_lines)
        return self.start_blocking_process(command_string=command)

    def view_file_contents(self, filename):
        """

        :param filename:
        :return:
        """

        command = "cat {file}".format(file=filename)
        return self.start_blocking_process(command_string=command)

    def list_files(self, verbose=False):
        """

        :param verbose:
        :return:
        """

        if verbose:
            command = "ls -ll"
            raw_results = self.start_blocking_process(command_string=command)
            result_lines = str(raw_results).split("\n")
            result_lines.pop()

            total = result_lines.pop(0)
            total = total.replace("total ", "")
            final_lines = []
            for line in result_lines:
                split_line = line.split(" ")
                filtered_line = list(filter(lambda a: a != "", split_line))  # remove all "" from list
                final_line = {
                    "permissions": filtered_line[0],
                    "score": filtered_line[1],
                    "owner": filtered_line[2],
                    "group": filtered_line[3],
                    "size": filtered_line[4],
                    "month": filtered_line[5],
                    "day": filtered_line[6],
                    "time": filtered_line[7],
                    "filename": filtered_line[8]
                }
                final_lines.append(final_line)

            final_results = {"total": total, "files": final_lines}

        else:
            command = "ls"
            raw_results = self.start_blocking_process(command_string=command)
            final_results = str(raw_results).split("\n")
            final_results.remove("")
        return final_results

    def web_get(self, url):
        """

        :param url:
        :return:
        """

        command = "wget {url}".format(url=url)
        return self.start_blocking_process(command_string=command)

    def remote_sync(self, from_directory, to_directory):
        """

        :param from_directory:
        :param to_directory:
        :return:
        """
        command = "rsync -a {dir1} {dir2}".format(dir1=from_directory, dir2=to_directory)
        return self.start_blocking_process(command_string=command)

    def network_addresses(self):
        """

        :return:
        """
        command = "ifconfig"
        return self.start_blocking_process(command_string=command)

    def list_hardware(self):
        """

        :return:
        """
        command = "lshw"
        return self.start_blocking_process(command_string=command)

    def disk_free_space(self):
        """

        :return:
        """
        command = "df -h"
        return self.start_blocking_process(command_string=command)

    def operating_system_information(self):
        """

        :return:
        """
        command = "lsb_release -a"
        return self.start_blocking_process(command_string=command)

    def operating_system_kernal_information(self):
        """

        :return:
        """
        command = "uname -a"
        return self.start_blocking_process(command_string=command)

    def md5_checksum(self, filename):
        """

        :return:
        """
        command = "md5sum {file}".format(file=filename)
        return self.start_blocking_process(command_string=command)

    def sha1_checksum(self, filename):
        """

        :return:
        """
        command = "sha1sum {file}".format(file=filename)
        return self.start_blocking_process(command_string=command)

    def update_system_packages(self):
        """

        :return:
        """
        command = "apt-get update"
        return self.start_blocking_process(command_string=command)

    def upgrade_system_packages(self):
        """

        :return:
        """
        command = "apt-get upgrade"
        return self.start_blocking_process(command_string=command)

    def install_system_packages(self, package_name):
        """

        :param package_name:
        :return:
        """
        command = "apt-get install {name}".format(name=package_name)
        return self.start_blocking_process(command_string=command)

    def system_uptime(self):
        """

        :return:
        """
        command = "uptime"
        return self.start_blocking_process(command_string=command)
