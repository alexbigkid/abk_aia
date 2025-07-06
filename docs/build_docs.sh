#!/bin/bash
# Build documentation script for ABK AIA

echo "🔧 Building ABK AIA Documentation..."
echo "======================================"

# Clean previous build
echo "Cleaning previous build..."
rm -rf _build/

# Build HTML documentation  
echo "Building HTML documentation..."
uv run sphinx-build -b html /Users/abk/dev/git/abk_aia/docs /Users/abk/dev/git/abk_aia/docs/_build/html

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Documentation built successfully!"
    echo "📖 Open: docs/_build/html/index.html"
    echo ""
    echo "To serve locally:"
    echo "  cd docs/_build/html && python -m http.server 8000"
    echo "  Then open: http://localhost:8000"
else
    echo ""
    echo "❌ Documentation build failed!"
    exit 1
fi