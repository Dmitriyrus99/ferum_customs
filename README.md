# Ferum Customs

![CI](https://github.com/Dmitriyrus99/ferum_customs/actions/workflows/ci.yml/badge.svg)
[![Coverage](https://img.shields.io/codecov/c/github/Dmitriyrus99/ferum_customs/main.svg?logo=codecov)](https://codecov.io/gh/Dmitriyrus99/ferum_customs)

Ferum Customs extends ERPNext with a service management layer. It keeps a registry of serviced equipment, tracks incoming requests and stores reports about performed work.

## Key Features

- Service request management
- Service reporting
- Telegram bot integration
- Google Drive integration

## Tech Stack

- **Backend:** Python, FastAPI, Frappe, Pydantic, Aiogram, OpenAI
- **UI Testing:** Playwright, ESLint, Prettier
- **Tooling:** Pytest, Ruff, Black, Isort, Pre-commit, Docker

## Getting Started

### Prerequisites

- Frappe >= 15
- PostgreSQL / MariaDB
- Python 3.10+

### Installation

See the [Installation Guide](INSTALL.md) for detailed instructions on how to install the project using Docker or on a bare-metal server.

## Usage

After installation the **Ferum Customs** module appears on the ERPNext desk. Typical workflow:

1. Create a **Service Object** that represents equipment or a location.
2. Open a **Service Request** for that object.
3. Technicians submit **Service Reports** describing the work done.
4. Optionally group several requests in a **Service Project**.

## Documentation

- [Deployment Guide](DEPLOY.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Russian Documentation](docs/overview_ru.md)

## License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.