from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestingToolsDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requirements = (ROOT / 'requirements.txt').read_text(encoding='utf-8')
        cls.readme = (ROOT / 'README.md').read_text(encoding='utf-8')

    def test_development_requirements_include_test_and_performance_tools(self):
        for dependency in ('pytest>=', 'locust>=', 'coverage>='):
            with self.subTest(dependency=dependency):
                self.assertIn(dependency, self.requirements)

    def test_runtime_and_test_tools_share_the_same_requirements_file(self):
        self.assertIn('Flask>=', self.requirements)

    def test_readme_documents_installation_test_and_coverage_commands(self):
        for command in (
            'python -m pip install -r requirements.txt',
            'python -m pytest',
            'python -m coverage run -m pytest',
            'python -m coverage report',
            'python -m coverage html',
            'locust --version',
        ):
            with self.subTest(command=command):
                self.assertIn(command, self.readme)


if __name__ == '__main__':
    unittest.main()
