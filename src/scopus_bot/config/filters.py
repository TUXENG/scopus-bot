from typing import Final


SUBJECT_AREA_TEST_IDS: Final[dict[str, str]] = {
    "Engineering": "facet-option-ENGI",
    "Materials Science": "facet-option-MATE",
    "Environmental Science": "facet-option-ENVI",
    "Earth and Planetary Sciences": "facet-option-EART",
}


DOCUMENT_TYPE_TEST_IDS: Final[dict[str, str]] = {
    "Article": "facet-option-ar",
    "Review": "facet-option-re",
    "Conference paper": "facet-option-cp",
}

DOCUMENT_TYPE_NAMES: Final[list[str]] = [
    "Article",
    "Review",
    "Conference paper",
]


NUM_PAGES: Final[int] = 2
FILTER_YEAR_TO: Final[int] = 2025