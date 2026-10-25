from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReadmeInstallationInstructionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        cls.requirements = (ROOT / 'requirements.txt').read_text(encoding='utf-8')

    def test_documents_virtual_environment_setup_for_all_platforms(self):
        for command in (
            'python3 -m venv .venv',
            'source .venv/bin/activate',
            'py -3 -m venv .venv',
            r'.venv\Scripts\Activate.ps1',
            r'.venv\Scripts\activate.bat',
        ):
            with self.subTest(command=command):
                self.assertIn(command, self.readme)

    def test_documents_dependency_installation_and_flask_launch(self):
        for instruction in (
            'python -m pip install -r requirements.txt',
            'FLASK_APP=server',
            'FLASK_SECRET_KEY',
            'flask run',
            'http://127.0.0.1:5000',
        ):
            with self.subTest(instruction=instruction):
                self.assertIn(instruction, self.readme)

    def test_flask_requirement_is_current_and_not_pinned_to_legacy_dependencies(self):
        self.assertIn('Flask>=3.1,<4', self.requirements)
        self.assertNotIn('Flask==1.1.2', self.requirements)


if __name__ == '__main__':
    unittest.main()
