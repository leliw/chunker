import pytest
from unittest.mock import MagicMock

# Assuming your load_models.py is in the same directory or accessible via PYTHONPATH
# If load_models.py is in a parent directory (e.g., app/), adjust the import accordingly.
# For example, if your tests directory is at the same level as app/:
# from app.load_models import main  # if load_models.py is in app/
from load_models import main # If load_models.py is in the same dir as tests/ or in PYTHONPATH


@pytest.fixture
def mock_server_config(mocker):
    """Fixture to mock AppConfig."""
    mock_config_instance = MagicMock()
    mock_config_instance.model_names = ["test-model"]
    mock_config_instance.data_dir = "./test_data"
    mocker.patch("load_models.AppConfig", return_value=mock_config_instance)
    return mock_config_instance


@pytest.fixture
def mock_sentence_transformer(mocker):
    """Fixture to mock SentenceTransformer."""
    mock_model_instance = MagicMock()
    mock_st_class = mocker.patch("load_models.SentenceTransformer", return_value=mock_model_instance)
    return mock_st_class, mock_model_instance


@pytest.fixture
def mock_os_makedirs(mocker):
    """Fixture to mock os.makedirs."""
    return mocker.patch("load_models.os.makedirs")


def test_main_successful_load_and_save(
    mock_server_config, mock_sentence_transformer, mock_os_makedirs, capsys
):
    """Test the main function for successful model loading and saving."""
    main()

    # Check if os.makedirs was called correctly
    expected_save_dir = f"{mock_server_config.data_dir}/{mock_server_config.model_names[0]}"
    mock_os_makedirs.assert_called_once_with(expected_save_dir, exist_ok=True)

    # Check if SentenceTransformer was instantiated
    mock_st_class, mock_model_instance = mock_sentence_transformer
    mock_st_class.assert_called_once_with(mock_server_config.model_names[0])

    # Check if model.save was called
    mock_model_instance.save.assert_called_once_with(expected_save_dir)

    # Check printed output
    captured = capsys.readouterr()
    assert f"Loading model '{mock_server_config.model_names[0]}' ..." in captured.out
    assert "loaded successfully." in captured.out
    assert f"saved in directory: {expected_save_dir}" in captured.out
    assert "Process completed." in captured.out


def test_main_model_load_failure(
    mock_server_config, mock_sentence_transformer, mock_os_makedirs, capsys
):
    """Test the main function when model loading fails."""
    mock_st_class, mock_model_instance = mock_sentence_transformer
    mock_st_class.side_effect = Exception("Test load error")

    main()

    # Check if os.makedirs was called
    expected_save_dir = f"{mock_server_config.data_dir}/{mock_server_config.model_names[0]}"
    mock_os_makedirs.assert_called_once_with(expected_save_dir, exist_ok=True)

    # Check if SentenceTransformer was attempted to be instantiated
    mock_st_class.assert_called_once_with(mock_server_config.model_names[0])

    # Ensure model.save was NOT called
    mock_model_instance.save.assert_not_called()

    # Check printed output
    captured = capsys.readouterr()
    assert f"Loading model '{mock_server_config.model_names[0]}' ..." in captured.out
    assert "Error loading model" in captured.out
    assert "Process completed." in captured.out


def test_main_model_save_failure(
    mock_server_config, mock_sentence_transformer, mock_os_makedirs, capsys
):
    """Test the main function when model saving fails."""
    mock_st_class, mock_model_instance = mock_sentence_transformer
    mock_model_instance.save.side_effect = Exception("Test save error")

    main()

    # Check if os.makedirs was called
    expected_save_dir = f"{mock_server_config.data_dir}/{mock_server_config.model_names[0]}"
    mock_os_makedirs.assert_called_once_with(expected_save_dir, exist_ok=True)

    # Check printed output
    captured = capsys.readouterr()
    assert f"Loading model '{mock_server_config.model_names[0]}' ..." in captured.out
    assert "loaded successfully." in captured.out
    assert "Error saving model" in captured.out
    assert "Process completed." in captured.out