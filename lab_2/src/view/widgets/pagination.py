import math
from typing import Callable, List, TypeVar

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QWidget

T = TypeVar("T")


class Paginator:
    def __init__(self, page_size: int = 10) -> None:
        self.page_size = page_size
        self.current_page = 1

    def total_pages(self, total_items: int) -> int:
        if total_items == 0:
            return 1
        return math.ceil(total_items / self.page_size)

    def slice(self, items: List[T]) -> List[T]:
        if not items:
            return []
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return items[start:end]

    def clamp_page(self, total_items: int) -> None:
        max_page = self.total_pages(total_items)
        if self.current_page > max_page:
            self.current_page = max_page
        if self.current_page < 1:
            self.current_page = 1


class PaginationBar(QWidget):
    """Панель постраничного вывода."""

    def __init__(
        self,
        parent: QWidget | None,
        on_change: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self.paginator = Paginator()
        self._total_items = 0

        layout = QHBoxLayout(self)

        layout.addWidget(QLabel("Записей на странице:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(1, 100)
        self.page_size_spin.setValue(10)
        self.page_size_spin.valueChanged.connect(self._apply_page_size)
        layout.addWidget(self.page_size_spin)

        for text, slot in (
            ("|<", self.first),
            ("<", self.prev),
            (">", self.next),
            (">|", self.last),
        ):
            btn = QPushButton(text)
            btn.setFixedWidth(36)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        self.info_label = QLabel("")
        layout.addWidget(self.info_label)
        layout.addStretch()

    def _apply_page_size(self) -> None:
        self.paginator.page_size = self.page_size_spin.value()
        self.paginator.current_page = 1
        self._on_change()

    def update_info(self, total_items: int, on_page: int) -> None:
        self._total_items = total_items
        self.paginator.clamp_page(total_items)
        page = self.paginator.current_page
        pages = self.paginator.total_pages(total_items)
        self.info_label.setText(
            f"Стр. {page} из {pages} | "
            f"на странице: {on_page} | "
            f"всего записей: {total_items}"
        )

    def first(self) -> None:
        self.paginator.current_page = 1
        self._on_change()

    def prev(self) -> None:
        self.paginator.current_page = max(1, self.paginator.current_page - 1)
        self._on_change()

    def next(self) -> None:
        max_page = self.paginator.total_pages(self._total_items)
        self.paginator.current_page = min(max_page, self.paginator.current_page + 1)
        self._on_change()

    def last(self) -> None:
        self.paginator.current_page = self.paginator.total_pages(self._total_items)
        self._on_change()
