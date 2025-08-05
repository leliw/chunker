import pytest
from unittest.mock import MagicMock

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

# Assuming tests are run from the root of the chunker project or PYTHONPATH is set appropriately
from app.features.chunks.recursive_splitter import RecursiveSplitter


@pytest.fixture
def mock_sentence_transformer_for_splitter() -> MagicMock:
    """
    Provides a mocked SentenceTransformer instance.
    The tokenize method is mocked to simulate tokenization where the number of tokens
    is equal to the number of words in the input string. This is used by the
    length_function in RecursiveSplitter.
    """
    model = MagicMock(spec=SentenceTransformer)

    def mock_tokenize_for_length_function(texts_list: list[str]):
        # This mock is for the length_function:
        # lambda t: len(self.model.tokenize([t])["input_ids"].tolist()[0])
        # So, model.tokenize is called with a list containing a single string `[t]`.
        if not texts_list or len(texts_list) != 1:
            # This case should ideally not be hit if called as self.model.tokenize([t])
            # For robustness, return something or raise error.
            # Based on SentenceTransformer behavior, it can handle multiple texts.
            # However, for this specific length_function, it's always one.
            # Let's stick to the expected input of one string in the list.
            raise ValueError(
                "mock_tokenize_for_length_function expects a list with a single string for this test setup"
            )

        text_item = texts_list[0]
        words = text_item.split()
        # This is the list of "tokens" whose length will be taken.
        # For example, if text_item has 5 words, this will be [0, 1, 2, 3, 4].
        actual_token_list = list(range(len(words)))

        # The RecursiveSplitter expects self.model.tokenize([t])["input_ids"]
        # to be an object with a .tolist() method.
        # .tolist() should return a list, and .tolist()[0] should be our actual_token_list.
        mock_input_ids_object = MagicMock()
        mock_input_ids_object.tolist.return_value = [actual_token_list]
        return {"input_ids": mock_input_ids_object}

    model.tokenize = MagicMock(side_effect=mock_tokenize_for_length_function)
    return model


def test_recursive_splitter_simple_case(mock_sentence_transformer_for_splitter: MagicMock):
    """Tests basic splitting functionality."""
    chunk_size = 5  # 5 "tokens" (words in our mock)
    chunk_overlap = 1 # 1 "token" (word in our mock)
    splitter = RecursiveSplitter(
        model=mock_sentence_transformer_for_splitter,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    test_text = "This is a simple sentence for testing the splitter functionality."
    # Word count: 10 words.
    # Expected chunks (based on word count as length):
    # 1. "This is a simple sentence" (5 words)
    # 2. "sentence for testing the splitter" (5 words, overlap "sentence")
    # 3. "splitter functionality." (2 words, overlap "splitter")
    expected_chunks_content = [
        "This is a simple sentence",
        "sentence for testing the splitter",
        "splitter functionality.",
    ]

    documents = splitter.split(test_text)

    assert len(documents) == len(expected_chunks_content)
    for i, doc in enumerate(documents):
        assert isinstance(doc, Document)
        assert doc.page_content == expected_chunks_content[i]
    # Check if tokenize was called (it's called by the length_function)
    mock_sentence_transformer_for_splitter.tokenize.assert_called()


def test_recursive_splitter_with_long_text_and_overlap(
    mock_sentence_transformer_for_splitter: MagicMock,
):
    """Tests splitting with specified overlap on a longer text."""
    chunk_size = 4
    chunk_overlap = 2
    splitter = RecursiveSplitter(
        model=mock_sentence_transformer_for_splitter,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    test_text = "one two three four five six seven eight nine ten"  # 10 words
    # Expected chunks:
    # 1. "one two three four" (length 4)
    # 2. "three four five six" (length 4, overlap "three four")
    # 3. "five six seven eight" (length 4, overlap "five six")
    # 4. "seven eight nine ten" (length 4, overlap "seven eight")
    expected_chunks_content = [
        "one two three four",
        "three four five six",
        "five six seven eight",
        "seven eight nine ten",
    ]

    documents = splitter.split(test_text)

    assert len(documents) == len(expected_chunks_content)
    for i, doc in enumerate(documents):
        assert isinstance(doc, Document)
        assert doc.page_content == expected_chunks_content[i]
    mock_sentence_transformer_for_splitter.tokenize.assert_called()


def test_recursive_splitter_text_shorter_than_chunk_size(
    mock_sentence_transformer_for_splitter: MagicMock,
):
    """Tests behavior when text is shorter than chunk_size."""
    chunk_size = 10
    chunk_overlap = 2
    splitter = RecursiveSplitter(
        model=mock_sentence_transformer_for_splitter,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    test_text = "This text is short."  # 4 words
    expected_chunks_content = ["This text is short."]

    documents = splitter.split(test_text)

    assert len(documents) == 1
    assert isinstance(documents[0], Document)
    assert documents[0].page_content == expected_chunks_content[0]
    mock_sentence_transformer_for_splitter.tokenize.assert_called()


def test_recursive_splitter_empty_text(mock_sentence_transformer_for_splitter: MagicMock):
    """Tests behavior with empty input text."""
    chunk_size = 5
    chunk_overlap = 1
    splitter = RecursiveSplitter(
        model=mock_sentence_transformer_for_splitter,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    test_text = ""
    # Langchain's RecursiveCharacterTextSplitter([text]) with text=""
    # results in [Document(page_content="")]
    documents = splitter.split(test_text)

    assert len(documents) == 1
    assert isinstance(documents[0], Document)
    assert documents[0].page_content == ""


def test_recursive_splitter_with_newlines(mock_sentence_transformer_for_splitter: MagicMock):
    """Tests splitting behavior with newline characters, relying on default separators."""
    chunk_size = 7  # words
    chunk_overlap = 1 # word
    splitter = RecursiveSplitter(
        model=mock_sentence_transformer_for_splitter,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    test_text = "Line one has four words.\n\nLine two also four words. Then a short one."
    # Piece 1: "Line one has four words." (4 words) -> Chunk 1
    # Piece 2: "Line two also four words. Then a short one." (8 words) -> needs splitting
    #   - "Line two also four words. Then a" (7 words) -> Chunk 2
    #   - "a short one." (2 words, overlap "short") -> Chunk 3
    expected_chunks_content = [
        "Line one has four words.",
        "Line two also four words. Then a",
        "a short one.",
    ]

    documents = splitter.split(test_text)

    assert len(documents) == len(expected_chunks_content)
    for i, doc in enumerate(documents):
        assert isinstance(doc, Document)
        assert doc.page_content == expected_chunks_content[i]
    mock_sentence_transformer_for_splitter.tokenize.assert_called()