#!/usr/bin/env python3
"""Runner script for METABRIC cohort ingestion and benchmark feature extraction."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.ingest_metabric import main

if __name__ == "__main__":
    main()
