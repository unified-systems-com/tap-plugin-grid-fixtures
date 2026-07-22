"""The field-surface exception carries a field no other fixture type declares.

`ExclusiveField` exists so a labelless match can prove that a node type missing a
property is silently non-matching rather than an error. That only works while
`type_exclusive_field` is genuinely exclusive — so the load-bearing assertion here is
the *comparison against every sibling type*, not this model's own field list. If a
future change adds `type_exclusive_field` to another fixture type (or "harmonizes" the
field surfaces), the Gridkin `bare_match__field_absent` scenario silently stops testing
anything, exactly as it did when the borrowed `lotr__character.bio` disappeared. This
test is the tripwire for that.
"""

from __future__ import annotations

import pytest
from tap_plugin.grid_fixtures.models import ExclusiveField

from tap_grid.models import Entity
from tap_grid.services import create_node

_EXCLUSIVE_FIELD = "type_exclusive_field"


@pytest.mark.django_db
class TestExclusivity:
    def test_no_other_fixture_type_declares_the_field(self) -> None:
        """The invariant the Gridkin field-absent scenario stands on."""
        from tap_plugin.grid_fixtures import models as fixture_models

        offenders = []
        for name in fixture_models.__all__:
            model = getattr(fixture_models, name)
            if model is ExclusiveField:
                continue
            if any(f.name == _EXCLUSIVE_FIELD for f in model._meta.get_fields()):
                offenders.append(name)
        assert not offenders, (
            f"{_EXCLUSIVE_FIELD!r} must exist on ExclusiveField and NOWHERE else, but "
            f"{offenders} also declare it. A labelless MATCH filtering on it would now "
            "scan more than one type, and bare_match__field_absent would stop proving "
            "that a type missing the property is silently skipped."
        )

    def test_the_field_is_declared_here(self) -> None:
        assert any(f.name == _EXCLUSIVE_FIELD for f in ExclusiveField._meta.get_fields())

    def test_field_is_exposed_to_the_data_lane(self) -> None:
        """A Gryphon data-lane predicate can only reach declared CRUD fields."""
        assert _EXCLUSIVE_FIELD in ExclusiveField.FIELD_CRUD_SCHEMA


@pytest.mark.django_db
class TestCreateThroughTheServiceLayer:
    def test_creates_with_the_exclusive_field_set(self) -> None:
        result = create_node(
            ExclusiveField.ENTITY_TYPE,
            {"name": "exclusive-1", "type_exclusive_field": "only-here"},
        )
        assert result.success, result.errors
        node = ExclusiveField.objects.get(entity_id=result.entity_id)
        assert node.type_exclusive_field == "only-here"

    def test_entity_name_is_projected_from_get_name(self) -> None:
        """req-grid-node-display — Entity.name is a subordinate projection."""
        result = create_node(ExclusiveField.ENTITY_TYPE, {"name": "exclusive-2"})
        assert result.success, result.errors
        assert Entity.objects.get(pk=result.entity_id).name == "exclusive-2"

    def test_exclusive_field_is_optional(self) -> None:
        """Only `name` is required; the node exists to be SCANNED, not populated."""
        result = create_node(ExclusiveField.ENTITY_TYPE, {"name": "exclusive-3"})
        assert result.success, result.errors
        assert ExclusiveField.objects.get(entity_id=result.entity_id).type_exclusive_field == ""
