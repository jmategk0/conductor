import unittest
import conductor


class TestCommandStringBuilder(unittest.TestCase):

    def setUp(self):
        self.software_params = {"db": "16s", "out": "results.xml", "num_threads": 2, "outfmt": 5}
        self.software_name = "blastn"
        self.software_flags = ["no_greedy"]

    def test_string_builder_full(self):

        expected_string = "blastn -outfmt 5 -out results.xml -db 16s -num_threads 2 -no_greedy"
        expected_prepend_value = "blastn"

        actual_string = conductor.command_string_builder(
            prepend=self.software_name,
            argument_dictionary=self.software_params,
            flags_list=self.software_flags)

        actual_string_str_array = actual_string.split(" ")
        expected_string_str_array2 = expected_string.split(" ")

        self.assertEquals(expected_prepend_value, actual_string_str_array[0])
        for param in expected_string_str_array2:
            self.assertIn(param, actual_string_str_array)

    def test_string_builder_no_flags(self):

        expected_string = "blastn -outfmt 5 -out results.xml -db 16s -num_threads 2"

        actual_string = conductor.command_string_builder(
            prepend=self.software_name,
            argument_dictionary=self.software_params)

        actual_string_str_array = actual_string.split(" ")
        expected_string_str_array2 = expected_string.split(" ")

        for param in expected_string_str_array2:
            self.assertIn(param, actual_string_str_array)

    def test_string_builder_custom_argument_delimiter(self):

        expected_string = "blastn --outfmt 5 --out results.xml --db 16s --num_threads 2"

        actual_string = conductor.command_string_builder(
            prepend=self.software_name,
            argument_dictionary=self.software_params,
            argument_delimiter="--")

        actual_string_str_array = actual_string.split(" ")
        expected_string_str_array2 = expected_string.split(" ")

        for param in expected_string_str_array2:
            self.assertIn(param, actual_string_str_array)

    def test_string_builder_custom_append(self):

        expected_string = "blastn -outfmt 5 -out results.xml -db 16s -num_threads 2 /test/dir"
        expected_append_value = "/test/dir"

        actual_string = conductor.command_string_builder(
            prepend=self.software_name,
            argument_dictionary=self.software_params,
            append=expected_append_value)

        actual_string_str_array = actual_string.split(" ")
        expected_string_str_array2 = expected_string.split(" ")

        self.assertEquals(expected_append_value, actual_string_str_array[len(actual_string_str_array)-1])
        for param in expected_string_str_array2:
            self.assertIn(param, actual_string_str_array)


class TestOperationWrapperMethods(unittest.TestCase):

    def setUp(self):
        # TODO: Write Tests
        self.ops = conductor.OperationWrapper(debug=True, log_filename="demo.txt")

    def test_load_commands_from_text_file(self):
        pass

    def test_start_blocking_process(self):
        command = "ls"
        expected_result = "conductor.py\nconductor.pyc\nconductorTests.py\ndemo.txt\n__init__.py\n__init__.pyc\n__pycache__\n"

        result = self.ops.start_blocking_process(command_string=command)

        self.assertEquals(expected_result, result)

    def test_make_directory(self):
        pass #TODO: Mock theses tests

    def test_run_list_of_commands(self):
        pass

    def test_install(self):
        pass

string_builder_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCommandStringBuilder)
unittest.TextTestRunner(verbosity=2).run(string_builder_test_suite)

operation_wrapper_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestOperationWrapperMethods)
unittest.TextTestRunner(verbosity=2).run(operation_wrapper_test_suite)
