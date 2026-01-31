"""
ProofGate Main Entry Point

Run with: python main.py
Or: uvicorn src.api.main:app --reload
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Start the ProofGate API server."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🔐 ProofGate - Multi-Agent Judgment System                ║
║                                                              ║
║   The AI that says "No" until you prove it.                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Server starting at: http://{host}:{port}                     ║
║                                                              ║
║   Endpoints:                                                 ║
║   • POST /api/judge     - Run judgment pipeline              ║
║   • POST /api/evidence  - Attach evidence document           ║
║   • GET  /api/traces    - List run traces                    ║
║   • GET  /api/excerpts  - List available excerpts            ║
║   • GET  /health        - Health check                       ║
║                                                              ║
║   Documentation: http://{host}:{port}/docs                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
