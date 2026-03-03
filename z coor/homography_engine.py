import cv2
import numpy as np


class CourtHomographyEngine:

    def __init__(self, court_width=6.1, court_length=13.4, scale=100):

        self.court_width  = court_width
        self.court_length = court_length
        self.scale        = scale

        self.dst_points = np.array([
            [0,           0           ],
            [court_width, 0           ],
            [court_width, court_length],
            [0,           court_length]
        ], dtype=np.float32)

        self.dst_points_scaled = self.dst_points * scale


    def compute_homography(self, image_points):
        
        image_points = np.array(image_points, dtype=np.float32)
        H, _ = cv2.findHomography(image_points, self.dst_points)
        return H


    def warp_image(self, image, H):
        output_w = int(self.court_width  * self.scale)
        output_h = int(self.court_length * self.scale)
        return cv2.warpPerspective(image, H, (output_w, output_h))


    def create_court_board(self):
        width_px  = int(self.court_width  * self.scale)
        height_px = int(self.court_length * self.scale)

        board = np.zeros((height_px, width_px, 3), dtype=np.uint8)
        board[:] = (0, 120, 0)

        white = (255, 255, 255)
        t = 3   # line thickness

        # Outer boundary
        cv2.rectangle(board, (0, 0), (width_px - 1, height_px - 1), white, t)

        # Net line (mid-court)
        net_y = int((self.court_length / 2) * self.scale)
        cv2.line(board, (0, net_y), (width_px, net_y), white, t + 1)

        # Singles sidelines (5.18 m wide, centred)
        side_margin = (self.court_width - 5.18) / 2
        left_x  = int(side_margin * self.scale)
        right_x = int((self.court_width - side_margin) * self.scale)
        cv2.line(board, (left_x,  0), (left_x,  height_px), white, t)
        cv2.line(board, (right_x, 0), (right_x, height_px), white, t)

        # Short service lines (1.98 m from net)
        short_top    = int((self.court_length / 2 - 1.98) * self.scale)
        short_bottom = int((self.court_length / 2 + 1.98) * self.scale)
        cv2.line(board, (0, short_top),    (width_px, short_top),    white, t)
        cv2.line(board, (0, short_bottom), (width_px, short_bottom), white, t)

        # Long service lines for doubles (0.76 m from back)
        top_long    = int(0.76 * self.scale)
        bottom_long = int((self.court_length - 0.76) * self.scale)
        cv2.line(board, (0, top_long),    (width_px, top_long),    white, t)
        cv2.line(board, (0, bottom_long), (width_px, bottom_long), white, t)

        # Centre line
        center_x = width_px // 2
        cv2.line(board, (center_x, 0), (center_x, height_px), white, t)

        return board


    def project_points(self, points, H):
        
        pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
        projected_meters = cv2.perspectiveTransform(pts, H)
        projected_pixels = projected_meters.reshape(-1, 2) * self.scale
        return projected_pixels


    def draw_players(self, board, player_points, colors=None):
        
        default_colors = [
            (0,   0,   255),
            (255, 50,  50 ),
            (0,   220, 220),
            (200, 0,   200),
        ]
        board_out = board.copy()
        h, w = board_out.shape[:2]

        for i, (x, y) in enumerate(player_points):
            px, py = int(round(x)), int(round(y))
            if px < -20 or px > w + 20 or py < -20 or py > h + 20:
                print(f"  [WARNING] P{i+1} projected off-court: ({px}, {py})")
                continue
            color = colors[i] if (colors and i < len(colors)) else default_colors[i % len(default_colors)]
            cv2.ellipse(board_out, (px, py + 6), (10, 4), 0, 0, 360, (0, 60, 0), -1)
            cv2.circle(board_out, (px, py), 10, color, -1)
            cv2.circle(board_out, (px, py), 10, (255, 255, 255), 2)
            cv2.putText(board_out, f"P{i+1}", (px - 8, py + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
        return board_out


    def debug_keypoint_order(self, image, court_kps):
        
        debug  = image.copy()
        labels = ["TL", "TR", "BR", "BL"]
        colors = [(0, 255, 0), (0, 165, 255), (0, 0, 255), (255, 0, 0)]
        for i, (x, y) in enumerate(court_kps[:4]):
            cv2.circle(debug, (int(x), int(y)), 10, colors[i], -1)
            cv2.putText(debug, labels[i], (int(x) + 10, int(y) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors[i], 2, cv2.LINE_AA)
        return debug