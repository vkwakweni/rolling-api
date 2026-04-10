from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class GroupKey(ABC):
    __slots__ = ("hormone_name", "dysmenorrhea_present", "performance_type")
    @abstractmethod
    def as_dict(self) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def as_tuple(self) -> tuple:
        raise NotImplementedError


@dataclass(frozen=True)
class HormoneDysmenorrheaPerformanceGroupKey(GroupKey):
    hormone_name: str
    dysmenorrhea_present: bool
    performance_type: str

    def as_dict(self) -> dict[str, object]:
        return {"hormone_name": self.hormone_name,
                "dysmenorrhea_present": self.dysmenorrhea_present,
                "performance_type": self.performance_type}
    
    def as_tuple(self) -> tuple:
        return (self.hormone_name, self.dysmenorrhea_present, self.performance_type)
    
    def __eq__(self, other):
        return self.hormone_name == other.hormone_name and \
                self.dysmenorrhea_present == other.dysmenorrhea_present and \
                self.performance_type == other.performance_type
    
    def __str__(self):
        return "\{'hormone_name': " + self.hormone_name + \
            ", 'dysmenorrhea_present': " + str(self.dysmenorrhea_present) + \
                ", 'performance_type: " + self.performance_type + "}"
    

@dataclass(frozen=True)
class HormonePerformanceGroupKey(GroupKey):
    hormone_name: str
    performance_type: str

    def as_dict(self) -> dict[str, object]:
        return {"hormone_name": self.hormone_name,
                "performance_type": self.performance_type}
    
    def as_tuple(self) -> tuple:
        return (self.hormone_name, self.performance_type)
    
    def __eq__(self, other):
        return self.hormone_name == other.hormone_name and \
                self.performance_type == other.performance_type
    
    def __str__(self):
        return "\{'hormone_name': " + self.hormone_name + \
                ", 'performance_type: " + self.performance_type + "}"


@dataclass(frozen=True)
class HormoneDysmenorrheaGroupKey(GroupKey):
    hormone_name: str
    dysmenorrhea_present: str

    def as_dict(self) -> dict[str, object]:
        return {"hormone_name": self.hormone_name,
                "dysmenorrhea_present": self.dysmenorrhea_present}
    
    def as_tuple(self) -> tuple:
        return (self.hormone_name, self.dysmenorrhea_present)
    
    def __eq__(self, other):
        return self.hormone_name == other.hormone_name and \
                self.dysmenorrhea_present == other.dysmenorrhea_present
    
    def __str__(self):
        return "\{'hormone_name': " + self.hormone_name + \
                ", 'performance_type: " + self.performance_type + "}"
    

@dataclass(frozen=True)
class HormoneGroupKey(GroupKey):
    hormone_name: str

    def as_dict(self) -> dict[str, object]:
        return {"hormone_name": self.hormone_name}
    
    def as_tuple(self) -> tuple:
        return (self.hormone_name,)
    
    def __eq__(self, other):
        return self.hormone_name == other.hormone_name
    
    def __str__(self):
        return "\{'hormone_name': " + self.hormone_name + "}"
    