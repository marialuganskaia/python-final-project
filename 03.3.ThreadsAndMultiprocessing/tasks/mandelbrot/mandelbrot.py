import matplotlib.pyplot as plt
import multiprocessing as mp
import ctypes
import math
from typing import List, Tuple, Optional, Any

all_arr: Any = None
all_width: int = 0
all_height: int = 0


def init_all(arr: Any, w: int, h: int) -> None:
    global all_arr, all_width, all_height
    all_arr = arr
    all_width = w
    all_height = h


def _scale(x: int, y: int, width: int, height: int) -> complex:
    return complex(3.5 * x / width - 2.5, 2. * y / height - 1.)


def calculate_mandelbrot(c: complex, max_iter: int) -> float:
    x0, y0 = c.real, c.imag
    x, y = 0.0, 0.0
    p = math.sqrt((x0 - 0.25) ** 2 + y0 ** 2)
    if x0 < p - 2 * p ** 2 + 0.25:
        return 0.0
    if (x0 + 1) ** 2 + y0 ** 2 < 0.0625:
        return 0.0
    for i in range(1, max_iter):
        x_new = x * x - y * y + x0
        y_new = 2 * x * y + y0

        x, y = x_new, y_new
        if x * x + y * y > 4:
            return float(i)

    return 0.0


def build_block(args: Tuple[int, int, int, int, int, int, int]) -> None:
    start_i, end_i, start_j, end_j, width, height, max_iter = args
    for i in range(start_i, end_i):
        for j in range(start_j, end_j):
            c: complex = _scale(j, i, width, height)
            it: float = calculate_mandelbrot(c, max_iter)
            all_arr[i * all_width + j] = it


class MandelbrotGenerator:
    def __init__(self, num_workers: int):
        self.num_workers = min(num_workers, mp.cpu_count())
        self.max_num_workers = num_workers

    def generate(self, width: int, height: int, max_iter: int) -> List[List[float]]:
        # Implement the parallel version of the Mandelbrot set generation
        if width * height < 1000 or self.num_workers == 1:
            result: List[List[float]] = []
            for i in range(height):
                row: List[float] = []
                for j in range(width):
                    c = _scale(j, i, width, height)
                    it = calculate_mandelbrot(c, max_iter)
                    row.append(it)
                result.append(row)
            return result

        arr: Any = mp.Array(ctypes.c_float, width * height, lock=False)
        block_size: int = 64
        block_rows: int = (height + block_size - 1) // block_size
        block_cols: int = (width + block_size - 1) // block_size
        block_height: int = block_size
        block_width: int = block_size
        blocks: List[Tuple[int, int, int, int, int, int, int]] = []

        for i in range(block_rows):
            for j in range(block_cols):
                start_i: int = i * block_height
                end_i: int = min((i + 1) * block_height, height)
                start_j: int = j * block_width
                end_j: int = min((j + 1) * block_width, width)
                blocks.append((start_i, end_i, start_j, end_j, width, height, max_iter))

        with mp.Pool(self.num_workers, initializer=init_all, initargs=(arr, width, height)) as pool:
            pool.map(build_block, blocks)

        final_result: list[list[float]] = [[arr[i * width + j] for j in range(width)] for i in range(height)]
        return final_result


def visualize(data: list[list[float]], colormap: str = 'magma', save_path: str | None = None) -> None:
    plt.imshow(data, cmap=colormap)
    # plt.colorbar()
    plt.axis('off')
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True, format='png')
    else:
        plt.show()


# if __name__ == "__main__":
#     generator = MandelbrotGenerator(num_workers=1)
#     data = generator.generate(100, 100, 10)
#     visualize(data)
