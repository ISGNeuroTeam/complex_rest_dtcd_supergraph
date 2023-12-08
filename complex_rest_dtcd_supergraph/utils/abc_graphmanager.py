from abc import ABC, abstractmethod


class AbstractGraphManager(ABC):

    @abstractmethod
    def read(self, graph_id: str) -> None:
        """Read graph json file by 'graph_id'"""
        pass

    @abstractmethod
    def read_all(self) -> None:
        """Read all graph json files"""
        pass

    @abstractmethod
    def write(self, graph: dict) -> None:
        """Create graph json file with `graph` data"""
        pass

    @abstractmethod
    def update(self, graph: dict) -> None:
        """Rewrite graph json file with `graph` data"""
        pass

    @abstractmethod
    def remove(self, graph_id: str) -> None:
        """Delete graph json file by 'graph_id'"""
        pass
