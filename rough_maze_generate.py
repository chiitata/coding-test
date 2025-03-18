import random
import sys

from PIL import Image, ImageDraw

# 再帰深度を必要に応じて引き上げる
sys.setrecursionlimit(10000)

def load_mask(image_path, cell_size=5):
    """
    画像を読み込み、グレースケール＆2値化でセル単位のマスクを作成する。
    ここでは、輪郭の有無に関わらず、すべてのセルを迷路生成可能（True）とする。
    
    Args:
        image_path (str): 入力画像のパス
        cell_size (int): セルサイズ（ピクセル単位）
        
    Returns:
        mask (2次元リスト): 全セルTrue
        grid_width (int): 水平方向のセル数
        grid_height (int): 垂直方向のセル数
        cell_size (int): セルサイズ
    """
    img = Image.open(image_path).convert("L")
    width, height = img.size
    grid_width = width // cell_size
    grid_height = height // cell_size
    # すべてのセルをTrueにする（全体を迷路生成対象とする）
    mask = [[True for _ in range(grid_width)] for _ in range(grid_height)]
    return mask, grid_width, grid_height, cell_size

class Maze:
    def __init__(self, grid_width, grid_height, mask):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.mask = mask  # ここではすべてTrue
        self.maze = [[{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(grid_width)]
                     for _ in range(grid_height)]
        self.visited = [[False for _ in range(grid_width)] for _ in range(grid_height)]
    
    def generate(self, cx, cy):
        self.visited[cy][cx] = True
        directions = ['N', 'S', 'E', 'W']
        random.shuffle(directions)
        for direction in directions:
            nx, ny = cx, cy
            if direction == 'N':
                ny = cy - 1
            elif direction == 'S':
                ny = cy + 1
            elif direction == 'E':
                nx = cx + 1
            elif direction == 'W':
                nx = cx - 1
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                if not self.visited[ny][nx] and self.mask[ny][nx]:
                    # 壁を取り除く（双方向）
                    self.maze[cy][cx][direction] = False
                    if direction == 'N':
                        self.maze[ny][nx]['S'] = False
                    elif direction == 'S':
                        self.maze[ny][nx]['N'] = False
                    elif direction == 'E':
                        self.maze[ny][nx]['W'] = False
                    elif direction == 'W':
                        self.maze[ny][nx]['E'] = False
                    self.generate(nx, ny)
    
    def get_maze(self):
        return self.maze

def adjust_color(color):
    """
    壁の色としてサンプリングした色が白に近い場合、少し濃いライトグレーに調整する。
    """
    if all(c >= 240 for c in color):
        return (220, 220, 220)
    return color

def draw_maze_with_color(maze, grid_width, grid_height, cell_size, orig_image, wall_size=1):
    """
    迷路データを描画する。各壁の中点の元画像の色をサンプリングし、
    白に近い場合は調整した色で描画する。
    """
    img_width = grid_width * cell_size + wall_size
    img_height = grid_height * cell_size + wall_size
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)
    
    # 外枠（上端と左端）の描画
    mid_top = (img_width // 2, wall_size // 2)
    color_top = adjust_color(orig_image.getpixel(mid_top))
    draw.line([(0, 0), (img_width, 0)], fill=color_top, width=wall_size)
    mid_left = (wall_size // 2, img_height // 2)
    color_left = adjust_color(orig_image.getpixel(mid_left))
    draw.line([(0, 0), (0, img_height)], fill=color_left, width=wall_size)
    
    for y in range(grid_height):
        for x in range(grid_width):
            cx = x * cell_size
            cy = y * cell_size
            # 東側の壁
            if maze[y][x]['E']:
                mid_x = cx + cell_size
                mid_y = cy + cell_size // 2
                sample = orig_image.getpixel((min(mid_x, orig_image.width - 1),
                                               min(mid_y, orig_image.height - 1)))
                color = adjust_color(sample)
                draw.line([(cx + cell_size, cy), (cx + cell_size, cy + cell_size)],
                          fill=color, width=wall_size)
            # 南側の壁
            if maze[y][x]['S']:
                mid_x = cx + cell_size // 2
                mid_y = cy + cell_size
                sample = orig_image.getpixel((min(mid_x, orig_image.width - 1),
                                               min(mid_y, orig_image.height - 1)))
                color = adjust_color(sample)
                draw.line([(cx, cy + cell_size), (cx + cell_size, cy + cell_size)],
                          fill=color, width=wall_size)
    return image

def main():
    image_path = "assignment_image.png"
    # セルサイズを5に設定して、細かすぎず荒すぎない迷路を生成
    mask, grid_width, grid_height, cell_size = load_mask(image_path, cell_size=5)
    
    # 生成開始点はグリッドの中央付近（任意で変更可能）
    start = (grid_width // 2, grid_height // 2)
    
    maze_obj = Maze(grid_width, grid_height, mask)
    maze_obj.generate(start[0], start[1])
    maze = maze_obj.get_maze()
    
    # 元画像（RGB）を読み込み（描画時の色サンプリングに使用）
    orig_image = Image.open(image_path).convert("RGB")
    
    maze_img = draw_maze_with_color(maze, grid_width, grid_height, cell_size, orig_image, wall_size=1)
    maze_img.save("rough_maze.png")
    print("rough_maze.png saved.")

if __name__ == "__main__":
    main()
