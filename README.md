# 🎭 Playwright Web Automation Testing Framework

A comprehensive Python-based web automation testing framework built with Playwright and Pytest, featuring parallel execution, Allure reporting, and CI/CD integration.

[![Playwright Tests](https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework/actions/workflows/playwright.yml/badge.svg)](https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework/actions)
[![Test Report](https://img.shields.io/badge/Allure-Report-blue)](https://Salman-Codup-qa.github.io/PlayWrightWebAutomationTestingFramework/)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Automatic Setup (Windows)](#automatic-setup-windows)
  - [Manual Setup](#manual-setup)
- [Running Tests](#-running-tests)
- [Test Reports](#-test-reports)
- [Project Structure](#-project-structure)
- [CI/CD Integration](#-cicd-integration)
- [Contributing](#-contributing)

## ✨ Features

- 🚀 **Multi-Browser Support** - Chrome, Firefox, WebKit
- ⚡ **Parallel Test Execution** - Faster test runs
- 📊 **Allure Reporting** - Beautiful, detailed test reports
- 🔐 **Session Management** - Auth state persistence
- 🎯 **Page Object Model** - Maintainable test structure
- 🔄 **CI/CD Ready** - GitHub Actions integration
- 📝 **Comprehensive Logging** - Detailed execution logs
- 🌐 **Cross-Platform** - Windows, Linux, macOS

## 🔧 Prerequisites

- **Python 3.8+** (Python 3.13 recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

## 📦 Installation

### Automatic Setup (Windows)

The easiest way to set up the framework on Windows:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework.git
   cd PlayWrightWebAutomationTestingFramework
   ```

2. **Double-click on `setup.cmd`**
   - Locate the `setup.cmd` file in the project root
   - Double-click to run
   - The script will automatically:
     - ✅ Create a Python virtual environment
     - ✅ Activate the virtual environment
     - ✅ Install all Python dependencies
     - ✅ Install Playwright browsers (Chromium, Firefox, WebKit)

3. **Wait for completion**
   - The setup process may take a few minutes
   - Once complete, you'll see "Project Setup Complete!"

### Manual Setup

#### Windows

```bash
# 1. Clone the repository
git clone https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework.git
cd PlayWrightWebAutomationTestingFramework

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
python -m playwright install
```

#### Linux/macOS

```bash
# 1. Clone the repository
git clone https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework.git
cd PlayWrightWebAutomationTestingFramework

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
python -m playwright install
```

## 🚀 Running Tests

### Basic Commands

#### Run Tests in Headless Mode (Default)
```bash
pytest --alluredir=allure-results -v -s
```

#### Run Tests in Headed Mode (Browser Visible)
```bash
pytest --alluredir=allure-results -v -s --headed
```

#### Run Tests in Specific Browser
```bash
# Firefox
pytest --alluredir=allure-results -v -s --headed --browser firefox

# Chrome/Chromium
pytest --alluredir=allure-results -v -s --headed --browser chromium

# WebKit (Safari)
pytest --alluredir=allure-results -v -s --headed --browser webkit
```

#### Recreate Authentication Session
```bash
pytest --alluredir=allure-results -v -s --headed --browser firefox --recreate-auth
```

### Advanced Commands

#### Run Specific Test File
```bash
pytest tests/test_login.py --alluredir=allure-results -v -s
```

#### Run Tests with Specific Marker
```bash
pytest -m smoke --alluredir=allure-results -v -s
```

#### Run Tests in Parallel
```bash
pytest -n auto --alluredir=allure-results -v -s
```

#### Run Tests with Custom Workers
```bash
pytest -n 4 --alluredir=allure-results -v -s
```

## 📊 Test Reports

### View Allure Reports Locally

1. **Generate and open the report**
   ```bash
   allure serve allure-results
   ```
   This will automatically open the report in your default browser.

2. **Generate static report**
   ```bash
   allure generate allure-results -o allure-report --clean
   ```

3. **Open generated report**
   ```bash
   allure open allure-report
   ```

### View Online Reports

View the latest test execution report on GitHub Pages:
🔗 [Test Report](https://Salman-Codup-qa.github.io/PlayWrightWebAutomationTestingFramework/)

Reports are automatically generated and published after each test run in CI/CD pipeline.

## 📁 Project Structure

```
PlayWrightWebAutomationTestingFramework/
│
├── .github/
│   └── workflows/
│       └── playwright.yml          # GitHub Actions CI/CD workflow
│
├── tests/                          # Test files
│   ├── conftest.py                # Pytest fixtures and configurations
│   ├── test_login.py              # Login test cases
│   └── test_example.py            # Example test cases
│
├── pages/                          # Page Object Model
│   ├── base_page.py               # Base page class
│   ├── login_page.py              # Login page objects
│   └── dashboard_page.py          # Dashboard page objects
│
├── utils/                          # Utility functions
│   ├── config.py                  # Configuration management
│   ├── logger.py                  # Logging utilities
│   └── helpers.py                 # Helper functions
│
├── data/                           # Test data
│   ├── test_data.json             # Test data in JSON format
│   └── Auth.json                  # Authentication state
│
├── allure-results/                # Allure test results (auto-generated)
├── allure-report/                 # Allure HTML report (auto-generated)
│
├── setup.cmd                       # Windows setup script
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🔄 CI/CD Integration

This framework is integrated with **GitHub Actions** for automated testing:

- ✅ Automatically runs tests on every push to `main` branch
- ✅ Supports manual workflow dispatch
- ✅ Generates and publishes Allure reports to GitHub Pages
- ✅ Maintains test execution history
- ✅ Multi-browser testing support

### Workflow Features

- **Python 3.13** environment
- **Parallel execution** with pytest-xdist
- **Allure reporting** with history tracking
- **Automatic deployment** to GitHub Pages
- **Cross-browser testing** (Chromium, Firefox, WebKit)

View workflow runs: [Actions](https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework/actions)

## 🛠️ Configuration

### pytest.ini

Configure Pytest settings in `pytest.ini`:

```ini
[pytest]
markers =
    smoke: Smoke test cases
    regression: Regression test cases
    critical: Critical test cases

addopts = -v -s --tb=short
```

### Browser Configuration

Modify browser settings in `conftest.py` or use command-line options:

```python
# In conftest.py
@pytest.fixture
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Salman Saleem**
- GitHub: [@Salman-Codup-qa](https://github.com/Salman-Codup-qa)

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Modern web testing framework
- [Pytest](https://pytest.org/) - Python testing framework
- [Allure](https://docs.qameta.io/allure/) - Test reporting framework

---

⭐ **Star this repository** if you find it helpful!

📢 **Report Issues** on the [Issues](https://github.com/Salman-Codup-qa/PlayWrightWebAutomationTestingFramework/issues) page.

🔔 **Watch** this repository to get notifications about updates.