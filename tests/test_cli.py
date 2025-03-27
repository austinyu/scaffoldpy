"""Test the CLI functions in scaffoldpy.cli."""

from scaffoldpy.cli import (
    prompt_for_project_config,
    prompt_for_user_config,
)
from scaffoldpy.models import DEFAULT_PROJECT_CONFIG


def test_prompt_for_user_config(mocker):
    """Test the prompt_for_user_config function."""
    # Mock user inputs with invalid (empty) input first, then valid input
    mock_inquirer = mocker.patch("scaffoldpy.cli.inquirer")
    mock_inquirer.text.return_value.execute.side_effect = [
        "John Doe",
        "john.doe@example.com",
    ]

    # Call the function
    result = prompt_for_user_config(None)

    # Assert the result
    assert result == {
        "author": "John Doe",
        "author_email": "john.doe@example.com",
    }
    assert mock_inquirer.text.call_count == 2


def test_prompt_for_project_config(mocker):
    """Test the prompt_for_project_config function."""
    # Mock user inputs with invalid (empty) input first, then valid input
    mock_inquirer = mocker.patch("scaffoldpy.cli.inquirer")
    mock_inquirer.text.return_value.execute.side_effect = [
        DEFAULT_PROJECT_CONFIG["project_name"],
    ]

    mock_inquirer.select.return_value.execute.side_effect = [
        DEFAULT_PROJECT_CONFIG["min_py_version"],
        DEFAULT_PROJECT_CONFIG["layout"],
        DEFAULT_PROJECT_CONFIG["build_backend"],
        DEFAULT_PROJECT_CONFIG["spell_checker"],
        DEFAULT_PROJECT_CONFIG["docs"],
        DEFAULT_PROJECT_CONFIG["code_editor"],
        DEFAULT_PROJECT_CONFIG["cloud_code_base"],
    ]

    mock_inquirer.checkbox.return_value.execute.side_effect = [
        DEFAULT_PROJECT_CONFIG["static_code_checkers"],
        DEFAULT_PROJECT_CONFIG["formatters"],
    ]

    mock_inquirer.confirm.return_value.execute.side_effect = [
        DEFAULT_PROJECT_CONFIG["pre_commit"]
    ]

    # Call the function
    result = prompt_for_project_config(None)

    # Assert the result
    assert result == DEFAULT_PROJECT_CONFIG
