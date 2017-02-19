import unittest
import conductor


class TestOperationWrapperMethods(unittest.TestCase):

    def setUp(self):
        # TODO: Write Tests
        self.test_dataset = ""

    def test_string_builder(self):
        data = {"db": "16s", "out": "results.xml", "num_threads": 2, "outfmt": 5}
        name = "blastn"
        flags = ["no_greedy"]
        my_string = conductor.command_string_builder(prepend=name, commands_dict=data, flags_list=flags)
        ex_string = "blastn -outfmt 5 -out results.xml -db 16s -num_threads 2 -no_greedy"
        array1 = my_string.split(" ")
        array2 = ex_string.split(" ")
        for item in array2:
            self.assertIn(item, array1)
