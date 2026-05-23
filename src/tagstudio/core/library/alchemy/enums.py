import enum
import random
from dataclasses import dataclass, field, replace
from pathlib import Path

import structlog

from tagstudio.core.query_lang.ast import AST
from tagstudio.core.query_lang.parser import Parser

MAX_SQL_VARIABLES = 32766  # 32766 is the max sql bind parameter count as defined here: https://github.com/sqlite/sqlite/blob/master/src/sqliteLimit.h#L140

logger = structlog.get_logger(__name__)


class TagColorEnum(enum.IntEnum):
    DEFAULT = 1
    BLACK = 2
    DARK_GRAY = 3
    GRAY = 4
    LIGHT_GRAY = 5
    WHITE = 6
    LIGHT_PINK = 7
    PINK = 8
    RED = 9
    RED_ORANGE = 10
    ORANGE = 11
    YELLOW_ORANGE = 12
    YELLOW = 13
    LIME = 14
    LIGHT_GREEN = 15
    MINT = 16
    GREEN = 17
    TEAL = 18
    CYAN = 19
    LIGHT_BLUE = 20
    BLUE = 21
    BLUE_VIOLET = 22
    VIOLET = 23
    PURPLE = 24
    LAVENDER = 25
    BERRY = 26
    MAGENTA = 27
    SALMON = 28
    AUBURN = 29
    DARK_BROWN = 30
    BROWN = 31
    LIGHT_BROWN = 32
    BLONDE = 33
    PEACH = 34
    WARM_GRAY = 35
    COOL_GRAY = 36
    OLIVE = 37

    @staticmethod
    def get_color_from_str(color_name: str) -> "TagColorEnum":
        for color in TagColorEnum:
            if color.name == color_name.upper().replace(" ", "_"):
                return color
        return TagColorEnum.DEFAULT


class ItemType(enum.Enum):
    ENTRY = 0
    COLLATION = 1
    TAG_GROUP = 2


class SortingModeEnum(enum.Enum):
    DATE_ADDED = "file.date_added"
    FILE_NAME = "generic.filename"
    PATH = "file.path"
    RANDOM = "sorting.mode.random"


@dataclass
class BrowsingState:
    """Represent a state of the Library grid view."""

    page_index: int = 0
    page_positions: dict[int, int] = field(default_factory=dict)
    sorting_mode: SortingModeEnum = SortingModeEnum.DATE_ADDED
    ascending: bool = False
    random_seed: float = 0

    show_hidden_entries: bool = False

    query: str | None = None
    text_query: str = ""
    search_tags: bool = False
    search_title: bool = True
    search_prompt: bool = True
    active_tag_filter_ids: frozenset[int] = field(default_factory=frozenset)
    excluded_tag_filter_ids: frozenset[int] = field(default_factory=frozenset)
    category_any_tag_filter_ids: frozenset[int] = field(default_factory=frozenset)

    # Abstract Syntax Tree Of the current Search Query
    @property
    def ast(self) -> AST | None:
        if self.query is None:
            return None
        return Parser(self.query).parse()

    @classmethod
    def show_all(cls) -> "BrowsingState":
        return BrowsingState()

    @classmethod
    def from_search_query(cls, search_query: str) -> "BrowsingState":
        return cls(query=search_query)

    @classmethod
    def from_tag_id(
        cls, tag_id: int | str, state: "BrowsingState | None" = None
    ) -> "BrowsingState":
        """Create and return a BrowsingState object given a tag ID.

        Args:
            tag_id(int): The tag ID to search for.
            state(BrowsingState|None): An optional BrowsingState object to use
                existing options from, such as sorting options.

        """
        logger.warning(state)
        if state:
            return state.with_search_query(f"tag_id:{str(tag_id)}")
        return cls(query=f"tag_id:{str(tag_id)}")

    @classmethod
    def from_path(cls, path: Path | str) -> "BrowsingState":
        return cls(query=f'path:"{str(path).strip()}"')

    @classmethod
    def from_mediatype(cls, mediatype: str) -> "BrowsingState":
        return cls(query=f"mediatype:{mediatype}")

    @classmethod
    def from_filetype(cls, filetype: str) -> "BrowsingState":
        return cls(query=f"filetype:{filetype}")

    @classmethod
    def from_tag_name(cls, tag_name: str) -> "BrowsingState":
        return cls(query=f'tag:"{tag_name}"')

    def with_page_index(self, index: int) -> "BrowsingState":
        return replace(self, page_index=index)

    def with_sorting_mode(self, mode: SortingModeEnum) -> "BrowsingState":
        seed = self.random_seed
        if mode == SortingModeEnum.RANDOM:
            seed = random.random()
        return replace(self, sorting_mode=mode, random_seed=seed)

    def with_sorting_direction(self, ascending: bool) -> "BrowsingState":
        return replace(self, ascending=ascending)

    def with_search_query(self, search_query: str) -> "BrowsingState":
        return replace(self, query=search_query)

    def with_text_query(self, text_query: str) -> "BrowsingState":
        return replace(self, text_query=text_query)

    def with_search_scopes(
        self, *, tags: bool, title: bool, prompt: bool
    ) -> "BrowsingState":
        return replace(self, search_tags=tags, search_title=title, search_prompt=prompt)

    def with_tag_filters(
        self,
        active_tag_filter_ids: set[int] | frozenset[int],
        excluded_tag_filter_ids: set[int] | frozenset[int],
        category_any_tag_filter_ids: set[int] | frozenset[int] | None = None,
    ) -> "BrowsingState":
        return replace(
            self,
            active_tag_filter_ids=frozenset(active_tag_filter_ids),
            excluded_tag_filter_ids=frozenset(excluded_tag_filter_ids),
            category_any_tag_filter_ids=(
                self.category_any_tag_filter_ids
                if category_any_tag_filter_ids is None
                else frozenset(category_any_tag_filter_ids)
            ),
        )

    def with_category_any_tag_filters(
        self, category_any_tag_filter_ids: set[int] | frozenset[int]
    ) -> "BrowsingState":
        return replace(
            self,
            category_any_tag_filter_ids=frozenset(category_any_tag_filter_ids),
        )

    def with_show_hidden_entries(self, show_hidden_entries: bool) -> "BrowsingState":
        return replace(self, show_hidden_entries=show_hidden_entries)


class FieldTypeEnum(enum.Enum):
    TEXT_LINE = "Text Line"
    TEXT_BOX = "Text Box"
    TAGS = "Tags"
    DATETIME = "Datetime"
    BOOLEAN = "Checkbox"
