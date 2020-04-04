import unittest

from utils.eurovision_utils import generate_event_stages

class TimeUtilsTest(unittest.TestCase):
	def test_if_extracted_as_many_events_as_there_are_stages_defined_then_should_generate_each_stage_for_each_event(self):
		stages = ['Semi-final 1', 'Semi-final 2', 'Final']
		generated_stages = generate_event_stages(3, stages, '_')
		self.assertTrue(len(generated_stages) == 3)
		self.assertTrue(generated_stages[0] == 'Semi-final 1')
		self.assertTrue(generated_stages[1] == 'Semi-final 2')
		self.assertTrue(generated_stages[2] == 'Final')

	def test_if_defined_stages_include_repetition_at_beginning_then_should_generate_stages_accordingly(self):
		stages = ['Heat...', 'Final']
		generated_stages = generate_event_stages(6, stages, '_')
		self.assertTrue(len(generated_stages) == 6)
		self.assertTrue(generated_stages[0] == 'Heat 1')
		self.assertTrue(generated_stages[1] == 'Heat 2')
		self.assertTrue(generated_stages[2] == 'Heat 3')
		self.assertTrue(generated_stages[3] == 'Heat 4')
		self.assertTrue(generated_stages[4] == 'Heat 5')
		self.assertTrue(generated_stages[5] == 'Final')

	def test_if_defined_stages_include_repetition_at_beginning_then_should_multiple_single_stage_then_should_generate_stages_accordingly(self):
		stages = ['Heat...', 'Andra Chansen', 'Final']
		generated_stages = generate_event_stages(6, stages, '_')
		self.assertTrue(len(generated_stages) == 6)
		self.assertTrue(generated_stages[0] == 'Heat 1')
		self.assertTrue(generated_stages[1] == 'Heat 2')
		self.assertTrue(generated_stages[2] == 'Heat 3')
		self.assertTrue(generated_stages[3] == 'Heat 4')
		self.assertTrue(generated_stages[4] == 'Andra Chansen')
		self.assertTrue(generated_stages[5] == 'Final')

	def test_if_defined_stages_include_repetition_in_middle_with_single_stages_before_and_after_then_should_generate_stages_accordingly(self):
		stages = ['Opening', 'Heat...', 'Final']
		generated_stages = generate_event_stages(5, stages, '_')
		self.assertTrue(len(generated_stages) == 5)
		self.assertTrue(generated_stages[0] == 'Opening')
		self.assertTrue(generated_stages[1] == 'Heat 1')
		self.assertTrue(generated_stages[2] == 'Heat 2')
		self.assertTrue(generated_stages[3] == 'Heat 3')
		self.assertTrue(generated_stages[4] == 'Final')

	def test_if_defined_stages_include_repetition_at_the_end_with_single_stages_before_then_should_generate_stages_accordingly(self):
		stages = ['Opening', 'Semi-final', 'Final...']
		generated_stages = generate_event_stages(4, stages, '_')
		self.assertTrue(len(generated_stages) == 4)
		self.assertTrue(generated_stages[0] == 'Opening')
		self.assertTrue(generated_stages[1] == 'Semi-final')
		self.assertTrue(generated_stages[2] == 'Final 1')
		self.assertTrue(generated_stages[3] == 'Final 2')

	def test_if_defined_stages_contain_more_than_one_repetition_then_should_apply_default(self):
		stages = ['Heat...', 'Heat...', 'Final']
		generated_stages = generate_event_stages(4, stages, '_')
		self.assertTrue(len(generated_stages) == 4)
		self.assertTrue(generated_stages[0] == 'Night 1')
		self.assertTrue(generated_stages[1] == 'Night 2')
		self.assertTrue(generated_stages[2] == 'Night 3')
		self.assertTrue(generated_stages[3] == 'Final')

	def test_if_less_defined_stages_than_events_then_should_apply_default(self):
		stages = ['Semi-final', 'Final']
		generated_stages = generate_event_stages(3, stages, '_')
		self.assertTrue(len(generated_stages) == 3)
		self.assertTrue(generated_stages[0] == 'Night 1')
		self.assertTrue(generated_stages[1] == 'Night 2')
		self.assertTrue(generated_stages[2] == 'Final')

	def test_if_less_events_than_defined_stages_then_should_use_latest_stages(self):
		stages = ['Opening', 'Semi-final', 'Final']
		generated_stages = generate_event_stages(2, stages, '_')
		self.assertTrue(len(generated_stages) == 2)
		self.assertTrue(generated_stages[0] == 'Semi-final')
		self.assertTrue(generated_stages[1] == 'Final')

	def test_if_repetition_expression_only_applied_once_then_should_not_include_number(self):
		stages = ['Semi-final...', 'Final']
		generated_stages = generate_event_stages(2, stages, '_')
		self.assertTrue(len(generated_stages) == 2)
		self.assertTrue(generated_stages[0] == 'Semi-final')
		self.assertTrue(generated_stages[1] == 'Final')