from unittest import mock

import pytest

from antareslauncher.use_cases.check_remote_queue.slurm_queue_show import (
    SlurmQueueShow,
)


@pytest.mark.unit_test
def test_when_slurm_queue_show_runs_then_env_get_queue_info_is_called_and_message_is_displayed():
    # given
    env_mock = mock.Mock()
    display_mock = mock.Mock()
    queue_info = "queue info"
    env_mock.get_queue_info = mock.Mock(return_value=queue_info)
    slurm_queue_show = SlurmQueueShow(env=env_mock, display=display_mock)
    message = "Checking remote server queue\n" + queue_info
    # when
    slurm_queue_show.run()
    # then
    env_mock.get_queue_info.assert_called_once()
    display_mock.show_message.assert_called_once_with(message, mock.ANY)
