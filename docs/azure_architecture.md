# Azure Backend Architectuur - HSO Data Extractor

## Overzicht

De HSO Data Extractor gebruikt een serverless Azure architectuur voor schaalbare en kosteneffectieve documentverwerking. De architectuur is ontworpen voor het verwerken van inkooporders (PDFs) en het extraheren van gestructureerde data.

## Architectuur Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │  Azure Function  │    │  Azure Blob     │
│   Frontend      │───▶│     App          │───▶│    Storage      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                           │
                              ▼                           │
                       ┌──────────────────┐              │
                       │ Azure Computer   │              │
                       │    Vision        │              │
                       │  (OCR Service)   │              │
                       └──────────────────┘              │
                              │                           │
                              ▼                           │
                       ┌──────────────────┐              │
                       │   Azure Key      │◀─────────────┘
                       │     Vault        │
                       │ (Secrets/Keys)   │
                       └──────────────────┘
```

## Azure Services

### 1. Azure Functions (Serverless Compute)

**Function App: `hso-data-extractor-functions`**

#### Functions:

1. **`convert_pdf_to_text`**
   - **Trigger**: HTTP POST
   - **Input**: PDF bestand (multipart/form-data)
   - **Output**: Geëxtraheerde tekst + blob URL
   - **Timeout**: 5 minuten
   - **Memory**: 1.5 GB

2. **`extract_purchase_order_data`**
   - **Trigger**: HTTP POST  
   - **Input**: Geëxtraheerde tekst (JSON)
   - **Output**: Gestructureerde data + confidence score
   - **Timeout**: 2 minuten
   - **Memory**: 512 MB

3. **`cleanup_old_files`** (Timer)
   - **Trigger**: Daily at 02:00 UTC
   - **Function**: Cleanup temporary files > 24h
   - **Memory**: 256 MB

#### Configuration:
```json
{
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  },
  "host": {
    "cors": {
      "allowedOrigins": ["*"],
      "supportCredentials": false
    }
  }
}
```

### 2. Azure Blob Storage

**Storage Account: `hsodataextractorstorage`**

#### Containers:

1. **`documents`** (Hot tier)
   - Originele PDF bestanden
   - Geëxtraheerde tekst bestanden
   - Processed JSON data
   - Retention: 7 jaar (compliance)

2. **`temp`** (Cool tier)
   - Tijdelijke bestanden voor processing
   - Auto-cleanup na 24 uur
   - Retention: 1 dag

3. **`archive`** (Archive tier)
   - Oude, verwerkte documenten
   - Long-term archival
   - Retention: 10 jaar

#### Folder Structure:
```
documents/
├── uploaded_pdfs/
│   └── {year}/{month}/{filename}_{timestamp}.pdf
├── extracted_text/
│   └── {filename}_{timestamp}.txt
├── extracted_data/
│   └── order_{timestamp}.json
└── processed_orders/
    └── {order_number}_{timestamp}.json

temp/
└── pdf_{timestamp}.pdf (voor Computer Vision)
```

### 3. Azure Computer Vision (Cognitive Services)

**Service: `hso-document-vision`**

- **API Version**: 3.2
- **Pricing Tier**: S1 (Standard)
- **Features gebruikt**:
  - Read API (OCR voor PDFs)
  - Multi-language support (NL/EN)
  - Handwriting recognition

#### API Endpoints:
- `POST /vision/v3.2/read/analyze` - Start OCR operatie
- `GET /vision/v3.2/read/analyzeResults/{operationId}` - Krijg resultaten

### 4. Azure Key Vault

**Vault: `hso-data-extractor-vault`**

#### Secrets:
- `storage-connection-string` - Blob Storage connection
- `computer-vision-key` - Cognitive Services API key
- `function-app-key` - Function App master key

#### Access Policies:
- Function App: Get/List secrets
- Development: Get/List/Set secrets (tijdelijk)

## Deployment & DevOps

### Azure Resource Manager (ARM) Template

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "type": "string",
      "allowedValues": ["dev", "test", "prod"],
      "defaultValue": "dev"
    }
  },
  "variables": {
    "functionAppName": "[concat('hso-data-extractor-', parameters('environment'))]",
    "storageAccountName": "[concat('hsodataext', parameters('environment'))]",
    "keyVaultName": "[concat('hso-vault-', parameters('environment'))]"
  },
  "resources": [
    // Function App, Storage Account, Key Vault, Computer Vision
  ]
}
```

### CI/CD Pipeline (Azure DevOps)

1. **Build Pipeline**:
   - Python function packaging
   - Dependencies installation
   - Unit tests execution
   - ARM template validation

2. **Release Pipeline**:
   - Deploy to DEV → TEST → PROD
   - Smoke tests na deployment
   - Rollback mechanisme

## Security & Compliance

### Authentication & Authorization

1. **Function App**:
   - Function-level keys voor externe toegang
   - Managed Identity voor Azure services
   - CORS configuratie voor Streamlit

2. **Storage Account**:
   - Shared Access Signatures (SAS) voor tijdelijke toegang
   - Network ACLs (alleen Azure services)
   - Encryption at rest (AES-256)

3. **Key Vault**:
   - Azure AD authentication
   - Role-based access control (RBAC)
   - Audit logging enabled

### Data Protection

- **Encryption**: Alle data encrypted at rest en in transit
- **Backup**: Geo-redundant storage (GRS) voor critical data
- **Retention**: Automatische cleanup volgens retention policies
- **GDPR**: Data anonymization mogelijkheden

## Monitoring & Logging

### Application Insights

**Instance: `hso-data-extractor-insights`**

#### Metrics:
- Function execution times
- Success/failure rates
- Storage throughput
- Computer Vision API calls

#### Custom Events:
- Document uploaded
- Conversion started/completed
- Data extraction started/completed
- Validation errors

#### Alerting:
- Function failures > 5% in 5 minutes
- High memory usage (> 80%)
- Storage quota near limit (> 90%)

### Log Analytics Workspace

- Centralized logging voor alle services
- Custom queries voor troubleshooting
- Long-term log retention (30 dagen)

## Performance & Scaling

### Auto-scaling Configuration

```json
{
  "functionApp": {
    "scaleController": {
      "maximumInstanceCount": 200,
      "targetInstanceCount": 10
    },
    "runtime": {
      "minInstanceCount": 1,
      "maxInstanceCount": 20
    }
  }
}
```

### Performance Optimizations

1. **Function App**:
   - Consumption plan voor cost efficiency
   - Pre-warmed instances voor reduced cold starts
   - Connection pooling voor external services

2. **Storage**:
   - Hot/Cool/Archive tiering strategie
   - CDN voor frequent accessed files
   - Parallel uploads voor grote bestanden

3. **Computer Vision**:
   - Request batching waar mogelijk
   - Retry logic met exponential backoff
   - Fallback naar PyPDF2 bij OCR failures

## Cost Optimization

### Geschatte Maandelijkse Kosten (100 documenten/dag)

| Service | Tier | Maandelijks | 
|---------|------|-------------|
| Function App | Consumption | €15 |
| Blob Storage | Mixed tiers | €25 |
| Computer Vision | S1 | €45 |
| Key Vault | Standard | €3 |
| Application Insights | Basic | €10 |
| **Total** | | **€98** |

### Cost-saving Strategieën

1. **Reserved Instances** voor predictable workloads
2. **Lifecycle policies** voor automated tiering
3. **Function execution optimization** om consumption te reduceren
4. **Computer Vision batching** om API calls te minimaliseren

## Disaster Recovery

### Backup Strategy

1. **Code**: Git repository + Azure DevOps
2. **Configuration**: ARM templates in source control
3. **Data**: 
   - GRS replication voor Blob Storage
   - Point-in-time restore mogelijk
   - Cross-region backup voor critical data

### Recovery Procedures

1. **Complete region failure**:
   - Failover naar secundaire regio (30 min RTO)
   - Data sync via GRS replication
   - DNS update voor traffic routing

2. **Service-specific failures**:
   - Function App: Auto-healing + restart
   - Storage: Automatic failover to secondary
   - Computer Vision: Fallback naar PyPDF2

## Alternatieve Architectuur Opties

### 1. Azure Container Instances + Azure Cosmos DB

**Voordelen**:
- Meer controle over runtime environment
- NoSQL database voor flexibele schema's
- Container orchestration mogelijkheden

**Nadelen**:
- Hogere kosten bij lage volumes
- Meer management overhead
- Complexere deployment

### 2. Azure App Service + Azure SQL Database

**Voordelen**:
- Always-on availability
- Relationele database voor structured data
- Built-in authentication/authorization

**Nadelen**:
- Hogere fixed costs
- Over-provisioned voor episodic workloads
- Minder serverless benefits

### 3. Azure Logic Apps + Power Platform

**Voordelen**:
- Low-code/no-code development
- Uitgebreide connector ecosystem
- Integrated business process automation

**Nadelen**:
- Vendor lock-in concerns
- Beperkte custom code mogelijkheden
- Performance limitaties bij heavy processing

## Implementatie Roadmap

### Fase 1: MVP Deployment (2 weken)
- [ ] Basic Function App deployment
- [ ] Blob Storage setup
- [ ] Computer Vision integration
- [ ] Local development environment

### Fase 2: Production Readiness (3 weken)
- [ ] Security hardening
- [ ] Monitoring & alerting setup
- [ ] CI/CD pipeline implementation
- [ ] Performance testing

### Fase 3: Advanced Features (4 weken)
- [ ] Multi-language support
- [ ] Advanced data validation
- [ ] Audit trail implementation
- [ ] Advanced analytics dashboard

### Fase 4: Optimization (2 weken)
- [ ] Performance tuning
- [ ] Cost optimization
- [ ] Disaster recovery testing
- [ ] Documentation finalization

## Conclusie

Deze Azure-gebaseerde architectuur biedt een schaalbare, kosteneffectieve en betrouwbare oplossing voor documentverwerking. De serverless aanpak zorgt voor optimale cost-efficiency bij variabele workloads, terwijl de Microsoft-stack integratie zorgt voor seamless enterprise adoption.

De architectuur is ontworpen met HSO's requirements in gedachten: professionele zakelijke oplossing, Microsoft-stack alignment, en schaalbaarheid voor toekomstige groei.
