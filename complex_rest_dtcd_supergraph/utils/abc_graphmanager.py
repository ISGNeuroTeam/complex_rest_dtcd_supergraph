from abc import ABC, abstractmethod


class AbstractGraphManager(ABC):

    @abstractmethod
    def read(self, graph_id: str) -> None:
        pass

    @abstractmethod
    def read_all(self) -> None:
        pass

    @abstractmethod
    def write(self, graph: dict) -> None:
        pass

    @abstractmethod
    def update(self, graph: dict) -> None:
        pass

    @abstractmethod
    def remove(self, graph_id: str) -> None:
        pass
