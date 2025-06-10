import numpy as np
import random
import time
from noise import pnoise2, snoise2
from scipy.interpolate import CubicSpline

# 生成随机单色图片
def generate_random_image(width, height):
    return [[random.choice([0, 1]) for _ in range(width)] for _ in range(height)]

# 使用柏林噪声生成图片
def generate_noise_image(width, height, t, scale=10.0, octaves=1):
    """使用柏林噪声生成图片，添加随机种子"""
    # 根据时间生成随机种子
    seed = int(t * 1000) + random.randint(0, 1000)
    random.seed(seed)
    
    image = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            # 添加随机偏移量以增加变化
            offset_x = random.uniform(0, 1)
            offset_y = random.uniform(0, 1)
            noise_val = snoise2((x + offset_x)/scale + t, 
                              (y + offset_y)/scale + t,
                              octaves=octaves,
                              base=seed)  # 使用seed作为base参数
            image[y][x] = 1 if noise_val > 0 else 0
    return image

def print_image(image):
    for row in image:
        print("".join(["#" if pixel else " " for pixel in row]))

# 拉格朗日插值
def lagrange_interpolation(image, x, y):
    """真正的拉格朗日插值实现"""
    height, width = len(image), len(image[0])
    x_indices = np.arange(width)
    y_indices = np.arange(height)
    
    def lagrange_basis(t, i, points):
        """计算拉格朗日基函数"""
        L = 1.0
        for j, point in enumerate(points):
            if i != j:
                L *= (t - point) / (points[i] - point)
        return L
    
    # 在x方向上取4个最近的点进行插值
    x_left = max(0, int(x) - 1)
    x_right = min(width - 2, x_left + 2)
    x_points = x_indices[x_left:x_right+2]
    x_values = [image[int(y)][xi] for xi in x_points]
    
    # x方向拉格朗日插值
    x_interp = sum(x_values[i] * lagrange_basis(x, i, x_points) 
                  for i in range(len(x_points)))
    
    # 在y方向上取4个最近的点进行插值
    y_left = max(0, int(y) - 1)
    y_right = min(height - 2, y_left + 2)
    y_points = y_indices[y_left:y_right+2]
    y_values = [image[yi][int(x)] for yi in y_points]
    
    # y方向拉格朗日插值
    y_interp = sum(y_values[i] * lagrange_basis(y, i, y_points) 
                  for i in range(len(y_points)))
    
    # 返回两个方向插值的平均值
    return (x_interp + y_interp) / 2

# 三次样条插值
def cubic_spline_interpolation(image, x, y):
    """改进的三次样条插值实现"""
    height, width = len(image), len(image[0])
    x_indices = np.arange(width)
    y_indices = np.arange(height)
    
    # 选择插值点范围
    x_left = max(0, int(x) - 2)
    x_right = min(width - 1, x_left + 4)
    y_left = max(0, int(y) - 2)
    y_right = min(height - 1, y_left + 4)
    
    # 获取局部区域的点
    x_local = x_indices[x_left:x_right]
    y_local = y_indices[y_left:y_right]
    
    # x方向插值
    x_values = [image[int(y)][xi] for xi in x_local]
    if len(x_values) >= 4:  # 确保有足够的点进行插值
        cs_x = CubicSpline(x_local, x_values, bc_type='natural')
        x_interp = cs_x(x)
    else:
        # 点数不足时退化为线性插值
        x_interp = np.interp(x, x_local, x_values)
    
    # y方向插值
    y_values = [image[yi][int(x)] for yi in y_local]
    if len(y_values) >= 4:
        cs_y = CubicSpline(y_local, y_values, bc_type='natural')
        y_interp = cs_y(y)
    else:
        y_interp = np.interp(y, y_local, y_values)
    
    # 组合两个方向的插值结果
    return (x_interp + y_interp) / 2

# 使用插值方法放大图片
def upscale_image(image, scale_factor, method='bilinear'):
    height, width = len(image), len(image[0])
    new_height, new_width = height * scale_factor, width * scale_factor
    upscaled_image = [[0 for _ in range(new_width)] for _ in range(new_height)]

    for y in range(new_height):
        for x in range(new_width):
            if method == 'lagrange':
                upscaled_image[y][x] = lagrange_interpolation(image, x / scale_factor, y / scale_factor)
            elif method == 'cubic_spline':
                upscaled_image[y][x] = cubic_spline_interpolation(image, x / scale_factor, y / scale_factor)
            else:
                raise ValueError("Unsupported interpolation method")

    return upscaled_image

def generate_test_images(num_images, image_size):
    """生成连续变化的测试图片集"""
    return [generate_noise_image(image_size, image_size, i * 0.2) for i in range(num_images)]

# 主程序
def main():
    num_batches = 50
    image_size = 16
    scale_factor = 2
    
    # 生成测试图片集
    print("生成测试图片集...")
    test_images = generate_test_images(num_batches, image_size)
    
    # 展示所有原始图片
    print("\n展示原始图片集：")
    for i, image in enumerate(test_images):
        print(f"\n原始图片 #{i + 1} ({image_size}x{image_size}):")
        print_image(image)
    
    input("\n按回车键继续执行插值测试...")
    
    # 拉格朗日插值测试
    lagrange_times = []
    lagrange_results = []
    print("\n执行拉格朗日插值...")
    for i, image in enumerate(test_images):
        start_time = time.time()
        upscaled_image = upscale_image(image, scale_factor, method='lagrange')
        end_time = time.time()
        lagrange_times.append(end_time - start_time)
        lagrange_results.append(upscaled_image)
        print(f"\n第{i + 1}张图片（拉格朗日插值）：")
        print(f"原始大小: {len(image)}x{len(image[0])}")
        print(f"放大后大小: {len(upscaled_image)}x{len(upscaled_image[0])}")
        print_image(upscaled_image)

    input("\n按回车键继续执行三次样条插值测试...")

    # 三次样条插值测试
    cubic_spline_times = []
    cubic_spline_results = []
    print("\n执行三次样条插值...")
    for i, image in enumerate(test_images):
        start_time = time.time()
        upscaled_image = upscale_image(image, scale_factor, method='cubic_spline')
        end_time = time.time()
        cubic_spline_times.append(end_time - start_time)
        cubic_spline_results.append(upscaled_image)
        print(f"\n第{i + 1}张图片（三次样条插值）：")
        print(f"原始大小: {len(image)}x{len(image[0])}")
        print(f"放大后大小: {len(upscaled_image)}x{len(upscaled_image[0])}")
        print_image(upscaled_image)

    # 输出结果对比
    print("\n计时结果对比：")
    print(f"拉格朗日插值平均时间：{np.mean(lagrange_times):.6f}秒")
    print(f"三次样条插值平均时间：{np.mean(cubic_spline_times):.6f}秒")
    
if __name__ == "__main__":
    main()