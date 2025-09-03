# HSO Data Extractor

Een professionele Streamlit-applicatie voor het verwerken van inkooporder PDFs met Azure backend integratie.

## ✨ Features

- **Document Upload**: Drag-and-drop PDF upload met validatie
- **Intelligente OCR**: Azure Computer Vision voor tekstextractie
- **Gestructureerde Data Extractie**: Automatische parsing van inkooporder gegevens
- **Human Verification**: Intuïtieve interface voor data validatie
- **Azure Integration**: Volledige Microsoft-stack implementatie
- **Professional UI**: HSO branding met moderne zakelijke uitstraling

## 🏗️ Architectuur

### Frontend
- **Streamlit**: Modern Python web framework
- **Responsive Design**: Optimaal voor desktop gebruik
- **Real-time Updates**: Live progress tracking
- **Professional Styling**: HSO corporate branding

### Backend (Azure)
- **Azure Functions**: Serverless document processing
- **Blob Storage**: Betrouwbare document opslag
- **Computer Vision**: AI-powered OCR service
- **Key Vault**: Veilige credential management

## 🚀 Quick Start

### Vereisten
- Python 3.8+
- pip package manager

### Installatie

1. **Clone de repository**:
   ```bash
   git clone <repository-url>
   cd DataExtractor
   ```

2. **Installeer dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configureer omgeving (.env)**:
   ```bash
   cp .env.example .env
   # Pas waarden aan voor lokaal gebruik (of laat USE_MOCK_AZURE=true voor demo)
   ```

4. **Start de applicatie**:
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**:
   ```
   http://localhost:8501
   ```

## 🧪 Testing

Run alle unit tests:
```bash
python run_tests.py
```

Of individuele test files:
```bash
python -m pytest tests/test_azure_client.py -v
python -m pytest tests/test_streamlit_app.py -v
```

## 📱 Gebruik

### 1. Overview Scherm
- Bekijk status van alle verwerkte documenten
- Zoek documenten op naam of ordernummer
- Filter op status (Completed/Uncompleted)
- Start nieuwe documentverwerking

### 2. Document Processing (4 stappen)

#### Stap 1: Upload
- Sleep PDF bestand naar upload area
- Maximaal 2MB, alleen PDF formaat
- Automatische bestandsvalidatie

#### Stap 2: Converting
- Azure Computer Vision OCR processing
- Fallback naar PyPDF2 voor tekst-PDFs
- Real-time progress indicator

#### Stap 3: Extracting
- AI-powered data extractie
- Structured parsing van:
  - Order nummers
  - Leverancier informatie
  - Line items met prijzen
  - Financiële totalen
  - Leveringsadressen

#### Stap 4: Human Check
- Side-by-side vergelijking origineel vs extracted
- Bewerkbare velden voor correcties
- Approve/Reject workflow
- Automatische opslag naar Azure Blob

## 🔧 Configuratie

### Environment Variables
Voorkeur: gebruik een `.env` bestand voor lokaal, en platform-variabelen (App Settings) in productie.

1) Lokaal (ontwikkeling):
```bash
cp .env.example .env
# bewerk .env en stel o.a. in:
# USE_MOCK_AZURE=true  # Laat aan voor demo
# AZURE_FUNCTION_URL=  # Vul in voor echte backend
# AZURE_STORAGE_ACCOUNT=
```

2) Productie (Azure App Service/Functions): stel de volgende variabelen in als App Settings, niet in `.env`:
```bash
export AZURE_FUNCTION_URL="https://your-function-app.azurewebsites.net"
export AZURE_STORAGE_ACCOUNT="yourstorageaccount"
export COMPUTER_VISION_ENDPOINT="https://yourregion.api.cognitive.microsoft.com/"
export COMPUTER_VISION_KEY="your_key_here"
```

Opmerkingen:
- Secrets beheer je in Azure Key Vault en injecteer je via Managed Identity naar App Settings. Commit nooit `.env`.
- De app leest config via `config.py` (python-dotenv) en valt terug op omgevingsvariabelen.

### Streamlit Config
Pas `.streamlit/config.toml` aan voor custom styling.

## 📊 Demo Mode

De applicatie draait standaard in demo mode met mock Azure services. Voor productie deployment:

1. **Azure Resources Setup**:
   - Deploy Azure Function App
   - Configure Blob Storage containers
   - Setup Computer Vision service
   - Configure Key Vault

2. **Backend Deployment**:
   ```bash
   # Deploy functions
   func azure functionapp publish your-function-app-name
   ```

3. **Frontend Configuration**:
   - Zet `USE_MOCK_AZURE=false` in de omgeving
   - Stel `AZURE_FUNCTION_URL` en `AZURE_STORAGE_ACCOUNT` in via App Settings (niet `.env`)
   - Herstart de app of deployment

## 🏢 HSO Integration

### Branding
- HSO corporate kleuren en styling
- Professional business interface
- Responsive design voor verschillende schermgroottes

### Security
- Azure AD authentication (ready voor implementatie)
- Role-based access control
- Secure credential management via Key Vault

### Compliance
- GDPR-ready data handling
- Audit trail logging
- Retention policy implementation

## 📈 Performance

### Optimalisaties
- Lazy loading van documenten
- Efficient state management
- Parallel processing capability
- Caching van extracted data

### Schaalbaarheid
- Serverless auto-scaling
- Consumption-based pricing
- Multi-region deployment ready

## 🛠️ Development

### Project Structure
```
DataExtractor/
├── app.py                    # Hoofdapplicatie
├── services/
│   └── azure_client.py      # Azure services client
├── backend/
│   └── azure_functions.py   # Azure Functions code
├── tests/
│   ├── test_azure_client.py
│   └── test_streamlit_app.py
├── docs/
│   └── azure_architecture.md
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
```

### Code Style
- PEP 8 compliance
- Type hints waar mogelijk
- Comprehensive docstrings
- Unit test coverage > 80%

## 🌐 Azure Deployment

Zie `docs/azure_architecture.md` voor:
- Gedetailleerde architectuur beschrijving
- Deployment instructies
- Cost optimization strategieën
- Security best practices
- Monitoring & logging setup

## 🐛 Troubleshooting

### Veelvoorkomende Issues

1. **Upload fails**:
   - Check bestandsgrootte (max 2MB)
   - Controleer PDF format
   - Verificeer internetconnectie

2. **OCR errors**:
   - Fallback naar PyPDF2 wordt automatisch gebruikt
   - Check Computer Vision service status
   - Verificeer API keys

3. **Data extraction issues**:
   - Manual correction mogelijk in Human Check
   - Regex patterns zijn aanpasbaar
   - Contact support voor nieuwe formaten

### Logs
```bash
# Streamlit logs
streamlit run app.py --logger.level debug

# Azure Function logs
func host start --verbose
```

## 📞 Support

Voor vragen of issues:
- Interne HSO IT support
- Developer documentatie in `/docs`
- Unit tests als referentie

---

**HSO Data Extractor** - Powered by Microsoft Azure & Streamlit 🚀
