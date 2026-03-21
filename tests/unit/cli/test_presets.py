"""Template pack presets."""

import pytest

from fastmvc_cli.generator import ProjectGenerator
from fastmvc_cli.presets import apply_template_pack


def test_apply_minimal_disables_redis_and_docker():
    g = ProjectGenerator("x", output_dir="/tmp")
    g.use_redis = True
    g.include_docker_compose = True
    apply_template_pack(g, "minimal")
    assert g.use_redis is False
    assert g.include_docker_compose is False


def test_apply_full_enables_celery_and_identity():
    g = ProjectGenerator("x", output_dir="/tmp")
    g.use_celery = False
    g.use_identity = False
    apply_template_pack(g, "full")
    assert g.use_celery is True
    assert g.use_identity is True


def test_standard_noop():
    g = ProjectGenerator("x", output_dir="/tmp")
    g.use_redis = True
    apply_template_pack(g, "standard")
    assert g.use_redis is True


def test_unknown_pack_raises():
    g = ProjectGenerator("x", output_dir="/tmp")
    with pytest.raises(ValueError, match="Unknown"):
        apply_template_pack(g, "nope")
