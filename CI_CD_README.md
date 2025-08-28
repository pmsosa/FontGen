# FontGen CI/CD Pipeline

This document describes the CI/CD pipeline setup for FontGen, including unit tests, Docker containerization, and GitHub Actions workflows.

## 🏗️ **Pipeline Overview**

The CI/CD pipeline consists of several stages:

1. **Unit Tests** - Run all tests to ensure code quality
2. **Docker Build** - Build and test the Docker container
3. **Security Scan** - Run security vulnerability checks
4. **Dependency Check** - Verify package security
5. **Deploy Preview** - Deploy PRs to preview environment
6. **Deploy Production** - Deploy to production (Render)

## 🧪 **Testing Strategy**

### **Test Coverage**

- **CLI Tests** (`tests/cli/`): Test the command-line interface
- **Core Tests** (`tests/`): Test core functionality and new features
- **Web Tests** (`tests/webapp/`): Test web UI components
- **Comprehensive Test Runner** (`tests/run_all_tests.py`): Run all tests with summary

### **Running Tests Locally**

```bash
# Run all tests
cd tests
python run_all_tests.py

# Run specific test suites
python cli/test_fontgen.py
python test_core_functionality.py
python webapp/test_api.py

# Run with pytest (if available)
pytest -v
```

## 🐳 **Docker Containerization**

### **Container Features**

- **Base Image**: Ubuntu 22.04 LTS
- **Dependencies**: FontForge, Potrace, Python 3.13
- **Port**: 8000 (Web UI)
- **Health Check**: Built-in endpoint monitoring
- **Volume Mounts**: Uploads, downloads, temp files

### **Building and Testing**

```bash
# Build the container
docker build -t fontgen:latest .

# Test the container
./docker-build-test.sh

# Run with docker-compose
docker-compose up -d

# Run manually
docker run -p 8000:8000 fontgen:latest
```

### **Docker Compose**

The `docker-compose.yml` provides:
- Easy development setup
- Volume persistence
- Health monitoring
- Config file mounting

## 🚀 **GitHub Actions Workflow**

### **Workflow Triggers**

- **Push** to `main` or `develop` branches
- **Pull Request** to `main` or `develop` branches

### **Job Dependencies**

```
test → docker-build → deploy-preview
  ↓
docker-build → security-scan → deploy-production
  ↓
docker-build → dependency-check → deploy-production
```

### **Environment Protection**

- **Production deployment** requires all checks to pass
- **Security scans** must complete successfully
- **Dependency checks** must pass

## 🔒 **Security Features**

### **Security Scanning**

- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability checking
- **Container scanning**: Docker image security

### **Dependency Management**

- **Pinned versions** in requirements.txt
- **Security updates** via automated checks
- **Vulnerability reporting** in CI/CD

## 📊 **Monitoring and Health Checks**

### **Health Check Endpoints**

- **Root endpoint** (`/`): Basic availability
- **Config API** (`/api/config`): Configuration access
- **Template API** (`/api/template`): Template generation

### **Container Health**

```bash
# Check container status
docker ps

# View logs
docker logs fontgen-web

# Health check
curl -f http://localhost:8000/
```

## 🚀 **Deployment**

### **Preview Deployments**

- **Automatic** for pull requests
- **Isolated** environment for testing
- **Feedback** via PR comments

### **Production Deployments**

- **Manual trigger** via main branch push
- **All checks** must pass
- **Rollback** capability available

### **Render Integration**

The pipeline is designed to work with Render:
1. **Build** container in CI/CD
2. **Test** container functionality
3. **Deploy** to Render (manual setup)
4. **Monitor** health and performance

## 🔧 **Configuration**

### **Environment Variables**

```bash
FONTGEN_ENV=docker
PYTHONPATH=/app
```

### **Volume Mounts**

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./downloads:/app/downloads
  - ./temp_files:/app/temp_files
  - ./cli/config.json:/app/cli/config.json:ro
```

## 📝 **Troubleshooting**

### **Common Issues**

1. **Docker build fails**: Check system dependencies
2. **Tests fail**: Verify Python environment and dependencies
3. **Container won't start**: Check logs and port conflicts
4. **Health check fails**: Verify web server startup

### **Debug Commands**

```bash
# Check container logs
docker logs fontgen-web

# Enter container
docker exec -it fontgen-web bash

# Check processes
docker exec fontgen-web ps aux

# Test endpoints
curl -v http://localhost:8000/
```

## 🎯 **Next Steps**

1. **Configure Render deployment** with your account
2. **Set up environment secrets** in GitHub
3. **Customize deployment logic** for your needs
4. **Add monitoring** and alerting
5. **Implement rollback** procedures

## 📚 **Resources**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Render Documentation](https://render.com/docs)
- [FontForge Documentation](https://fontforge.org/docs/)
- [Potrace Documentation](http://potrace.sourceforge.net/)

---

**🎉 Your FontGen CI/CD pipeline is ready for production deployment!**
