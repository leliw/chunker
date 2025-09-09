import pytest
from pydantic import ValidationError

from app.features.chunks.chunk_model import ChunksRequest, GcpFile


def test_chunks_request_with_text():
    """
    Tests that ChunksRequest is valid when only 'text' is provided.
    """
    # Given: a valid text
    text = "This is a sample text."
    # When: creating a ChunksRequest with text
    req = ChunksRequest(text=text)
    # Then: the model is created successfully
    assert req.text == text
    assert req.input_file is None


def test_chunks_request_with_input_file():
    """
    Tests that ChunksRequest is valid when only 'input_file' is provided.
    """
    # Given: a valid input file
    input_file = GcpFile(name="file.txt", bucket="my-bucket")
    # When: creating a ChunksRequest with input_file
    req = ChunksRequest(input_file=input_file)
    # Then: the model is created successfully
    assert req.input_file == input_file
    assert req.text is None


def test_chunks_request_with_both_text_and_input_file():
    """
    Tests that ChunksRequest raises a ValueError when both 'text' and 'input_file' are provided.
    """
    with pytest.raises(ValidationError, match="Either 'text' or 'input_file' must be provided, not both."):
        ChunksRequest(text="some text", input_file=GcpFile(name="file.txt"))


def test_chunks_request_with_neither_text_nor_input_file():
    """
    Tests that ChunksRequest raises a ValueError when neither 'text' nor 'input_file' is provided.
    """
    with pytest.raises(ValidationError, match="Either 'text' or 'input_file' must be provided."):
        ChunksRequest()
