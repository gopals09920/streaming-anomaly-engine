# Distributed Real-Time Streaming Anomaly Engine

## Overview
A low-latency MLOps architecture designed to ingest continuous transaction event streams, maintain real-time sliding-window feature states via Redis, and perform sub-50ms anomaly scoring using fast-path models.

## Key Performance Metrics
- **Internal Inference Latency:** ~1ms (Exceeding sub-50ms SLA)
- **Throughput:** Zero dropped events under high concurrency simulation
- **Drift Detection:** Population Stability Index (PSI) tracking for data drift monitoring

## Tech Stack
Python, FastAPI, Redis, LightGBM, Docker, Prometheus, Asynchronous IO