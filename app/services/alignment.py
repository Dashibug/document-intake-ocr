import cv2
import numpy as np


class DocumentAligner:
    """OpenCV-based document alignment service.

    The aligner tries to:
    1. find the largest document-like quadrilateral contour;
    2. apply perspective transform;
    3. fallback to deskew rotation if quadrilateral was not found.

    This is a lightweight and fully local baseline suitable for bank cards,
    ID cards and driver licenses.
    """

    def __init__(
        self,
        max_processing_side: int = 1000,
        min_document_area_ratio: float = 0.08,
    ) -> None:
        self.max_processing_side = max_processing_side
        self.min_document_area_ratio = min_document_area_ratio

    def align(self, image: np.ndarray) -> tuple[np.ndarray, list[str]]:
        warnings: list[str] = []

        if image is None or image.size == 0:
            raise ValueError("Empty image was passed to DocumentAligner.")

        height, width = image.shape[:2]

        if height < 50 or width < 50:
            warnings.append(
                "Image is too small for reliable alignment. Original image was returned."
            )
            return image.copy(), warnings

        resized_image, resize_ratio = self._resize_for_processing(image)

        document_contour = self._find_document_contour(resized_image)

        if document_contour is not None:
            points = document_contour.reshape(4, 2).astype("float32")
            points = points / resize_ratio

            aligned = self._four_point_transform(image, points)

            warnings.append(
                "Document contour was found. Perspective transform was applied."
            )

            return aligned, warnings

        warnings.append(
            "Document quadrilateral contour was not found. Fallback deskew was used."
        )

        deskewed = self._deskew_by_min_area_rect(image)

        return deskewed, warnings

    def _resize_for_processing(
        self,
        image: np.ndarray,
    ) -> tuple[np.ndarray, float]:
        height, width = image.shape[:2]
        max_side = max(height, width)

        if max_side <= self.max_processing_side:
            return image.copy(), 1.0

        resize_ratio = self.max_processing_side / float(max_side)
        new_width = int(width * resize_ratio)
        new_height = int(height * resize_ratio)

        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

        return resized, resize_ratio

    def _find_document_contour(self, image: np.ndarray) -> np.ndarray | None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blurred, 50, 150)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        if not contours:
            return None

        image_area = image.shape[0] * image.shape[1]
        min_area = self.min_document_area_ratio * image_area

        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for contour in contours[:20]:
            area = cv2.contourArea(contour)

            if area < min_area:
                continue

            perimeter = cv2.arcLength(contour, True)

            for epsilon_ratio in (0.015, 0.02, 0.03, 0.04, 0.05):
                approx = cv2.approxPolyDP(
                    contour,
                    epsilon_ratio * perimeter,
                    True,
                )

                if len(approx) == 4 and cv2.isContourConvex(approx):
                    return approx

        return None

    def _four_point_transform(
        self,
        image: np.ndarray,
        points: np.ndarray,
    ) -> np.ndarray:
        rect = self._order_points(points)

        top_left, top_right, bottom_right, bottom_left = rect

        width_a = np.linalg.norm(bottom_right - bottom_left)
        width_b = np.linalg.norm(top_right - top_left)
        max_width = int(max(width_a, width_b))

        height_a = np.linalg.norm(top_right - bottom_right)
        height_b = np.linalg.norm(top_left - bottom_left)
        max_height = int(max(height_a, height_b))

        max_width = max(max_width, 1)
        max_height = max(max_height, 1)

        destination = np.array(
            [
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1],
            ],
            dtype="float32",
        )

        transform_matrix = cv2.getPerspectiveTransform(rect, destination)

        warped = cv2.warpPerspective(
            image,
            transform_matrix,
            (max_width, max_height),
        )

        return warped

    def _order_points(self, points: np.ndarray) -> np.ndarray:
        rect = np.zeros((4, 2), dtype="float32")

        points_sum = points.sum(axis=1)
        rect[0] = points[np.argmin(points_sum)]
        rect[2] = points[np.argmax(points_sum)]

        points_diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(points_diff)]
        rect[3] = points[np.argmax(points_diff)]

        return rect

    def _deskew_by_min_area_rect(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        if not contours:
            return image.copy()

        largest_contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(largest_contour)

        angle = rect[-1]

        if angle < -45:
            angle = 90 + angle

        if abs(angle) < 1.0:
            return image.copy()

        return self._rotate_bound(image, angle)

    def _rotate_bound(self, image: np.ndarray, angle: float) -> np.ndarray:
        height, width = image.shape[:2]

        center = (width / 2.0, height / 2.0)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])

        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))

        rotation_matrix[0, 2] += (new_width / 2.0) - center[0]
        rotation_matrix[1, 2] += (new_height / 2.0) - center[1]

        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (new_width, new_height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        return rotated