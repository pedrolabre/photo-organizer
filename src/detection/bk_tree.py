from typing import TypeVar, Generic, Callable, Dict, List, Tuple, Optional, Iterable

T = TypeVar("T")


class BKNode(Generic[T]):
    def __init__(self, item: T) -> None:
        self.items: List[T] = [item]
        self.children: Dict[int, BKNode[T]] = {}


class BKTree(Generic[T]):
    def __init__(self, distance_fn: Callable[[T, T], int]) -> None:
        self._distance_fn: Callable[[T, T], int] = distance_fn
        self._root: Optional[BKNode[T]] = None
        self._size: int = 0

    @property
    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._root is None

    def clear(self) -> None:
        self._root = None
        self._size = 0

    def insert(self, item: T) -> None:
        if self._root is None:
            self._root = BKNode(item)
            self._size += 1
            return

        current = self._root
        while True:
            dist = self._distance_fn(current.items[0], item)
            if dist == 0:
                current.items.append(item)
                self._size += 1
                return

            if dist not in current.children:
                current.children[dist] = BKNode(item)
                self._size += 1
                return

            current = current.children[dist]

    def add(self, item: T) -> None:
        self.insert(item)

    def build(self, items: Iterable[T]) -> None:
        for item in items:
            self.insert(item)

    def search(self, query: T, max_distance: int) -> List[Tuple[T, int]]:
        if self._root is None:
            return []

        results: List[Tuple[T, int]] = []
        stack: List[BKNode[T]] = [self._root]

        while stack:
            node = stack.pop()
            dist = self._distance_fn(node.items[0], query)

            if dist <= max_distance:
                for item in node.items:
                    results.append((item, dist))

            low = max(0, dist - max_distance)
            high = dist + max_distance

            for edge_dist, child in node.children.items():
                if low <= edge_dist <= high:
                    stack.append(child)

        results.sort(key=lambda pair: pair[1])
        return results
