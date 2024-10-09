"""
test_prompt_context_activities.py
"""

import os, json
import unittest
from unittest.mock import patch
from colorama import Fore, Style
# test package imports
import altered.settings as sts
from altered.renderer import Render
import altered.hlp_printing as hlpp
from altered.prompt_context_activities import ContextActivities


class Test_ContextActivities(unittest.TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        """
        Set up class-level test data and configuration.
        """
        cls.verbose = 0
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.renderer = Render(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        """
        Clean up after the tests if necessary.
        """
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        """
        Load test data from the actual test activity log.
        """
        test_data_path = os.path.join(sts.test_data_dir, "test_activity_log.json")
        activities = []
        
        if os.path.exists(test_data_path):
            with open(test_data_path, 'r') as f:
                activities = [json.loads(line.strip()) for line in f]

        return activities

    def test___init__(self, *args, **kwargs):
        """
        Test the initialization of the ContextActivities class.
        """
        # Initialize the class with a test log file
        ContextActivities.logs_dir = sts.test_data_dir
        context_activities = ContextActivities()

        # Assert that the context is initialized correctly
        self.assertIsInstance(context_activities.context, dict)
        self.assertIn('activities', context_activities.context)

    def test_load_activities(self, *args, **kwargs):
        """
        Test the loading of activities from the log file into the context.
        """
        context_activities = ContextActivities(log_file_path=os.path.join(
                                            sts.test_data_dir, "test_activity_log.json"))
        context_activities.load_activities()

        # Check that activities have been loaded into the context
        self.assertEqual(len(context_activities.context['activities']), len(self.test_data))
        self.assertEqual(context_activities.context['activities'][0]['application_name'], 
                                                    self.test_data[0]['application_name'])

    def test_get_activities_results(self, *args, **kwargs):
        """
        Test retrieving the most recent activities from the context.
        """
        context_activities = ContextActivities(log_file_path=os.path.join(
                                            sts.test_data_dir, "test_activity_log.json"))
        context_activities.load_activities()

        # Test retrieving activities
        results = context_activities.get_activities_results(num_activities=2)
        self.assertEqual(len(results['activities']), 2)
        self.assertEqual(results['activities'][0]['application_name'], self.test_data[-2]['application_name'])
        self.assertEqual(results['activities'][1]['application_name'], self.test_data[-1]['application_name'])

        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name=ContextActivities.template_name,
                                            context = {'context': results},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)


    def test_load_git_diffs_unmocked(self):
        # Initialize the ContextActivities instance
        context_activities = ContextActivities()

        # Call load_git_diffs with 2 changes
        context_activities.load_git_diffs(num_changes=2)

if __name__ == "__main__":
    unittest.main()
