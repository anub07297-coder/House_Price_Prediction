#!/usr/bin/env python
"""
Quick script to start the House Price Prediction API

Usage:
  python run_api.py          # Start on http://localhost:8000
  python run_api.py 9000     # Start on http://localhost:9000
"""

import sys
import uvicorn

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║   HOUSE PRICE PREDICTION API                                ║
    ║   Starting on http://localhost:{port}                          ║
    ║                                                              ║
    ║   Interactive Docs:  http://localhost:{port}/docs             ║
    ║   ReDoc:            http://localhost:{port}/redoc             ║
    ║   API Endpoint:     POST http://localhost:{port}/predict      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "src.house_price_prediction.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
