# Lakehouse Binding Instructions — Apex Motors Car Manufacturing

## Prerequisites

1. **Disable OneLake Security** on the Lakehouse (Settings → OneLake Security → Off)
2. Lakehouse schemas must be **disabled** (Public Preview)
3. All CSV files uploaded to `Files/Data/Lakehouse/` and loaded as Delta tables

---

## Entity Bindings

### 1. Vehicle → DimVehicle

| Property | Column | Type |
|----------|--------|------|
| VehicleId (KEY) | VehicleId | string |
| Vehicle_VIN | Vehicle_VIN | string |
| Vehicle_Model | Vehicle_Model | string |
| Vehicle_Year | Vehicle_Year | int |
| Vehicle_Color | Vehicle_Color | string |
| Vehicle_Status | Vehicle_Status | string |

> Note: Timeseries properties are not applicable to Vehicle.

### 2. Assembly → DimAssembly

| Property | Column | Type |
|----------|--------|------|
| AssemblyId (KEY) | AssemblyId | string |
| Assembly_Name | Assembly_Name | string |
| Assembly_Kind | Assembly_Kind | string |
| Assembly_Station | Assembly_Station | string |

> Note: Timeseries properties (Asm_Torque, Asm_TempC, Asm_CycleTime) are bound separately via Eventhouse.

### 3. Component → DimComponent

| Property | Column | Type |
|----------|--------|------|
| ComponentId (KEY) | ComponentId | string |
| Comp_Name | Comp_Name | string |
| Comp_PartNumber | Comp_PartNumber | string |
| Comp_LotBatch | Comp_LotBatch | string |

### 4. Facility → DimFacility

| Property | Column | Type |
|----------|--------|------|
| FacilityId (KEY) | FacilityId | string |
| Facility_Name | Facility_Name | string |
| Facility_Location | Facility_Location | string |
| Facility_Capacity | Facility_Capacity | int |

> Note: Timeseries properties (Fac_EnergyKWh, Fac_Throughput, Fac_DowntimeMin) are bound separately via Eventhouse.

### 5. Supplier → DimSupplier

| Property | Column | Type |
|----------|--------|------|
| SupplierId (KEY) | SupplierId | string |
| Supplier_Name | Supplier_Name | string |
| Supplier_Region | Supplier_Region | string |
| Supplier_Rating | Supplier_Rating | double |

### 6. ProdOrder → DimProdOrder

| Property | Column | Type |
|----------|--------|------|
| ProdOrderId (KEY) | ProdOrderId | string |
| ProdOrd_Qty | ProdOrd_Qty | int |
| ProdOrd_Status | ProdOrd_Status | string |
| ProdOrd_DueDate | ProdOrd_DueDate | datetime |

---

## Relationship Bindings

All relationships use dedicated Edge tables with columns matching entity key names exactly.

| Relationship | Edge Table | Source Key | Target Key |
|-------------|------------|------------|------------|
| BUILT_AT | EdgeVehicleFacility | VehicleId | FacilityId |
| ASSEMBLED_INTO | EdgeAssemblyVehicle | AssemblyId | VehicleId |
| USES_COMPONENT | EdgeAssemblyComponent | AssemblyId | ComponentId |
| SUPPLIED_BY | EdgeComponentSupplier | ComponentId | SupplierId |
| PRODUCED_AT | EdgeOrderFacility | ProdOrderId | FacilityId |
| ORDERS_VEHICLE | EdgeOrderVehicle | ProdOrderId | VehicleId |
| SHIPS_TO | EdgeSupplierFacility | SupplierId | FacilityId |

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| "Cannot bind - OneLake security enabled" | Disable OneLake Security in Lakehouse settings |
| "Missing mapping for key property" | Ensure key column is listed as first property in bindings |
| "targetKeyColumn mismatch" | Column name must exactly match target entity's key name |
| "Property not unique" | Each property name must be unique across ALL entities |
