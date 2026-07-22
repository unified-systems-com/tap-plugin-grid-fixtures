"""Exclusive-Field Fixture Node — the ONLY fixture type carrying `type_exclusive_field`."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel

# The uniform scalar surface every grid_fixtures node type shares (see pg_node), PLUS
# the one field that exists nowhere else. The uniformity of the other types is the
# invariant that makes this type's extra field meaningful: a predicate on
# `type_exclusive_field` can match exactly one node type and no other, by construction.
_FIELD_CRUD_SCHEMA: dict[str, Any] = {
    "name": {"type": "string", "minLength": 1},
    "description": {"type": "string"},
    "kind": {"type": "string"},
    "severity_score": {"type": "integer"},
    "is_open": {"type": "boolean"},
    "observed_at": {"type": ["string", "null"], "format": "date-time"},
    "tags": {"type": "object"},
    "type_exclusive_field": {"type": "string"},
}


class ExclusiveField(BaseModel):
    """Fixture node carrying a data-lane field that NO other fixture type declares.

    A bare, labelless `MATCH (n) WHERE n.data.type_exclusive_field = ...` must scan
    this type and *silently skip* every other node type — a missing property is
    non-matching, not an error (`req-grid-traversal-lang-bare-match-3`). Proving that
    needs a field present on exactly one type: if NO type has the field the executor
    emits no SQL at all, and the scenario passes vacuously without distinguishing
    "silently skipped" from "nothing to do".

    That is not hypothetical. This type exists because the corpus previously borrowed
    `lotr__character.bio` for the job, and when the lotr plugin was retired the scenario
    silently went vacuous. The neutral fixture vocabulary now owns the capability it
    depends on, rather than borrowing it from a demo plugin that can be deleted.

    Deliberately does NOT join the uniform-field-surface family (see models/__init__.py)
    — being the exception IS its testing purpose.

    See plugins/grid_fixtures/README.md.
    """

    ENTITY_TYPE: ClassVar[str] = "grid_fixtures__exclusive_field"
    ENTITY_NAME: ClassVar[str] = "Exclusive-Field Fixture Node"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "Fixture node carrying `type_exclusive_field`, a data-lane field no other fixture type "
        "declares — so a labelless match filtering on it must scan this type alone."
    )

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = _FIELD_CRUD_SCHEMA
    CREATE_REQUIRED: ClassVar[list[str]] = ["name"]
    REPLACE_REQUIRED: ClassVar[list[str]] = ["name"]
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {"tap_viz": {"shape": "ellipse"}}

    # No OUTBOUND_EDGES / INBOUND_EDGES — this type exists for its FIELD surface, not
    # its topology; leaving it unconstrained keeps it out of the constraint archetypes.

    name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    kind = models.CharField(max_length=255, blank=True, default="", db_index=True)
    severity_score = models.IntegerField(default=0, db_index=True)
    is_open = models.BooleanField(default=False)
    observed_at = models.DateTimeField(null=True, blank=True)
    tags = models.JSONField(default=dict, blank=True)
    # The point of the whole type. Not indexed: scenarios assert which TYPES get
    # scanned, never this column's selectivity.
    type_exclusive_field = models.CharField(max_length=255, blank=True, default="")

    class Meta(BaseModel.Meta):
        db_table = "grid_fixtures__exclusive_field"

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name
