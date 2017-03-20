import os
import logging
import logging.config


def command_string_builder(argument_dictionary, prepend, append="",
                           flags_list="", argument_delimiter="-"):
    """This function dynamically builds a shell executable command string, so that
    you don't have to manually build strings using the pythons string
    formatting tools. This function is lazy and somewhat inefficient.

    Args:
        argument_dictionary (dict): A dictionary of command line arguments.
            Should not have any "-" marks. keys are arg names.
        prepend (str): A string value attached to the start of the command
            string. Normally the software name/path.
        append (str): A string value added to the end of the command string.
            Sometimes used for file paths. Defaults to nothing ("").
        flags_list (List[str]): A list of command lines flags without argument
            delimiters. Defaults to nothing ("").
        argument_delimiter (str): By default arguments delimiters are defined
            as "-", here they may be changed to "--" or any other value needed
            by the command.

    Returns:
        str: A fully formatted command string. Not in this implementation
            arguments will be placed in random order.
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
            formatted_flag = "{delim}{flag_value} ".format(delim=argument_delimiter,
                                                           flag_value=item)
            my_flags.append(formatted_flag)
        flags_string = "".join(my_flags)
        formatted_command_string = "{arg_list}{flags}".format(flags=flags_string,
                                                              arg_list=formatted_command_string)

    # prepend
    formatted_command_string = "{prepend} {arg_list}".format(prepend=prepend,
                                                             arg_list=formatted_command_string)

    if append:
        formatted_command_string = "{arg_list} {append}".format(append=append,
                                                                arg_list=formatted_command_string)

    return formatted_command_string


class OperationWrapper(object):

    def __init__(self, debug=False, log_filename=""):
        self.print_command_strings = debug
        if self.print_command_strings:
            logging.basicConfig(filename=log_filename, level=logging.INFO)
            self.logger = logging.getLogger(__name__)

    def load_commands_from_text_file(self, filename):
        """Reads the contents of a text file and loads each line into a list
        element.

        Args:
            filename (str): Name of file with a list of shell commands on each
            line.

        Returns:
            List(str): A list of shell commands without newlines.
        """
        with open(filename, 'r') as command_file:
            commands = command_file.read().splitlines()

        return commands

    def start_blocking_process(self, command_string):
        """Executes a shell commend. The function will not exit until the shell
        command has completed.

        Args:
            command_string (str): A shell command represented as a string.
        
        Returns:
            str: The shell output of the command.
        """
        if self.print_command_strings:
            self.logger.info(command_string)

        process = os.popen(command_string)
        process_response = process.read()
        process.close()

        return process_response

    def start_non_blocking_process(self, command_string):
        # TODO: Find a lazy way to start a non-blocking process with the
        # multithreading lib? Or maybe async?
        raise NotImplementedError

    def run_list_of_commands(self, list_of_command_strings):
        """Executes each shell command sequentially by iterating though the
        list of commands.

        Args:
            list_of_command_strings (List[str]): A list containing strings
                where each string is a shell command without newlines.
        """
        for command in list_of_command_strings:
            self.start_blocking_process(command_string=command)

    def install(self, command_filename):
        """Reads the contents of command_filename and then runs each install
        command sequentially.

        Args:
            command_filename (str): Name of file with a list of shell commands
            on each line.
        """
        command_list = self.load_commands_from_text_file(command_filename)
        self.run_list_of_commands(command_list)

    def change_permissions(self, permission_code, directory_name,
                           enable_recursion):

        """Uses chmod to change permissions on the specified directory.

        Args:
            permission_code (str): Code used for allocating file/directory
                permissions such as g+wrx. or 755.
            directory_name (str): The name of the file or directory you want to
                edit permissions on.
            enable_recursion (bool): Enable recursion to apply the permission
                code to all files/folders within the directory

        Returns:
            str:: A formatted chmod command string.
        """
        if enable_recursion:
            command = "chmod {code} {dir}".format(code=permission_code,
                                                  dir=directory_name)
        else:
            command = "chmod {code} {dir} -R".format(code=permission_code,
                                                     dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def change_group(self, group_name, directory_name, enable_recursion):

        """Changes user group on the specified directory.

        Args:
            group_name (str): The name of the user group.
            directory_name (str): The name of the directory.
            enable_recursion (bool): Enable recursion to apply the permission
                code to all files/folders within the directory
        
        Returns:
            str: A formatted chgrp command
        """
        if enable_recursion:
            command = "chgrp {grp} {dir}".format(grp=group_name,
                                                 dir=directory_name)
        else:
            command = "chgrp {grp} {dir} -R".format(grp=group_name,
                                                    dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def change_owner(self, new_owner, directory_name, enable_recursion):
        """Changes ownership of the specified directory.

        Args:
             new_owner (str): User to be assigned to the specified directory.
             directory_name (str): Directory to be modified.
             enable_recursion (bool): Enable recursion to apply the owner to
                all files and folders within the directory.

        Returns:
            str: A formatted chown command.
        """
        if enable_recursion:
            command = "chown {own} {dir}".format(own=new_owner,
                                                 dir=directory_name)
        else:
            command = "chgrp {own} {dir} -R".format(own=new_owner,
                                                    dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def add_group(self, group_name):
        """Creates a new group account with default values.

        Args:
            group_name (str): Name of new group.

        Returns:
            str: A formatted groupadd command.
        """
        command = "groupadd {name}".format(name=group_name)
        return self.start_blocking_process(command_string=command)

    def list_my_groups(self):
        """Lists the groups the current user belongs to.

        Returns:
            List(str): List of user's groups as strings.
        """
        command = "groups"

        results = self.start_blocking_process(command_string=command)
        results = str(results).rstrip()
        return results.split(" ")

    def list_user_groups(self, username, verbose=False):
        """Lists the groups a user belongs to.

        Args:
            username (str): User to look up groups for.
            verbose (bool): If verbose, username, uid, gid, and groups will be
                returned as a dictionary. Otherwise, only groups are returned
                as a list. Defaults to False.

        Returns:
            List(str) or dict: Groups the user belongs to.
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
            groups_raw = raw_results[2].replace("groups=",
                                                "").replace(")", "").split(",")
            groups = {}
            for group in groups_raw:
                group_temp = group.split("(")
                groups[group_temp[0]] = group_temp[1]

            final_results = {"username": username, "uid": uid, "gid": gid,
                             "groups": groups}
        else:
            string_to_remove = '{user} : '.format(user=username)
            command = "groups {user}".format(user=username)
            raw_results = self.start_blocking_process(command_string=command)
            raw_results = str(raw_results.rstrip())
            final_results = raw_results.replace(string_to_remove,
                                                "").split(" ")

        return final_results

    def add_new_user(self, username, user_home_directory, user_groups):
        """Adds a new user account to the system.

        Args:
            username (str): Username to be added.
            user_home_directory (str): Directory to assign as user's home
                directory.
            user_groups (str): User groups to add new user to.

        Returns:
            str: Output of useradd command.
        """
        command = "useradd -d {home} -m {user} -G {groups}".format(
            home=user_home_directory,
            user=username,
            groups=user_groups)
        return self.start_blocking_process(command_string=command)

    def set_user_password(self, username, password):
        """Sets or changes password for the specified user.

        Args:
            username (str): User whose password should be changed.
            password (str): User's new password.

        Returns:
            str: Output of chpasswd command.
        """
        command = "echo {user}:{password} | chpasswd".format(user=username,
                                                             password=password)
        return self.start_blocking_process(command_string=command)

    def list_all_groups_on_system(self):
        """Lists all groups on the OS.

        Returns:
            str: Contents of /etc/group
        """
        command = "cat /etc/group"
        return self.start_blocking_process(command_string=command)

    def list_all_users(self):
        """Lists all users on the system.

        Returns:
            str: Output of /etc/passwd
        """
        command = "cat /etc/passwd"

        return self.start_blocking_process(command_string=command)

    def make_directory(self, full_dir_path):
        """Makes a new file directory.

        Args:
            full_dir_path (str): path where the dir should be created.
        """
        mk_dir_command = "mkdir {dir}".format(dir=full_dir_path)
        self.start_blocking_process(command_string=mk_dir_command)

    def move_directory(self, from_directory, to_directory):
        """Moves the specified directory.

        Args:
            from_directory (str): Directory to be moved.
            to_directory (str): New location for directory.

        Returns:
            str: Output of mv command.
        """
        command = "mv {dir1} {dir2}".format(dir1=from_directory,
                                            dir2=to_directory)
        return self.start_blocking_process(command_string=command)

    def copy_directory(self, from_directory, to_directory):
        """Copies the specified directory.

        Args:
            from_directory (str): Directory to be copied.
            to_directory (str): New location for directory.

        Returns:
            str: Output of cp command.
        """
        command = "cp {dir1} {dir2}".format(dir1=from_directory,
                                            dir2=to_directory)
        return self.start_blocking_process(command_string=command)

    def remove_directory(self, directory_name):
        """Removes the specified directory.

        Args:
            directory_name (str): Directory to be removed.

        Returns:
            str: Output of rm command.
        """
        command = "rm {dir}".format(dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def print_working_directory(self):
        """Gets the current working directory.

        Returns:
            str: Location of current working directory.
        """
        command = "pwd"
        return self.start_blocking_process(command_string=command)

    def change_working_directory(self, directory_name):
        """Changes the current working directory.

        Args:
             directory_name (str): Directory to move into.

        Returns:
            str: Output of cd command.
        """
        command = "cd {dir}".format(dir=directory_name)
        return self.start_blocking_process(command_string=command)

    def head_file(self, filename, number_of_lines):
        """Returns the specified number of lines from the beginning of a file.

        Args:
             filename (str): Name of file to parse.
             number_of_lines (int): Number of lines to return.
             
        Returns:
            str: The beginning of the specified file.
        """
        command = "head -n {lines} {file}".format(file=filename,
                                                  lines=number_of_lines)
        return self.start_blocking_process(command_string=command)

    def tail_file(self, filename, number_of_lines):
        """Returns the specified number of lines from the end of a file.

        Args:
             filename (str): Name of file to parse.
             number_of_lines (int): Number of lines to return.
             
        Returns:
            str: The end of the specified file.
        """
        command = "tail -n {lines} {file}".format(file=filename,
                                                  lines=number_of_lines)
        return self.start_blocking_process(command_string=command)

    def view_file_contents(self, filename):
        """Returns a text representation of the entire contents of a file.

        Args:
            filename (str): File whose contents should be returned.
            
        Returns:
            str: String representation of file.
        """

        command = "cat {file}".format(file=filename)
        return self.start_blocking_process(command_string=command)

    def list_files(self, verbose=False):
        """Returns a listing of the files in the current working directory.

        Args:
             verbose (bool): If True, returns a dictionary including each
                item's permissions, score, owner, group, size, month, day,
                time, and filename. Otherwise, returns only a list of names of
                contents. Defaults to False.
        Returns:
            List(str) or dict: Contents of current directory.
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
                filtered_line = list(filter(lambda a: a != "",
                                            split_line))  # remove all ""
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
        """Downloads a file from the Internet.

        Args:
             url (str): URL to retrieve.

        Returns:
            str: Output of wget command.
        """
        command = "wget {url}".format(url=url)
        return self.start_blocking_process(command_string=command)

    def remote_sync(self, from_directory, to_directory):
        """Copies a directory remotely.

        Args:
            from_directory (str): Name of source directory.
            to_directory (str): Name of destination for directory.

        Returns:
            str: Output of rsync command.
        """
        command = "rsync -a {dir1} {dir2}".format(dir1=from_directory,
                                                  dir2=to_directory)
        return self.start_blocking_process(command_string=command)

    def network_addresses(self):
        """Configures kernel-resident network interface.

        Returns:
            str: Output of ifconfig command.
        """
        command = "ifconfig"
        return self.start_blocking_process(command_string=command)

    def list_hardware(self):
        """Gets hardware configuration of machine.

        Returns:
            str: Output of lshw command.
        """
        command = "lshw"
        return self.start_blocking_process(command_string=command)

    def disk_free_space(self):
        """Looks up free disk space on the machine.

        Returns:
            str: Output of df command.
        """
        command = "df -h"
        return self.start_blocking_process(command_string=command)

    def operating_system_information(self):
        """Gets operating system information.

        Returns:
            str: Output of lsb_release command.
        """
        command = "lsb_release -a"
        return self.start_blocking_process(command_string=command)

    def operating_system_kernel_information(self):
        """Gets OS kernel information.

        Returns:
            str: Output of uname command.
        """
        command = "uname -a"
        return self.start_blocking_process(command_string=command)

    def md5_checksum(self, filename):
        """Gets the MD5 checksum of a file.

        Args:
            filename (str): File to find checksum for.

        Returns:
            str: Output of md5sum command.
        """
        command = "md5sum {file}".format(file=filename)
        return self.start_blocking_process(command_string=command)

    def sha1_checksum(self, filename):
        """Gets the SHA1 checksum of a file.

        Args:
            filename (str): File to find checksum for.

        Returns:
            str: Output of sha1sum command.
        """
        command = "sha1sum {file}".format(file=filename)
        return self.start_blocking_process(command_string=command)

    def update_system_packages(self):
        """Synchronizes index files of packages on machine.

        Returns:
            str: Output of apt-get update command.
        """
        command = "apt-get update"
        return self.start_blocking_process(command_string=command)

    def upgrade_system_packages(self):
        """Fetches newest versions of packages on machine.

        Returns:
            str: Output of apt-get upgrade command.
        """
        command = "apt-get upgrade"
        return self.start_blocking_process(command_string=command)

    def install_system_packages(self, package_name):
        """Installs a software package.

        Args:
             package_name (str): Name of package to install.

        Returns:
            str: Output of apt-get install command.
        """
        command = "apt-get install {name}".format(name=package_name)
        return self.start_blocking_process(command_string=command)

    def system_uptime(self):
        """Returns duration the system has been online.

        Returns:
            str: System uptime.
        """
        command = "uptime"
        return self.start_blocking_process(command_string=command)
