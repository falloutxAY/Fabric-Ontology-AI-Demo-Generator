"""
Regression tests for setup-mode Kusto binding cluster URI handling.

These tests verify that ``_step_configure_bindings`` correctly:

1. Retrieves the Eventhouse cluster URI via ``_get_eventhouse_cluster_uri()``.
2. Fails fast (FAILED status) when the cluster URI is unavailable.
3. Passes ``cluster_uri`` to ``add_eventhouse_binding()``, so generated
   KustoTable bindings include ``sourceTableProperties.clusterUri``.

Also verifies that ``DataBinding.to_dict()`` includes ``clusterUri`` when
provided and omits it when absent.
"""

import base64
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from demo_automation.binding.binding_builder import (
    BindingType,
    DataBinding,
    OntologyBindingBuilder,
    PropertyBinding,
    SourceType,
)
from demo_automation.binding.binding_parser import (
    ParsedEntityBinding,
    ParsedPropertyMapping,
)
from demo_automation.binding.yaml_parser import YamlBindingsConfig
from demo_automation.core.config import (
    DemoConfiguration,
    DemoOptions,
    FabricConfig,
    ResourceConfig,
    ResourcesConfig,
)
from demo_automation.orchestrator import DemoOrchestrator, SetupState, StepStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _encode_json_to_base64(obj: dict) -> str:
    """Encode *obj* as base64-encoded JSON (matches Fabric API payload format)."""
    return base64.b64encode(json.dumps(obj).encode("utf-8")).decode("utf-8")


def _make_config(tmp_path: Path) -> DemoConfiguration:
    """Return a minimal ``DemoConfiguration`` that avoids touching the filesystem."""
    return DemoConfiguration(
        name="TestDemo",
        demo_path=tmp_path,
        fabric=FabricConfig(workspace_id="ws-001"),
        resources=ResourcesConfig(
            eventhouse=ResourceConfig(name="TestEventhouse"),
        ),
        options=DemoOptions(skip_existing=True),
    )


def _make_orchestrator(tmp_path: Path) -> DemoOrchestrator:
    """Return an orchestrator wired with a fake config and mocked state manager."""
    config = _make_config(tmp_path)
    with patch("demo_automation.orchestrator.SetupStateManager"):
        orch = DemoOrchestrator(config)

    # Pre-populate state as if earlier steps already ran
    orch.state = SetupState(
        eventhouse_id="eventhouse-001",
        kql_database_id="kqldb-001",
        ontology_id="ontology-001",
    )
    return orch


def _make_yaml_config() -> YamlBindingsConfig:
    """Return a ``YamlBindingsConfig`` with one eventhouse entity binding."""
    entity_binding = ParsedEntityBinding(
        entity_name="Sensor",
        table_name="SensorTelemetry",
        key_column="SensorId",
        binding_type="timeseries",
        property_mappings=[
            ParsedPropertyMapping(
                source_column="SensorId",
                target_property="SensorId",
            ),
            ParsedPropertyMapping(
                source_column="Temperature",
                target_property="Temperature",
            ),
        ],
    )
    return YamlBindingsConfig(eventhouse_entities=[entity_binding])


def _make_ontology_definition(entity_id: str = "ent-sensor-001") -> dict:
    """
    Return a minimal Fabric ontology definition dict with one entity part.

    The entity part matches the ``Sensor`` entity used in ``_make_yaml_config``.
    """
    entity_payload = {
        "id": entity_id,
        "name": "Sensor",
        "properties": [
            {"id": "prop-sensor-id", "name": "SensorId"},
            {"id": "prop-temperature", "name": "Temperature"},
        ],
    }
    return {
        "definition": {
            "parts": [
                {
                    "path": f"EntityTypes/{entity_id}/entity.json",
                    "payload": _encode_json_to_base64(entity_payload),
                }
            ]
        }
    }


# ---------------------------------------------------------------------------
# DataBinding.to_dict() tests
# ---------------------------------------------------------------------------

class TestDataBindingToDict:
    """Unit tests for DataBinding.to_dict() cluster URI serialisation."""

    def test_includes_cluster_uri_when_provided(self):
        """to_dict() must include clusterUri in sourceTableProperties when cluster_uri is set."""
        binding = DataBinding(
            binding_id="bid-001",
            entity_type_id="ent-001",
            binding_type=BindingType.TIME_SERIES,
            source_type=SourceType.KUSTO_TABLE,
            workspace_id="ws-001",
            item_id="eventhouse-001",
            table_name="SensorTelemetry",
            key_column="SensorId",
            timestamp_column="Timestamp",
            database_name="TelemetryDB",
            cluster_uri="https://test-cluster.kusto.fabric.microsoft.com",
            property_bindings=[
                PropertyBinding(
                    source_column="SensorId",
                    target_property_id="prop-sensor-id",
                ),
            ],
        )

        result = binding.to_dict()

        source_props = result["dataBindingConfiguration"]["sourceTableProperties"]
        assert source_props["sourceType"] == "KustoTable"
        assert source_props["databaseName"] == "TelemetryDB"
        assert source_props["clusterUri"] == "https://test-cluster.kusto.fabric.microsoft.com"

    def test_omits_cluster_uri_when_not_provided(self):
        """to_dict() must not include clusterUri when cluster_uri is None."""
        binding = DataBinding(
            binding_id="bid-002",
            entity_type_id="ent-001",
            binding_type=BindingType.TIME_SERIES,
            source_type=SourceType.KUSTO_TABLE,
            workspace_id="ws-001",
            item_id="eventhouse-001",
            table_name="SensorTelemetry",
            key_column="SensorId",
            timestamp_column="Timestamp",
            database_name="TelemetryDB",
            cluster_uri=None,
            property_bindings=[],
        )

        result = binding.to_dict()

        source_props = result["dataBindingConfiguration"]["sourceTableProperties"]
        assert "clusterUri" not in source_props


# ---------------------------------------------------------------------------
# _step_configure_bindings regression tests
# ---------------------------------------------------------------------------

class TestStepConfigureBindings:
    """Regression tests for cluster URI handling in _step_configure_bindings."""

    # ------------------------------------------------------------------
    # Helpers / fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def orch(self, tmp_path: Path) -> DemoOrchestrator:
        return _make_orchestrator(tmp_path)

    # ------------------------------------------------------------------
    # Fail-fast: missing cluster URI
    # ------------------------------------------------------------------

    def test_fails_when_cluster_uri_unavailable(self, orch: DemoOrchestrator):
        """
        _step_configure_bindings must return FAILED when the Eventhouse cluster
        URI cannot be retrieved, instead of creating a broken KustoTable binding.
        """
        yaml_config = _make_yaml_config()
        ontology_def = _make_ontology_definition()

        orch._check_cancellation = MagicMock()  # no-op
        orch._report_progress = MagicMock()  # no-op

        mock_fc = MagicMock()
        mock_fc.get_ontology_definition.return_value = ontology_def
        mock_fc.get_kql_database.return_value = {"displayName": "TelemetryDB"}
        orch._fabric_client = mock_fc

        # Simulate cluster URI being unavailable
        orch._get_eventhouse_cluster_uri = MagicMock(return_value=None)

        with patch(
            "demo_automation.orchestrator.parse_bindings_yaml",
            return_value=yaml_config,
        ):
            result = orch._step_configure_bindings()

        assert result.status == StepStatus.FAILED
        assert "clusterUri" in result.message or "cluster URI" in result.message.lower()

    # ------------------------------------------------------------------
    # Success path: cluster URI present in generated binding
    # ------------------------------------------------------------------

    def test_includes_cluster_uri_in_kusto_binding(self, orch: DemoOrchestrator):
        """
        _step_configure_bindings must pass cluster_uri to add_eventhouse_binding
        so that generated KustoTable binding parts contain clusterUri.
        """
        cluster_uri = "https://test-cluster.kusto.fabric.microsoft.com"
        yaml_config = _make_yaml_config()
        ontology_def = _make_ontology_definition()

        orch._check_cancellation = MagicMock()
        orch._report_progress = MagicMock()

        captured_parts: list[dict] = []

        # Capture the definition parts passed to update_ontology_definition.
        # The orchestrator calls it as:
        #   update_ontology_definition(ontology_id=..., definition={"parts": [...]})
        def capture_update(ontology_id, definition):
            captured_parts.extend(definition.get("parts", []))

        mock_fc = MagicMock()
        # First call: build entity map; second call: post-upload validation.
        # Return a definition with a DataBindings part on the second call so
        # the count check passes.
        binding_validation_part = {
            "path": "EntityTypes/ent-sensor-001/DataBindings/test-binding.json",
            "payload": _encode_json_to_base64({"dataBindingConfiguration": {}}),
        }
        validation_def = {
            "definition": {
                "parts": [binding_validation_part],
            }
        }
        mock_fc.get_ontology_definition.side_effect = [ontology_def, validation_def]
        mock_fc.get_kql_database.return_value = {"displayName": "TelemetryDB"}
        mock_fc.update_ontology_definition.side_effect = capture_update
        orch._fabric_client = mock_fc

        orch._get_eventhouse_cluster_uri = MagicMock(return_value=cluster_uri)

        # Suppress state-manager save
        orch._state_manager = MagicMock()

        with patch(
            "demo_automation.orchestrator.parse_bindings_yaml",
            return_value=yaml_config,
        ):
            result = orch._step_configure_bindings()

        assert result.status == StepStatus.COMPLETED, (
            f"Expected COMPLETED but got {result.status}: {result.message}"
        )

        # Decode captured definition parts and find KustoTable bindings
        kusto_bindings = []
        for part in captured_parts:
            payload_b64 = part.get("payload", "")
            if not payload_b64:
                continue
            try:
                payload = json.loads(base64.b64decode(payload_b64).decode("utf-8"))
            except Exception:
                continue
            config = payload.get("dataBindingConfiguration", {})
            source_props = config.get("sourceTableProperties", {})
            if source_props.get("sourceType") == "KustoTable":
                kusto_bindings.append(source_props)

        assert kusto_bindings, "No KustoTable binding parts were uploaded"
        for source_props in kusto_bindings:
            assert "clusterUri" in source_props, (
                f"KustoTable binding is missing clusterUri: {source_props}"
            )
            assert source_props["clusterUri"] == cluster_uri

    # ------------------------------------------------------------------
    # Verify cluster URI retrieval is attempted
    # ------------------------------------------------------------------

    def test_get_eventhouse_cluster_uri_is_called(self, orch: DemoOrchestrator):
        """
        _step_configure_bindings must call _get_eventhouse_cluster_uri() when
        eventhouse entities are present in the binding configuration.
        """
        yaml_config = _make_yaml_config()
        ontology_def = _make_ontology_definition()

        orch._check_cancellation = MagicMock()
        orch._report_progress = MagicMock()
        orch._state_manager = MagicMock()

        mock_fc = MagicMock()
        mock_fc.get_ontology_definition.return_value = ontology_def
        mock_fc.get_kql_database.return_value = {"displayName": "TelemetryDB"}
        orch._fabric_client = mock_fc

        mock_get_uri = MagicMock(return_value=None)
        orch._get_eventhouse_cluster_uri = mock_get_uri

        with patch(
            "demo_automation.orchestrator.parse_bindings_yaml",
            return_value=yaml_config,
        ):
            orch._step_configure_bindings()

        mock_get_uri.assert_called_once()
