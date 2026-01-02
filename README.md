# 🚀 Trading AI Pro - Professional Trading System with AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**An advanced trading platform powered by AI for intelligent market analysis and chart pattern recognition**

🌐 **[Live Demo](https://trading-aitool.streamlit.app/)** • [Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture)

</div>

---

## 📖 Overview

**Trading AI Pro** is a comprehensive trading analysis system that combines artificial intelligence with professional trading tools. Upload chart screenshots and get AI-powered analysis with optimal entry, stop-loss, and take-profit levels. Share your analysis with friends and colleagues via WhatsApp, Telegram, or Twitter - all from a beautiful, modern web interface.

**🌐 Try it now:** [https://trading-aitool.streamlit.app/](https://trading-aitool.streamlit.app/)

### ✨ Key Highlights

- 🤖 **AI-Powered Chart Analysis** - Upload trading charts and get instant entry, stop-loss, and take-profit levels
- 📤 **Easy Sharing** - Share your analysis via WhatsApp, Telegram, or Twitter with one click
- 💰 **Risk Management Focus** - Generate excellent returns while maintaining proper risk management
- 🎯 **Automatic Detection** - AI automatically detects position type, leverage, symbol, and strategy
- 🎨 **Modern UI** - Beautiful, intuitive interface with premium gold accents and dark theme
- 🔒 **Secure** - No API keys required - just upload and analyze

---

## 🎯 Features

### 🔍 AI Chart Analysis

Upload a screenshot of any trading chart and let our AI analyze it:

- **Automatic Detection:**
  - Asset symbol (ETH/USDT, BTC/USDT, etc.)
  - Position type (Long/Short recommendation)
  - Optimal leverage (1x-100x)
  - Trading strategy (Breakout, Reversal, Trend Following, etc.)
  
- **Trading Levels:**
  - Entry price
  - Stop loss (adjusted for leverage)
  - Take profit (minimum 2:1 risk-reward ratio)
  - Current price reading

- **Analysis Details:**
  - Pattern detection
  - Confidence level (0-100%)
  - Risk-reward ratio
  - Detailed reasoning for each recommendation

**Powered by:** Google Gemini 2.5 Flash Lite

### 📤 Share Your Analysis

Easily share your trading analysis with friends and colleagues:

- **Multiple Platforms:**
  - Share via WhatsApp with formatted message
  - Share via Telegram with one click
  - Share via Twitter/X to your followers
  
- **Formatted Messages:**
  - Professional message format with all key details
  - Includes asset, position type, leverage, and levels
  - Copy to clipboard option for manual sharing

- **No Account Required:**
  - Share without any API keys or account setup
  - Works instantly after analysis

### 🎨 Modern User Interface

Beautiful, professional design:

- **Dark Theme** - Easy on the eyes for long trading sessions
- **Responsive Layout** - Works on desktop and tablet
- **Intuitive Navigation** - Simple, clean interface
- **Real-Time Updates** - Instant feedback on all actions

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Google Gemini API key (for AI analysis)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MarxMad/Trading_AI_tool.git
   cd Trading_AI_tool
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Create a `.env` file in the root directory:
   ```env
   # Google Gemini API (Required for AI analysis)
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

   Or use the provided script:
   ```bash
   ./run_simple.sh
   ```

6. **Access the application:**
   
   Open your browser and navigate to: `http://localhost:8501`

### First Steps

1. **Configure Gemini API:**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add it to your `.env` file or Streamlit Cloud secrets
   - See [CONFIGURACION_GEMINI.md](CONFIGURACION_GEMINI.md) for details

2. **Start Analyzing Charts:**
   - Upload a chart screenshot
   - Select margin mode (Cross or Isolated)
   - Click "Analyze Chart with AI"
   - Review the AI recommendations
   - Share your analysis via WhatsApp, Telegram, or Twitter

### 🌐 Online Access

**Try the application online without installation:**
- **Live Demo:** [https://trading-aitool.streamlit.app/](https://trading-aitool.streamlit.app/)

---

## 📁 Project Structure

```
Trading_AI_tool/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── config/
│   └── config.yaml            # Configuration file
├── data/
│   ├── collectors/            # Data collection modules
│   │   └── yfinance_collector.py
│   └── processors/            # Data processing
│       └── technical_indicators.py
├── monitoring/
│   ├── image_analyzer.py      # AI chart analysis (Gemini)
│   └── trading_journal.py     # Trade tracking system
├── exchanges/
│   └── coinw_client.py        # Exchange integration (legacy)
├── risk/
│   └── risk_manager.py        # Risk management & position sizing
├── payment/
│   └── stripe_handler.py      # Subscription management
├── database/
│   └── db_handler.py          # Database operations
└── utils/
    ├── config_loader.py       # Configuration loader
    └── logger.py              # Logging utility
```

---

## 🏗️ Architecture

### System Overview

```mermaid
graph LR
    subgraph "User Interface"
        A[Chart Upload] --> B[AI Analysis]
        B --> C[Trade Execution]
        C --> D[Journal View]
    end
    
    subgraph "AI Processing"
        E[Gemini Vision] --> F[Pattern Detection]
        F --> G[Level Calculation]
    end
    
    subgraph "Trading Engine"
        H[Risk Management] --> I[Position Sizing]
        I --> J[Order Execution]
    end
    
    B --> E
    C --> H
    J --> K[Share Analysis]
    D --> L[Statistics]
    
    style A fill:#4a9eff,stroke:#333,color:#fff
    style E fill:#10b981,stroke:#333,color:#fff
    style K fill:#d4af37,stroke:#333,color:#fff
```

### Core Components

#### 1. **Image Analyzer** (`monitoring/image_analyzer.py`)
- Analyzes trading chart screenshots using Google Gemini Vision
- Automatically detects trading parameters
- Validates and adjusts recommended levels
- Returns structured analysis data

#### 2. **Share Functionality** (Built-in)
- Share analysis via WhatsApp, Telegram, or Twitter
- Formatted message generation
- Copy to clipboard option
- No external dependencies required

#### 3. **Trading Journal** (`monitoring/trading_journal.py`)
- Trade recording and storage
- Performance statistics calculation
- Trade filtering and search
- Data export capabilities

#### 4. **Risk Manager** (`risk/risk_manager.py`)
- Position sizing based on risk percentage
- Stop loss and take profit calculations
- Capital management
- Risk metrics tracking

### Data Flow

```mermaid
flowchart TD
    A[User Uploads Chart Image] --> B[Image Analyzer]
    B --> C[Google Gemini AI Analysis]
    C --> D[Extract Trading Parameters]
    D --> E{User Reviews Results}
    E -->|Shares| F[Share Functionality]
    E -->|New Analysis| A
    F --> G[Generate Share Message]
    G --> H[Share via Platform]
    H --> I[Analysis Complete]
    
    style A fill:#4a9eff,stroke:#333,color:#fff
    style C fill:#10b981,stroke:#333,color:#fff
    style H fill:#d4af37,stroke:#333,color:#fff
    style I fill:#8b5cf6,stroke:#333,color:#fff
```

### System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit Web Interface]
    end
    
    subgraph "AI Layer"
        IA[Image Analyzer]
        GEM[Google Gemini API]
    end
    
    subgraph "Trading Layer"
        RM[Risk Manager]
        CJ[Trading Journal]
    end
    
    subgraph "Share Layer"
        SH[Share Handler]
        PL[Platforms]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        LOG[Logging System]
    end
    
    UI --> IA
    IA --> GEM
    UI --> RM
    UI --> SH
    SH --> PL
    RM --> LOG
    
    style UI fill:#4a9eff,stroke:#333,color:#fff
    style GEM fill:#10b981,stroke:#333,color:#fff
    style PL fill:#d4af37,stroke:#333,color:#fff
    style DB fill:#8b5cf6,stroke:#333,color:#fff
```

### Chart Analysis Process

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant IA as Image Analyzer
    participant Gemini as Gemini API
    participant SH as Share Handler
    
    User->>UI: Upload Chart Image
    UI->>IA: Analyze Image
    IA->>Gemini: Send Image + Prompt
    Gemini-->>IA: Analysis Results
    IA->>IA: Validate Prices
    IA->>IA: Adjust Levels
    IA-->>UI: Return Analysis
    UI->>User: Display Results
    
    User->>UI: Click "Share" Button
    UI->>SH: Generate Share Message
    SH-->>UI: Formatted Message
    UI->>User: Show Share Options
    User->>UI: Select Platform
    UI->>SH: Share via Platform
    SH-->>User: Analysis Shared
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI analysis |

### Configuration Files

- **`config/config.yaml`** - Main configuration file
- **`.env`** - Environment variables (not committed to git)

### Streamlit Cloud Deployment

For production deployment on Streamlit Cloud:

1. Push your code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```
4. Deploy!

**🌐 Live Application:** [https://trading-aitool.streamlit.app/](https://trading-aitool.streamlit.app/)

See [Streamlit Cloud Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud) for details.

---

## 📚 Documentation

### Setup Guides

- **[Gemini Configuration](CONFIGURACION_GEMINI.md)** - How to set up Google Gemini API
- **[Stripe Configuration](CONFIGURACION_STRIPE.md)** - Subscription payment setup

### User Guides

- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- **[Interface Guide](INTERFAZ_GRAFICA.md)** - Detailed UI documentation
- **[Implementation Plan](PLAN_IMPLEMENTACION.md)** - Development roadmap

### API Documentation

- **Image Analyzer API** - See `monitoring/image_analyzer.py` docstrings
- **Trading Journal API** - See `monitoring/trading_journal.py` docstrings

---

## 🛠️ Development

### Adding New Features

The codebase is modular and easy to extend:

#### Adding New Share Platforms

1. Extend the share functionality in `app.py`:
   ```python
   def generate_share_message(analysis: dict) -> str:
       # Customize message format
   ```

2. Add new share button:
   ```python
   # Add new platform share button
   platform_url = f"https://platform.com/share?text={message}"
   ```

#### Adding New AI Models

1. Extend `ImageAnalyzer` class:
   ```python
   def _analyze_with_new_model(self, image):
       # Implementation
   ```

2. Add model selection logic in `analyze_chart_image()`

#### Customizing Risk Management

Modify `risk/risk_manager.py`:
- Adjust position sizing algorithms
- Add new risk metrics
- Implement custom stop-loss strategies

### Testing

Run tests (when implemented):
```bash
pytest tests/
```

### Code Style

Follow PEP 8 guidelines. The project uses:
- Type hints where applicable
- Docstrings for all functions/classes
- Logging instead of print statements

---

## 🔒 Security

### API Credentials

- **Never commit API keys to version control**
- Credentials are stored in `.env` (local) or Streamlit secrets (cloud)
- All API communications use HTTPS

### Best Practices

1. **Application Security:**
   - Keep dependencies updated
   - Review code before deploying
   - Use environment variables for secrets
   - Regular security audits
   - Only share analysis with trusted parties

---

## 📊 Performance Metrics

The system tracks various performance metrics:

- **Win Rate** - Percentage of profitable trades
- **Total P&L** - Cumulative profit/loss
- **Average P&L** - Average profit per trade
- **Risk-Reward Ratio** - Average risk to reward ratio
- **Sharpe Ratio** - Risk-adjusted returns (future)
- **Maximum Drawdown** - Largest peak-to-trough decline (future)

---

## 🚨 Important Disclaimers

### Trading Risks

⚠️ **Trading involves substantial risk of loss. Past performance does not guarantee future results.**

- Never trade with money you cannot afford to lose
- AI recommendations are for informational purposes only
- Always do your own research before trading
- Start with small positions and scale gradually
- Use proper risk management (stop losses, position sizing)

### AI Limitations

- AI analysis is based on chart patterns and technical indicators
- Market conditions can change rapidly
- AI may not account for all market factors
- Always verify AI recommendations before trading
- Confidence levels are estimates, not guarantees

### Sharing Analysis

- Analysis results are for informational purposes only
- Always verify AI recommendations before making trading decisions
- Share responsibly and only with trusted parties
- Remember that past analysis does not guarantee future results

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Commit with clear messages** (`git commit -m 'Add amazing feature'`)
5. **Push to your branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Contribution Guidelines

- Follow existing code style
- Add docstrings to new functions
- Update documentation for new features
- Test your changes thoroughly
- Keep commits focused and atomic

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - For powerful AI vision capabilities
- **Streamlit** - For the amazing web framework
- **Open Source Community** - For various libraries and tools

---

## 📞 Support

- **Documentation Issues** - Open an issue on GitHub
- **Bug Reports** - Use GitHub Issues with detailed description
- **Feature Requests** - Submit via GitHub Issues
- **Questions** - Check documentation first, then open a discussion

---

## 🗺️ Roadmap

### Upcoming Features

- [ ] Support for multiple exchanges (Binance, Bybit, etc.)
- [ ] Advanced backtesting engine
- [ ] Machine learning model training
- [ ] Real-time market data integration
- [ ] Mobile app support
- [ ] Social trading features
- [ ] Advanced risk analytics
- [ ] Portfolio management tools

### Version History

- **v2.0.0** (Current) - AI analysis with sharing functionality, premium UI with gold accents
- **v1.0.0** - Initial release with AI analysis
- Future versions will include advanced features and optimizations

---

<div align="center">

**Built with ❤️ for the trading community**

[⭐ Star this repo](https://github.com/MarxMad/Trading_AI_tool) if you find it useful!

</div>
