# NASA PACE Ocean Color Monitoring

Automated system for monitoring ocean health using NASA PACE satellite data. Tracks phytoplankton blooms, water quality, chlorophyll concentrations, and ocean ecosystem changes.

## Overview

This project analyzes NASA PACE Ocean Color Instrument (OCI) data to monitor marine ecosystem health. The system processes hyperspectral ocean observations to detect phytoplankton activity, harmful algal blooms, and water quality changes.

## Mission Background

NASA PACE (Plankton, Aerosol, Cloud, ocean Ecosystem) launched February 2024:
- Advanced Ocean Color Instrument with hyperspectral capabilities
- Monitors ocean biology, chemistry, and ecology
- Global coverage for tracking phytoplankton and ocean health
- Applications: Marine ecosystems, fisheries, carbon cycle, water quality

## Features

The system provides:
- Chlorophyll-a concentration mapping
- Phytoplankton bloom detection
- Ocean color classification
- Harmful algal bloom alerts
- Water quality assessment

## Data Processing

Analyzes:
- Ocean color spectral signatures
- Chlorophyll-a concentrations
- Particulate organic carbon
- Colored dissolved organic matter
- Aerosol optical depth over ocean

## Automated Updates

GitHub Actions workflow runs daily to:
- Retrieve latest PACE ocean color data
- Process spectral measurements
- Detect bloom events
- Generate ocean health maps
- Commit results automatically

## Output

Generated files:
- `data/` - PACE ocean color observations
- `results/` - Ocean health analysis (JSON)
- `plots/` - Chlorophyll maps and time series
- `maps/` - Geographic distribution of blooms

## Applications

Monitoring for:
- Harmful algal bloom early warning
- Phytoplankton dynamics
- Ocean productivity assessment
- Coastal water quality
- Marine ecosystem health

## Notes

Focuses on ocean ecosystem monitoring using advanced hyperspectral remote sensing. PACE provides unprecedented detail in ocean color observations for tracking marine life and water quality globally.
