import pytest
from unittest.mock import MagicMock, patch

# Assuming your load_model.py is in the same directory or accessible via PYTHONPATH
# If load_model.py is in a parent directory (e.g., app/), adjust the import accordingly.
# For example, if your tests directory is at the same level as app/:
# from app.load_model import main  # if load_model.py is in app/
from load_model import main # If load_model.py is in the same dir as tests/ or in PYTHONPATH


@pytest.fixture
def mock_server_config(mocker):
    """Fixture to mock ServerConfig."""
    mock_config_instance = MagicMock()
    mock_config_instance.model_name = "test-model"
    mock_config_instance.data_dir = "./test_data"
    mocker.patch("load_model.ServerConfig", return_value=mock_config_instance)
    return mock_config_instance


@pytest.fixture
def mock_sentence_transformer(mocker):
    """Fixture to mock SentenceTransformer."""
    mock_model_instance = MagicMock()
    mock_st_class = mocker.patch("load_model.SentenceTransformer", return_value=mock_model_instance)
    return mock_st_class, mock_model_instance


@pytest.fixture
def mock_os_makedirs(mocker):
    """Fixture to mock os.makedirs."""
    return mocker.patch("load_model.os.makedirs")


def test_main_successful_load_and_save(
    mock_server_config, mock_sentence_transformer, mock_os_makedirs, capsys
):
    """Test the main function for successful model loading and saving."""
    main()

    # Check if os.makedirs was called correctly
    expected_save_dir = f"{mock_server_config.data_dir}/{mock_server_config.model_name}"
    mock_os_makedirs.assert_called_once_with(expected_save_dir, exist_ok=True)

    # Check if SentenceTransformer was instantiated
    mock_st_class, mock_model_instance = mock_sentence_transformer
    mock_st_class.assert_called_once_with(mock_server_config.model_name)

    # Check if model.save was called
    mock_model_instance.save.assert_called_once_with(expected_save_dir)

    # Check printed output
    captured = capsys.readouterr()
    assert f"Loading model '{mock_server_config.model_name}' ..." in captured.out
    assert "Model loaded successfully." in captured.out
    assert f"Model saved in directory: {expected_save_dir}" in captured.out
    assert "Process completed." in captured.out


def test_main_model_load_failure(
    mock_server_config, mock_sentence_transformer, mock_os_makedirs, capsys
):
    """Test the main function when model loading fails."""
    mock_st_class, mock_model_instance = mock_sentence_transformer
    mock_st_class.side_effect = Exception("Test load error")

    main()

    # Check if os.makedirs was called
    expected_save_dir = f"{mock_server_config.data_dir}/{mock_server_config.model_name}"
    mock_os_makedirs.assert_called_once_with(expected_save_dir, exist_ok=True)

    # Check if SentenceTransformer was attempted to be instantiated
    mock_st_class.assert_called_once_with(mock_server_config.model_name)

    # Ensure model.save was NOT called
    mock_model_instance.save.assert_not_called()

    # Check printed output
    captured = capsys.readouterr()
    assert f"Loading model '{mock_server_config.model_name}' ..." in captured.out
    assert "Error loading model: Test load error" in captured.out
    assert "Process completed." in captured.out


def test_main_model_save_failure(
    mock_server_config, mock_sentence_transformer, mock_os_makedirs, capsys
):
    """Test the main function when model saving fails."""
    mock_st_class, mock_model_instance = mock_sentence_transformer
    mock_model_instance.save.side_effect = Exception("Test save error")

    main()

    # Check if os.makedirs was called
    expected_save_dir = f"{mock_server_config.data_dir}/{mock_server_config.model_name}"
    mock_os_makedirs.assert_called_once_with(expected_save_dir, exist_ok=True)

    # Check printed output
    captured = capsys.readouterr()
    assert f"Loading model '{mock_server_config.model_name}' ..." in captured.out
    assert "Model loaded successfully." in captured.out
    assert "Error saving model: Test save error" in captured.out
    assert "Process completed." in captured.out