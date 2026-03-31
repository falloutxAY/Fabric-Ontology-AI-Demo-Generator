# Demo Questions — Apex Motors Car Manufacturing

---

## Question 1: Component Traceability

**Business Question**: Which suppliers provided components used in vehicle VH-001?

**Why It Matters**: When a quality issue is found in a finished vehicle, manufacturers must rapidly trace back through assemblies to the source components and their suppliers for recall assessment.

### Graph Traversal

```
Vehicle (VH-001) ←[ASSEMBLED_INTO]← Assembly -[USES_COMPONENT]→ Component -[SUPPLIED_BY]→ Supplier
```

### GQL Query

```gql
MATCH (a:Assembly)-[:ASSEMBLED_INTO]->(v:Vehicle),
      (a)-[:USES_COMPONENT]->(c:Component)-[:SUPPLIED_BY]->(s:Supplier)
FILTER v.VehicleId = 'VH-001'
LET assemblyName = a.Assembly_Name
LET componentName = c.Comp_Name
LET partNumber = c.Comp_PartNumber
LET supplierName = s.Supplier_Name
LET supplierRegion = s.Supplier_Region
RETURN assemblyName, componentName, partNumber, supplierName, supplierRegion
ORDER BY assemblyName
```

### Expected Results

| assemblyName | componentName | partNumber | supplierName | supplierRegion |
|-------------|---------------|------------|-------------|----------------|
| Chassis Frame C1 | Steel Frame Rail | PN-20101 | Global Chassis Corp | Southeast |
| Chassis Frame C1 | Cross Member | PN-20102 | Global Chassis Corp | Southeast |
| Dashboard Unit D1 | Instrument Cluster | PN-30101 | TechDash Electronics | West Coast |
| Dashboard Unit D1 | HVAC Module | PN-30102 | TechDash Electronics | West Coast |
| Engine Block A1 | Piston Set | PN-10201 | Premier Auto Parts | Midwest |
| Engine Block A1 | Crankshaft | PN-10202 | Premier Auto Parts | Midwest |
| Engine Block A1 | Turbocharger | PN-10204 | Premier Auto Parts | Midwest |

### Why Ontology is Better

| Approach | Effort |
|----------|--------|
| **Traditional SQL** | 4-table JOIN across DimVehicle, EdgeAssemblyVehicle, EdgeAssemblyComponent, EdgeComponentSupplier with nested subqueries |
| **Ontology Graph** | Single MATCH pattern following natural relationships — no joins, no subqueries |

---

## Question 2: Supplier Impact Analysis

**Business Question**: Which vehicles contain components from supplier Premier Auto Parts?

**Why It Matters**: If a supplier reports a defective batch, the manufacturer needs to instantly identify every affected vehicle for targeted recalls instead of broad fleet-wide actions.

### Graph Traversal

```
Supplier (SUP-001) ←[SUPPLIED_BY]← Component ←[USES_COMPONENT]← Assembly -[ASSEMBLED_INTO]→ Vehicle
```

### GQL Query

```gql
MATCH (c:Component)-[:SUPPLIED_BY]->(s:Supplier),
      (a:Assembly)-[:USES_COMPONENT]->(c),
      (a)-[:ASSEMBLED_INTO]->(v:Vehicle)
FILTER s.SupplierId = 'SUP-001'
LET vehicleVIN = v.Vehicle_VIN
LET vehicleModel = v.Vehicle_Model
LET vehicleStatus = v.Vehicle_Status
LET componentName = c.Comp_Name
RETURN vehicleVIN, vehicleModel, vehicleStatus, componentName
ORDER BY vehicleVIN
```

### Expected Results

| vehicleVIN | vehicleModel | vehicleStatus | componentName |
|-----------|-------------|---------------|---------------|
| 1APEX2026A0000001 | Apex Sedan X | Completed | Piston Set |
| 1APEX2026A0000001 | Apex Sedan X | Completed | Crankshaft |
| 1APEX2026A0000001 | Apex Sedan X | Completed | Turbocharger |
| 1APEX2026A0000002 | Apex Sedan X | Completed | Piston Set |
| 1APEX2026A0000002 | Apex Sedan X | Completed | Cylinder Head |
| 1APEX2026A0000003 | Apex SUV Z | Completed | Crankshaft |
| 1APEX2026A0000003 | Apex SUV Z | Completed | Exhaust Manifold |
| 1APEX2026A0000005 | Apex Coupe R | In Assembly | Piston Set |
| 1APEX2026A0000005 | Apex Coupe R | In Assembly | Turbocharger |
| 1APEX2026A0000009 | Apex Sedan X | In Assembly | Crankshaft |

### Why Ontology is Better

| Approach | Effort |
|----------|--------|
| **Traditional SQL** | Reverse-direction multi-JOIN from Supplier → Component → Assembly → Vehicle across 4 tables |
| **Ontology Graph** | Natural reverse traversal in a single MATCH — the graph handles direction automatically |

---

## Question 3: Production Order Fulfillment

**Business Question**: Which vehicles are associated with production order PO-001 and where were they built?

**Why It Matters**: Production managers need to track order fulfillment status and verify that vehicles were manufactured at the assigned facility.

### Graph Traversal

```
ProdOrder (PO-001) -[ORDERS_VEHICLE]→ Vehicle -[BUILT_AT]→ Facility
```

### GQL Query

```gql
MATCH (po:ProdOrder)-[:ORDERS_VEHICLE]->(v:Vehicle)-[:BUILT_AT]->(f:Facility)
FILTER po.ProdOrderId = 'PO-001'
LET vehicleVIN = v.Vehicle_VIN
LET vehicleModel = v.Vehicle_Model
LET vehicleStatus = v.Vehicle_Status
LET facilityName = f.Facility_Name
LET facilityLocation = f.Facility_Location
RETURN vehicleVIN, vehicleModel, vehicleStatus, facilityName, facilityLocation
ORDER BY vehicleVIN
```

### Expected Results

| vehicleVIN | vehicleModel | vehicleStatus | facilityName | facilityLocation |
|-----------|-------------|---------------|-------------|-----------------|
| 1APEX2026A0000001 | Apex Sedan X | Completed | Apex Detroit Plant | Detroit MI |
| 1APEX2026A0000002 | Apex Sedan X | Completed | Apex Detroit Plant | Detroit MI |
| 1APEX2026A0000006 | Apex Sedan X | Quality Check | Apex Detroit Plant | Detroit MI |
| 1APEX2026A0000009 | Apex Sedan X | In Assembly | Apex Detroit Plant | Detroit MI |
| 1APEX2026A0000012 | Apex Sedan X | Completed | Apex Detroit Plant | Detroit MI |

### Why Ontology is Better

| Approach | Effort |
|----------|--------|
| **Traditional SQL** | JOIN EdgeOrderVehicle → DimVehicle → EdgeVehicleFacility → DimFacility |
| **Ontology Graph** | Two-hop MATCH pattern directly follows the business relationship chain |

---

## Question 4: Facility Supplier Network

**Business Question**: Which suppliers ship to the Apex Detroit Plant?

**Why It Matters**: Supply chain managers need visibility into which suppliers serve each plant for logistics planning and risk assessment of single-source dependencies.

### Graph Traversal

```
Supplier -[SHIPS_TO]→ Facility (FAC-001)
```

### GQL Query

```gql
MATCH (s:Supplier)-[:SHIPS_TO]->(f:Facility)
FILTER f.FacilityId = 'FAC-001'
LET supplierName = s.Supplier_Name
LET supplierRegion = s.Supplier_Region
LET supplierRating = s.Supplier_Rating
LET facilityName = f.Facility_Name
RETURN supplierName, supplierRegion, supplierRating, facilityName
ORDER BY supplierRating DESC
```

### Expected Results

| supplierName | supplierRegion | supplierRating | facilityName |
|-------------|---------------|----------------|-------------|
| TechDash Electronics | West Coast | 4.9 | Apex Detroit Plant |
| Premier Auto Parts | Midwest | 4.8 | Apex Detroit Plant |
| SafeStop Brakes | Midwest | 4.7 | Apex Detroit Plant |
| Global Chassis Corp | Southeast | 4.5 | Apex Detroit Plant |

### Why Ontology is Better

| Approach | Effort |
|----------|--------|
| **Traditional SQL** | JOIN EdgeSupplierFacility → DimSupplier with WHERE on FacilityId |
| **Ontology Graph** | Simple one-hop MATCH with filter — reads like a natural question |

---

## Question 5: Multi-Hop Full Traceability

**Business Question**: For each facility, how many distinct suppliers provide components through the assembly chain?

**Why It Matters**: Executives need a high-level view of supplier concentration per plant to assess supply chain risk and diversification.

### Graph Traversal

```
Facility ←[BUILT_AT]← Vehicle ←[ASSEMBLED_INTO]← Assembly -[USES_COMPONENT]→ Component -[SUPPLIED_BY]→ Supplier
```

### GQL Query

```gql
MATCH (a:Assembly)-[:ASSEMBLED_INTO]->(v:Vehicle)-[:BUILT_AT]->(f:Facility),
      (a)-[:USES_COMPONENT]->(c:Component)-[:SUPPLIED_BY]->(s:Supplier)
LET facilityName = f.Facility_Name
LET supplierName = s.Supplier_Name
RETURN facilityName, supplierName, count(*) AS componentLinks
GROUP BY facilityName, supplierName
ORDER BY facilityName, componentLinks DESC
```

### Expected Results

| facilityName | supplierName | componentLinks |
|-------------|-------------|----------------|
| Apex Austin Plant | Premier Auto Parts | 3 |
| Apex Austin Plant | DriveForce Systems | 2 |
| Apex Austin Plant | TechDash Electronics | 2 |
| Apex Austin Plant | Global Chassis Corp | 1 |
| Apex Detroit Plant | Premier Auto Parts | 5 |
| Apex Detroit Plant | Global Chassis Corp | 3 |
| Apex Detroit Plant | TechDash Electronics | 3 |
| Apex Nashville Plant | Global Chassis Corp | 3 |
| Apex Nashville Plant | TechDash Electronics | 2 |
| Apex Nashville Plant | DriveForce Systems | 2 |

### Why Ontology is Better

| Approach | Effort |
|----------|--------|
| **Traditional SQL** | 5-table JOIN chain with GROUP BY — extremely complex, error-prone, slow |
| **Ontology Graph** | 4-hop MATCH with GROUP BY — the graph engine handles traversal optimization |

---

## Data Agent Instructions

Support group by in GQL.

You are a data agent for the Apex Motors Car Manufacturing ontology. This ontology models the production traceability of vehicles, assemblies, components, suppliers, facilities, and production orders.

### Entity Types
- **Vehicle** (key: VehicleId) — Finished vehicles with VIN, model, year, color, status
- **Assembly** (key: AssemblyId) — Major assemblies (engine, chassis, interior, drivetrain) with timeseries: torque, temperature, cycle time
- **Component** (key: ComponentId) — Individual parts with part numbers and lot batches
- **Facility** (key: FacilityId) — Manufacturing plants with location and capacity; timeseries: energy, throughput, downtime
- **Supplier** (key: SupplierId) — Parts suppliers with region and rating
- **ProdOrder** (key: ProdOrderId) — Production orders with quantity, status, due date

### Relationships
- Vehicle -[BUILT_AT]→ Facility
- Assembly -[ASSEMBLED_INTO]→ Vehicle
- Assembly -[USES_COMPONENT]→ Component
- Component -[SUPPLIED_BY]→ Supplier
- ProdOrder -[PRODUCED_AT]→ Facility
- ProdOrder -[ORDERS_VEHICLE]→ Vehicle
- Supplier -[SHIPS_TO]→ Facility

### GQL Syntax Rules
- Use `MATCH` with patterns, not `SELECT`
- Use `FILTER` for conditions (not `WHERE` after MATCH)
- Use `LET` to alias properties before `RETURN`
- Aggregations (`count`, `sum`, `avg`) REQUIRE `GROUP BY` with all non-aggregated expressions
- Use bounded quantifiers `{1,N}` for variable-length paths (max 8 hops)
- No `OPTIONAL MATCH` (not supported)
- Use `ZONED_DATETIME()` for datetime literals
- Results must be under 64MB
