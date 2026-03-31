# Apex Motors — Car Manufacturing Demo

## Overview

**Company**: Apex Motors  
**Domain**: Automotive Manufacturing & Supply Chain  
**Use Case**: Production traceability — tracking vehicle assembly, component sourcing, supplier networks, and production orders across multiple manufacturing facilities.

This demo models a car manufacturing operation with 6 entity types, 7 relationships, and timeseries telemetry from assembly stations and facility operations.

---

## Entity & Relationship Summary

| Entity | Key | Records | Timeseries |
|--------|-----|---------|------------|
| Vehicle | VehicleId | 15 | — |
| Assembly | AssemblyId | 20 | Torque, Temperature, Cycle Time |
| Component | ComponentId | 15 | — |
| Facility | FacilityId | 3 | Energy, Throughput, Downtime |
| Supplier | SupplierId | 5 | — |
| ProdOrder | ProdOrderId | 5 | — |

| Relationship | Source → Target |
|-------------|----------------|
| BUILT_AT | Vehicle → Facility |
| ASSEMBLED_INTO | Assembly → Vehicle |
| USES_COMPONENT | Assembly → Component |
| SUPPLIED_BY | Component → Supplier |
| PRODUCED_AT | ProdOrder → Facility |
| ORDERS_VEHICLE | ProdOrder → Vehicle |
| SHIPS_TO | Supplier → Facility |

---

## Folder Structure

```
demo-CarManufacturing/
├── README.md
├── .demo-metadata.yaml
├── demo-questions.md
├── ontology-structure.md
├── Bindings/
│   ├── bindings.yaml
│   ├── lakehouse-binding.md
│   └── eventhouse-binding.md
├── Data/
│   ├── Lakehouse/
│   │   ├── DimVehicle.csv
│   │   ├── DimAssembly.csv
│   │   ├── DimComponent.csv
│   │   ├── DimFacility.csv
│   │   ├── DimSupplier.csv
│   │   ├── DimProdOrder.csv
│   │   ├── EdgeVehicleFacility.csv
│   │   ├── EdgeAssemblyVehicle.csv
│   │   ├── EdgeAssemblyComponent.csv
│   │   ├── EdgeComponentSupplier.csv
│   │   ├── EdgeOrderFacility.csv
│   │   ├── EdgeOrderVehicle.csv
│   │   └── EdgeSupplierFacility.csv
│   └── Eventhouse/
│       ├── AssemblyTelemetry.csv
│       └── FacilityTelemetry.csv
└── Ontology/
    ├── car-manufacturing.ttl
    └── ontology-diagram-slide.html
```

---

## Prerequisites

- Microsoft Fabric workspace with capacity
- Fabric IQ (Ontology) enabled
- Lakehouse with OneLake Security **disabled**
- Eventhouse with KQL database
- `fabric-demo` CLI tool installed (`pip install -e Demo-automation/`)

---

## Quick Start

```bash
# 1. Configure workspace
python -m demo_automation config init

# 2. Validate the demo package
python -m demo_automation validate demo-CarManufacturing

# 3. Run full setup
python -m demo_automation setup demo-CarManufacturing
```

---

## Known Limitations

- Lakehouse OneLake Security must be disabled for data binding
- Each entity supports only one static (Lakehouse) binding
- GQL queries have a maximum of 8 hops for variable-length paths
- Query results are truncated at 64MB

---

## Demo Scenarios

### Scenario 1: Recall Investigation
A defective piston batch (LOT-2026-0301) is reported. Trace which vehicles are affected by querying Component → Assembly → Vehicle to identify all VINs for targeted recall.

### Scenario 2: Facility Risk Assessment
Evaluate supplier concentration at the Detroit plant. Query which suppliers ship to FAC-001 and how many component links pass through each supplier to assess single-source risk.

### Scenario 3: Production Order Tracking
Track production order PO-001 from order through vehicle assembly to final facility. Verify all vehicles are built at the correct assigned plant and check completion status.
