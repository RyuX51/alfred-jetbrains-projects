import unittest

import mock

from recent_projects import create_json, Project, find_app_data, find_recentprojects_file, read_projects_from_file, \
    filter_and_sort_projects


class Unittests(unittest.TestCase):
    def setUp(self):
        self.recentProjectsPath = '/Users/JohnSnow/Library/Application Support' \
                                  '/JetBrains/IntelliJIdea2020.2/options/recentProjects.xml'
        self.example_projects_paths = ["~/Documents/spring-petclinic", "~/Desktop/trash/My Project (42)"]

        with mock.patch("os.path.expanduser") as mock_expanduser:
            mock_expanduser.return_value = '/Users/JohnSnow/Documents/spring-petclinic'
            self.example_project = Project(self.example_projects_paths[0])

    @mock.patch('os.path.isfile')
    def test_create_json(self, mock_isfile):
        mock_isfile.return_value = False
        expected = '{"items": [{"type": "file", ' \
                   '"arg": "/Users/JohnSnow/Documents/spring-petclinic", ' \
                   '"subtitle": "/Users/JohnSnow/Documents/spring-petclinic", ' \
                   '"title": "spring-petclinic"}]}'
        self.assertEqual(expected, create_json([self.example_project]))

    @mock.patch("os.path.expanduser")
    @mock.patch('os.path.isfile')
    @mock.patch("__builtin__.open", mock.mock_open(read_data="custom_project_name"))
    def test_create_json_from_custom_name(self, mock_isfile, mock_expand_user):
        mock_expand_user.return_value = '/Users/JohnSnow/Documents/spring-petclinic'
        mock_isfile.return_value = True
        expected = '{"items": [{"type": "file", ' \
                   '"arg": "/Users/JohnSnow/Documents/spring-petclinic", ' \
                   '"subtitle": "/Users/JohnSnow/Documents/spring-petclinic", ' \
                   '"title": "custom_project_name"}]}'
        self.assertEqual(expected, create_json([Project("~/Documents/spring-petclinic")]))

    @mock.patch("__builtin__.open", mock.mock_open(read_data='{"clion": {"folder-name": "CLion","name": "CLion"}}'))
    def test_read_app_data(self):
        self.assertEqual(find_app_data("clion"), {"folder-name": 'CLion', "name": 'CLion'})

        with self.assertRaises(SystemExit) as exitcode:
            find_app_data("rider")
        self.assertEqual(exitcode.exception.code, 1)

    @mock.patch("__builtin__.open")
    def test_read_app_data_products_file_missing(self, mock_open):
        mock_open.side_effect = IOError()
        with self.assertRaises(SystemExit) as exitcode:
            find_app_data("clion")
        self.assertEqual(exitcode.exception.code, 1)

    @mock.patch("os.path.expanduser")
    @mock.patch("os.walk")
    def test_find_recent_files_xml(self, mock_walk, expand_user):
        expand_user.return_value = '/Users/JohnSnow/Library/Application Support/JetBrains/'
        mock_walk.return_value = iter([
            ('/Path',
             ['IntelliJIdea2020.1',
              'IntelliJIdea2020.2',
              'IntelliJIdea2020.2-backup',
              'GoLand2020.1',
              'GoLand2020.2'], []),
        ])
        """Happy Flow"""
        self.assertEqual(find_recentprojects_file({"name": "IntelliJ IDEA", "folder-name": "IntelliJIdea"}),
                         self.recentProjectsPath)

    @mock.patch("__builtin__.open", mock.mock_open(
        read_data='<application>'
                  '<component name="RecentProjectsManager">'
                  '<option name="recentPaths">'
                  '<list>'
                  '<option value="$USER_HOME$/Documents/spring-petclinic" />'
                  '<option value="$USER_HOME$/Desktop/trash/My Project (42)" />'
                  '</list>'
                  '</option>'
                  '</component>'
                  '</application>'))
    def test_read_projects(self):
        self.assertEqual(read_projects_from_file(self.recentProjectsPath), self.example_projects_paths)

    def test_filter_projects(self):
        projects = map(Project, self.example_projects_paths)
        self.assertEqual([Project(self.example_projects_paths[0])], filter_and_sort_projects("petclinic", projects))

    def test_filter_projects_no_query(self):
        projects = map(Project, self.example_projects_paths)
        self.assertEqual(filter_and_sort_projects("", projects), projects)

    def test_project_equals(self):
        project = Project(self.example_projects_paths[0])
        self.assertTrue(project == Project("~/Documents/spring-petclinic"))
        self.assertFalse(project == "some-other-object")

    def test_project_sort_on_match_type(self):
        project = Project(self.example_projects_paths[0])
        self.assertEqual(project.sort_on_match_type("sp"), 0)
        self.assertEqual(project.sort_on_match_type("spring-petclinic"), 1)
        self.assertEqual(project.sort_on_match_type("foobar"), 2)


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
