# Document Intake OCR

## Problem
The system performs primary processing of personal document images:
alignment, OCR, field extraction and visualization.

## Supported documents
- bank cards
- ID cards
- driver licenses

## Architecture
Input image -> Alignment -> OCR -> Text normalization -> Document classification -> Field extraction -> JSON + annotated image

## Why PaddleOCR
PaddleOCR was selected as the default OCR backend because it provides local OCR inference, text detection and recognition, supports multilingual scenarios and can run on CPU/GPU.

## Why rule-based extraction
For a small test task, rule-based extraction is more transparent and easier to validate than training a KIE model from scratch.

## Limitations
- Works best with rectangular documents.
- Does not guarantee perfect extraction for all country-specific IDs.
- LLM extraction is optional and disabled by default.
- Personal data is not sent to external APIs unless explicitly enabled.

## Run
docker compose up --build

## API example
curl -X POST http://localhost:8000/api/v1/process \
  -F "file=@samples/input/card.jpg"