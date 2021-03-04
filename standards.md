# standards

Limit blank lines to what is suggested to pep8
For example in the tests:

```python
    def test_given_repo_when_get_list_of_studies_called_then_repo_get_list_of_studies_is_called(self):
        # given
        repo_mock = mock.Mock()
        repo_mock.get_list_of_studies = mock.Mock()
        study_list_composer = StudyListComposer(repo=repo_mock, file_system=None)
        # when
        study_list_composer.get_list_of_studies()
        # then
        repo_mock.get_list_of_studies.assert_called_once()
```

The class do not need to inherit from `object`

Instead of
```python
class LaunchController(object):
    def __init__(self):
        pass
```
use
```python
class LaunchController:
    def __init__(self):
        pass
```
