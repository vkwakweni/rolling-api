from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class GroupKey(ABC):
    """
    Abstract base class for group keys used in the analysis engine.
    
    Each group key represents a unique combination of attributes that define a group for analysis.
    """
    __slots__ = ("hormone_name", "dysmenorrhea_present", "performance_type", "cycle_phase")

    @abstractmethod
    def as_dict(self) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def as_tuple(self) -> tuple:
        raise NotImplementedError


@dataclass(frozen=True)
class HormonePhaseGroupKey(GroupKey):
    hormone_name: str
    cycle_phase: str

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name,
                "cycle_phase": self.cycle_phase}
    
    def as_tuple(self):
        """Convert the group key as a tuple representation."""
        return (self.hormone_name, self.cycle_phase)
    
    def __eq__(self, other):
        """
        Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name and cycle phase.
        """
        return self.hormone_name == other.hormone_name and \
                self.cycle_phase == other.cycle_phase
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': }" + self.hormone_name + \
            ", 'cycle_phase': " + self.cycle_phase


@dataclass(frozen=True)
class HormoneDysmenorrheaPhaseGroupKey(GroupKey):
    """
    Group key that includes hormone name, dysmenorrhea presence, and cycle phase.
    
    This group key is used to analyze the relationship between hormone levels, dysmenorrhea symptoms, and cycle phases.
    
    Attributes:
        hormone_name (str): The name of the hormone being analyzed.
        dysmenorrhea_present (bool): Whether dysmenorrhea symptoms are present.
        cycle_phase (str): The cycle phase the athlete was in.
    """
    hormone_name: str
    dysmenorrhea_present: bool
    cycle_phase: str

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name,
                "dysmenorrhea_present": self.dysmenorrhea_present,
                "cycle_phase": self.cycle_phase}
    
    def as_tuple(self) -> tuple:
        """Convert the group key to a tuple representation."""
        return (self.hormone_name, self.dysmenorrhea_present, self.cycle_phase)
    
    def __eq__(self, other):
        """Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name, dysmenorrhea presence, and performance type.
        """
        return self.hormone_name == other.hormone_name and \
                self.dysmenorrhea_present == other.dysmenorrhea_present and \
                self.cycle_phase == other.cycle_phase
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': " + self.hormone_name + \
            ", 'dysmenorrhea_present': " + str(self.dysmenorrhea_present) + \
                ", 'cycle_phase: " + self.cycle_phase + "}"
    
@dataclass(frozen=True)
class HormonePerformancePhaseGroupKey(GroupKey):
    """
    Group key that includes hormone name, performance type, and cycle phase.
    
    This group key is used to analyze the relationship between hormone levels, performance types, and cycle phases.
    
    Attributes:
        hormone_name (str): The name of the hormone being analyzed.
        performance_type (bool): The name of the performance type.
        cycle_phase (str): The cycle phase the athlete was in.
    """
    hormone_name: str
    performance_type: bool
    cycle_phase: str

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name,
                "performance_type": self.performance_type,
                "cycle_phase": self.cycle_phase}
    
    def as_tuple(self) -> tuple:
        """Convert the group key to a tuple representation."""
        return (self.hormone_name, self.performance_type, self.cycle_phase)
    
    def __eq__(self, other):
        """Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name, performance type, and cycle phase.
        """
        return self.hormone_name == other.hormone_name and \
                self.performance_type == other.performance_type and \
                self.cycle_phase == other.cycle_phase
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': " + self.hormone_name + \
            ", 'performance_type': " + str(self.performance_type) + \
                ", 'cycle_phase: " + self.cycle_phase + "}"


@dataclass(frozen=True)
class HormoneDysmenorrheaPerformanceGroupKey(GroupKey):
    """
    Group key that includes hormone name, dysmenorrhea presence, and performance type.
    
    This group key is used to analyze the relationship between hormone levels, dysmenorrhea symptoms, and performance outcomes.
    
    Attributes:
        hormone_name (str): The name of the hormone being analyzed.
        dysmenorrhea_present (bool): Whether dysmenorrhea symptoms are present.
        performance_type (str): The type of performance being analyzed, representing the intensity of the performance (e.g. 'off season' performance meaning lower intensity, and 'high intensity').
    """

    hormone_name: str
    dysmenorrhea_present: bool
    performance_type: str

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name,
                "dysmenorrhea_present": self.dysmenorrhea_present,
                "performance_type": self.performance_type}
    
    def as_tuple(self) -> tuple:
        """Convert the group key to a tuple representation."""
        return (self.hormone_name, self.dysmenorrhea_present, self.performance_type)
    
    def __eq__(self, other):
        """Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name, dysmenorrhea presence, and performance type.
        """
        return self.hormone_name == other.hormone_name and \
                self.dysmenorrhea_present == other.dysmenorrhea_present and \
                self.performance_type == other.performance_type
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': " + self.hormone_name + \
            ", 'dysmenorrhea_present': " + str(self.dysmenorrhea_present) + \
                ", 'performance_type: " + self.performance_type + "}"
    

@dataclass(frozen=True)
class HormonePerformanceGroupKey(GroupKey):
    """
    Group key that includes hormone name and performance type.
    
    This group key is used to analyze the relationship between hormone levels and performance outcomes.
    
    Attributes:
        hormone_name (str): The name of the hormone being analyzed.
        performance_type (str): The type of performance being analyzed, representing the intensity of the performance (e.g. 'off season' performance meaning lower intensity, and 'high intensity').
    """
    hormone_name: str
    performance_type: str

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name,
                "performance_type": self.performance_type}
    
    def as_tuple(self) -> tuple:
        """Convert the group key to a tuple representation."""
        return (self.hormone_name, self.performance_type)
    
    def __eq__(self, other):
        """Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name and performance type.
        """
        return self.hormone_name == other.hormone_name and \
                self.performance_type == other.performance_type
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': " + self.hormone_name + \
                ", 'performance_type: " + self.performance_type + "}"


@dataclass(frozen=True)
class HormoneDysmenorrheaGroupKey(GroupKey):
    """
    Group key that includes hormone name and dysmenorrhea presence.
    
    This group key is used to analyze the relationship between hormone levels and dysmenorrhea symptoms.
    
    Attributes:
        hormone_name (str): The name of the hormone being analyzed.
        dysmenorrhea_present (bool): Whether dysmenorrhea symptoms are present.
    """
    hormone_name: str
    dysmenorrhea_present: bool

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name,
                "dysmenorrhea_present": self.dysmenorrhea_present}
    
    def as_tuple(self) -> tuple:
        """Convert the group key to a tuple representation."""
        return (self.hormone_name, self.dysmenorrhea_present)
    
    def __eq__(self, other):
        """Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name and dysmenorrhea presence.
        """
        return self.hormone_name == other.hormone_name and \
                self.dysmenorrhea_present == other.dysmenorrhea_present
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': " + self.hormone_name + \
                ", 'performance_type: " + self.performance_type + "}"
    

@dataclass(frozen=True)
class HormoneGroupKey(GroupKey):
    """
    Group key that includes hormone name.
    
    This group key is used to analyze the relationship between hormone levels.
    
    Attributes:
        hormone_name (str): The name of the hormone being analyzed.
    """
    hormone_name: str

    def as_dict(self) -> dict[str, object]:
        """Convert the group key to a dictionary representation."""
        return {"hormone_name": self.hormone_name}
    
    def as_tuple(self) -> tuple:
        """Convert the group key to a tuple representation."""
        return (self.hormone_name,)
    
    def __eq__(self, other):
        """Check for equality between two group keys.
        
        Two group keys are considered equal if they have the same hormone name.
        """
        return self.hormone_name == other.hormone_name
    
    def __str__(self):
        """Return a string representation of the group key."""
        return "\{'hormone_name': " + self.hormone_name + "}"
    