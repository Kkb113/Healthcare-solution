"""Versioned data quality, lineage and citation types."""

from dataclasses import dataclass

CONTRACT_VERSION = "hcp-platform-1"


@dataclass(frozen=True)
class Lineage:
    delivery_id: str
    source_file: str
    file_sha256: str
    source_system: str
    source_version: str
    batch_id: str

    def __post_init__(self):
        if (
            not all(
                [
                    self.delivery_id,
                    self.source_file,
                    self.source_system,
                    self.source_version,
                    self.batch_id,
                ]
            )
            or len(self.file_sha256) != 64
            or any(c not in "0123456789abcdef" for c in self.file_sha256)
        ):
            raise ValueError("Incomplete source lineage contract")


@dataclass(frozen=True)
class QualityResult:
    rule_id: str
    checked: int
    failed: int

    def __post_init__(self):
        if (
            not self.rule_id
            or any(
                isinstance(n, bool) or not isinstance(n, int) or n < 0
                for n in [self.checked, self.failed]
            )
            or self.failed > self.checked
        ):
            raise ValueError("Invalid quality counts")


@dataclass(frozen=True)
class Citation:
    evidence_id: str
    source_version: str
    governed_object: str
    scope_version: int
    content_sha256: str

    def __post_init__(self):
        if (
            not self.evidence_id
            or not self.source_version
            or len(self.governed_object.split(".")) != 3
            or self.scope_version < 1
            or len(self.content_sha256) != 64
        ):
            raise ValueError("Incomplete versioned citation")
