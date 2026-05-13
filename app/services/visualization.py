import cv2
import numpy as np

from app.core.schemas import OCRItem


class Visualizer:
    def draw_ocr_annotations(
        self,
        image: np.ndarray,
        request_id: str,
        ocr_items: list[OCRItem],
    ) -> np.ndarray:
        annotated = image.copy()

        for item in ocr_items:
            if item.bbox is None or len(item.bbox) != 4:
                continue

            points = np.array(item.bbox, dtype=np.int32)

            cv2.polylines(
                annotated,
                [points],
                isClosed=True,
                color=(0, 255, 0),
                thickness=2,
            )

            x = int(points[:, 0].min())
            y = int(points[:, 1].min())

            label = f"{item.text} ({item.confidence:.2f})"

            cv2.putText(
                annotated,
                label,
                (x, max(20, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        height, width = annotated.shape[:2]
        margin = max(10, min(width, height) // 40)

        cv2.putText(
            annotated,
            f"request_id={request_id}",
            (margin, max(30, margin * 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        return annotated