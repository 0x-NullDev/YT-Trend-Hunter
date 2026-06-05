# Contributing to YT Trend Hunter

First off, thank you for considering contributing to YT Trend Hunter! We welcome contributions from everyone.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### 🐛 Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/yt-trend-hunter/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, etc.)

### 💡 Suggesting Features

1. Check if the feature has been suggested in [Issues](https://github.com/yourusername/yt-trend-hunter/issues)
2. Create a new issue with:
   - Clear title and description
   - Use case and benefits
   - Example implementation if possible

### 🔧 Pull Requests

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write/update tests
5. Run tests: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15 (optional, Docker handles this)
- Redis 7 (optional, Docker handles this)

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/yt-trend-hunter.git
cd yt-trend-hunter

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run backend
uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest
pytest --cov=app tests/
pytest --cov=app tests/ --cov-report=html

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

### Code Style

- **Python**: Follow PEP 8, use type hints, run `black` and `ruff`
- **TypeScript**: Follow the project's ESLint configuration
- **Documentation**: Keep docstrings and README updated

```bash
# Format Python code
black backend/
ruff check backend/ --fix

# Format TypeScript code
cd frontend
npm run lint --fix
```

## Project Structure

```
yt-trend-hunter/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   │   ├── ai/       # AI providers
│   │   │   ├── collectors/  # Data collectors
│   │   │   └── engines/  # Intelligence engines
│   │   └── tasks/        # Celery tasks
│   ├── tests/            # Test files
│   └── alembic/          # Database migrations
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── tests/            # Test files
└── docs/                 # Documentation
```

## Adding a New AI Provider

1. Create a new class in `backend/app/services/ai/` that inherits from `AIProvider`
2. Implement all abstract methods
3. Add the provider to `AIFactory.providers` dict
4. Update the `.env.example` with new provider's configuration

## Adding a New Data Source

1. Create a new collector in `backend/app/services/collectors/`
2. Implement the data fetching logic
3. Add the source to the appropriate engine
4. Update the API endpoints if needed

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## Questions?

Feel free to reach out via:
- [GitHub Discussions](https://github.com/yourusername/yt-trend-hunter/discussions)
- [Issue Tracker](https://github.com/yourusername/yt-trend-hunter/issues)

Thank you for contributing! 🎯
