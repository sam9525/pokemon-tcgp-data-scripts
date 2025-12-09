import cv2
import glob
import numpy as np
import os


def load_icons():
    """
    Load icons from type-icons folder.
    """
    icons = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for icon_path in glob.glob(os.path.join(base_dir, "type-icons", "*.png")):
        name = os.path.splitext(os.path.basename(icon_path))[0]
        img = cv2.imdecode(np.fromfile(icon_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            icons[name] = img
    return icons


def match_icon(crop, icons, threshold=0.5, scales=None, method=cv2.TM_CCOEFF_NORMED):
    """
    Match a crop against all icons. Returns the best match name and score.
    Args:
        crop (numpy.ndarray): The image to search for icons.
        icons (dict): A dictionary of icons to search for.
        threshold (float): The threshold for matching icons.
        scales (numpy.ndarray): The scales to use for matching.
        method (int): The matching method to use.
    Returns:
        tuple: The best match name and score.
    """
    best_score = -1 if method != cv2.TM_SQDIFF_NORMED else 1.1
    best_type = None

    # Scales around 0.25
    if scales is None:
        scales = np.linspace(0.25, 0.35, 5)

    for scale in scales:
        # Try to match each icon and the best one will be returned
        for name, icon in icons.items():
            # Resize icon
            new_width = int(icon.shape[1] * scale)
            new_height = int(icon.shape[0] * scale)
            resized_icon = cv2.resize(
                icon, (new_width, new_height), interpolation=cv2.INTER_AREA
            )

            if (
                resized_icon.shape[0] > crop.shape[0]
                or resized_icon.shape[1] > crop.shape[1]
            ):
                continue

            res = cv2.matchTemplate(crop, resized_icon, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if max_val > best_score:
                best_score = max_val
                best_type = name

    if best_score > threshold:
        return best_type
    return None


def find_all_icons(crop, icons, threshold=0.5):
    """
    Find ALL occurrences of icons in the crop.
    Args:
        crop (numpy.ndarray): The image to search for icons.
        icons (dict): A dictionary of icons to search for.
        threshold (float): The threshold for matching icons.
    Returns a list of found types, sorted by x-coordinate.
    """
    candidates = []

    # Scales around 0.25
    scales = np.linspace(0.20, 0.35, 5)

    for name, icon in icons.items():
        for scale in scales:
            new_width = int(icon.shape[1] * scale)
            new_height = int(icon.shape[0] * scale)

            if new_width == 0 or new_height == 0:
                continue

            if new_width > crop.shape[1] or new_height > crop.shape[0]:
                continue

            resized_icon = cv2.resize(
                icon, (new_width, new_height), interpolation=cv2.INTER_AREA
            )

            try:
                res = cv2.matchTemplate(crop, resized_icon, cv2.TM_CCOEFF_NORMED)
            except:
                continue

            # Find all locations above threshold
            locs = np.where(res >= threshold)
            # locs is (y_indices, x_indices)

            for pt in zip(*locs[::-1]):  # zip(x, y)
                x, y = pt
                score = res[y, x]
                # Store: score, x, y, w, h, name
                candidates.append((score, x, y, new_width, new_height, name))

    # Sort candidates by score (descending)
    candidates.sort(key=lambda x: x[0], reverse=True)

    final_matches = []

    # Accepted rects to check overlap
    accepted_rects = []

    def compute_iou(boxA, boxB):
        # box: (x, y, w, h)
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0

        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    for cand in candidates:
        score, x, y, w, h, name = cand
        box = (x, y, w, h)

        is_overlapping = False
        for accepted_box in accepted_rects:
            # If IoU is high, it's the same icon (or a slightly worse match of the same one)
            if compute_iou(box, accepted_box) > 0.3:  # 0.3 threshold for overlap
                is_overlapping = True
                break

        if not is_overlapping:
            final_matches.append(cand)
            accepted_rects.append(box)

    # Sort final matches by Y then X
    final_matches.sort(key=lambda x: x[2])  # Sort by Y

    unique_matches_by_name = {}
    for score, x, y, w, h, name in final_matches:
        if (
            name not in unique_matches_by_name
            or score > unique_matches_by_name[name][0]
        ):
            unique_matches_by_name[name] = (score, x, y, w, h, name)
    final_matches = list(unique_matches_by_name.values())

    final_matches.sort(key=lambda x: x[2])  # Sort by Y

    curr_y = final_matches[0][2]
    prev_y = curr_y
    prev_h = final_matches[0][4]
    current_row = [final_matches[0]]
    rows = []
    for i in range(1, len(final_matches)):
        curr_y = final_matches[i][2]

        if abs(curr_y - prev_y) < (prev_h * 0.5):
            current_row.append(final_matches[i])
        else:
            rows.append(current_row)
            current_row = [final_matches[i]]
    rows.append(current_row)

    # Sort each row by X
    sorted_matches = []
    for row in rows:
        row.sort(key=lambda x: x[1])
        sorted_matches.extend(row)

    return [m[5] for m in sorted_matches]
