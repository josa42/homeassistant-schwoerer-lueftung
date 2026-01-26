#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if version argument is provided
if [ -z "$1" ]; then
    print_error "Usage: $0 <version>"
    print_error "Example: $0 1.0.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"

# Validate version format (semantic versioning)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Please use semantic versioning (e.g., 1.0.0)"
    exit 1
fi

print_info "Preparing release ${TAG}..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Please commit or stash your changes."
    exit 1
fi

# Make sure we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warn "You are not on the main branch (current: ${CURRENT_BRANCH})"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Aborted"
        exit 1
    fi
fi

# Pull latest changes
print_info "Pulling latest changes..."
git pull origin "$CURRENT_BRANCH"

# Update version in manifest.json
print_info "Updating version in manifest.json..."
MANIFEST_FILE="custom_components/schwoerer_lueftung/manifest.json"
if [ ! -f "$MANIFEST_FILE" ]; then
    print_error "Manifest file not found: $MANIFEST_FILE"
    exit 1
fi

# Use sed to update version (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"${VERSION}\"/" "$MANIFEST_FILE"
else
    sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"${VERSION}\"/" "$MANIFEST_FILE"
fi

print_info "Version updated in manifest.json"

# Check if version was actually updated
NEW_VERSION=$(grep -o '"version": "[^"]*"' "$MANIFEST_FILE" | cut -d'"' -f4)
if [ "$NEW_VERSION" != "$VERSION" ]; then
    print_error "Failed to update version in manifest.json"
    exit 1
fi

# Run tests
print_info "Running tests..."
if command -v make &> /dev/null && grep -q "^test:" Makefile 2>/dev/null; then
    make test
else
    print_warn "No test command found, skipping tests"
fi

# Run linter
print_info "Running linter..."
if command -v make &> /dev/null && grep -q "^lint:" Makefile 2>/dev/null; then
    make lint
else
    print_warn "No lint command found, skipping linting"
fi

# Commit changes
print_info "Committing version bump..."
git add "$MANIFEST_FILE"
git commit -m "chore: bump version to ${VERSION}"

# Create and push tag
print_info "Creating tag ${TAG}..."
git tag -a "$TAG" -m "Release ${TAG}"

print_info "Pushing changes and tag..."
git push origin "$CURRENT_BRANCH"
git push origin "$TAG"

print_info ""
print_info "✓ Release ${TAG} created successfully!"
print_info ""
print_info "Next steps:"
print_info "  1. GitHub Actions will automatically create a release with the zip file"
print_info "  2. Go to https://github.com/josa42/homeassistant-schwoerer-lueftung/releases"
print_info "  3. Edit the release notes if needed"
print_info ""
print_info "The integration zip file will be available for HACS installation"
