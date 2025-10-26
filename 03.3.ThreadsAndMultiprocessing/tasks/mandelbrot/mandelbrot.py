import matplotlib.pyplot as plt

class MandelbrotGenerator:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers

    def generate(self, width: int, height: int, max_iter: int) -> list[list[float]]:
        # Implement the parallel version of the Mandelbrot set generation
        pass

    @staticmethod
    def _scale(x: int, y: int, width: int, height: int) -> complex:
        return complex(3.5 * x / width - 2.5, 2 * y / height - 1)

def visualize(data: list[list[float]], colormap: str = 'magma', save_path: str | None = None) -> None:
    plt.imshow(data, cmap=colormap)
    # plt.colorbar()
    plt.axis('off')
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True, format='png')
    else:
        plt.show()