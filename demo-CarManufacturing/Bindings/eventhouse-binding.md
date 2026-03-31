# Eventhouse Binding Instructions — Apex Motors Car Manufacturing

## Prerequisites

1. Eventhouse **CarManufacturing_Telemetry** created with KQL database **CarManufacturingDB**
2. Static (Lakehouse) bindings must be completed FIRST for Assembly and Facility
3. CSV data ingested into KQL tables

---

## Assembly Timeseries — AssemblyTelemetry

### Configuration

| Setting | Value |
|---------|-------|
| Entity | Assembly |
| KQL Table | AssemblyTelemetry |
| Key Column | AssemblyId |
| Timestamp Column | Timestamp |

### Property Mappings

| Property | Column | Type |
|----------|--------|------|
| Asm_Torque | Asm_Torque | double |
| Asm_TempC | Asm_TempC | double |
| Asm_CycleTime | Asm_CycleTime | double |

### KQL Ingestion Command

```kql
.ingest into table AssemblyTelemetry (
    h'abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files/Data/Eventhouse/AssemblyTelemetry.csv'
) with (format='csv', ignoreFirstRecord=true)
```

---

## Facility Timeseries — FacilityTelemetry

### Configuration

| Setting | Value |
|---------|-------|
| Entity | Facility |
| KQL Table | FacilityTelemetry |
| Key Column | FacilityId |
| Timestamp Column | Timestamp |

### Property Mappings

| Property | Column | Type |
|----------|--------|------|
| Fac_EnergyKWh | Fac_EnergyKWh | double |
| Fac_Throughput | Fac_Throughput | double |
| Fac_DowntimeMin | Fac_DowntimeMin | double |

### KQL Ingestion Command

```kql
.ingest into table FacilityTelemetry (
    h'abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files/Data/Eventhouse/FacilityTelemetry.csv'
) with (format='csv', ignoreFirstRecord=true)
```

---

## Binding Steps

1. Navigate to the ontology in Fabric IQ
2. Select the entity (Assembly or Facility)
3. Click **Add timeseries binding**
4. Select the Eventhouse and KQL database
5. Choose the KQL table
6. Map the key column and timestamp column
7. Map each timeseries property to its KQL column
8. Save the binding

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| "Static binding required first" | Complete Lakehouse binding for the entity before timeseries |
| "Key column not found" | Ensure KQL table has same key column name as static binding |
| Stale data | Ensure timestamps are recent (within last 7 days) |
