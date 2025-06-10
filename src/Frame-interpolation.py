import numpy as np
import random
import time
from noise import pnoise2, snoise2
from scipy.interpolate import CubicSpline

def generate_continuous_frame(width, height, t, scale=10.0, octaves=1):
    """使用柏林噪声生成连续变化的帧，添加随机种子"""
    # 根据时间生成随机种子
    seed = int(t * 1000) + random.randint(0, 1000)
    random.seed(seed)
    
    frame = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            # 添加随机偏移量以增加变化
            offset_x = random.uniform(0, 1)
            offset_y = random.uniform(0, 1)
            noise_val = snoise2((x + offset_x)/scale + t, 
                              (y + offset_y)/scale + t,
                              octaves=octaves,
                              base=seed)  # 使用seed作为base参数
            frame[y][x] = 1 if noise_val > 0 else 0
    return frame

def print_image(image):
    for row in image:
        print("".join(["#" if pixel else " " for pixel in row]))

def generate_sequence(num_frames, image_size):
    """生成连续的图片序列"""
    frames = []
    for i in range(num_frames):
        # 使用帧索引作为时间参数，确保连续性
        t = i * 0.2  # 控制变化速度的系数
        frame = generate_continuous_frame(image_size, image_size, t)
        frames.append(frame)
    return frames

def interpolate_frames_lagrange(frame1, frame2, t):
    """改进的拉格朗日插值实现"""
    height, width = len(frame1), len(frame1[0])
    result = [[0 for _ in range(width)] for _ in range(height)]
    
    def lagrange_basis(t, i, points):
        """计算拉格朗日基函数"""
        L = 1.0
        for j, point in enumerate(points):
            if i != j:
                L *= (t - point) / (points[i] - point)
        return L

    # 使用4个时间点进行插值
    t_points = np.array([-1, 0, 1, 2])  # 相对时间点
    
    for y in range(height):
        for x in range(width):
            # 获取4个时间点的像素值
            if t < 0.5:
                # 使用前后两帧及其邻近帧
                pixel_values = [
                    frame1[y][x],  # t=0
                    frame1[y][x],  # t=0
                    frame2[y][x],  # t=1
                    frame2[y][x]   # t=1
                ]
            else:
                # 使用当前帧和后续帧
                pixel_values = [
                    frame1[y][x],  # t=0
                    frame1[y][x],  # t=0
                    frame2[y][x],  # t=1
                    frame2[y][x]   # t=1
                ]
            
            # 拉格朗日插值
            result[y][x] = sum(pixel_values[i] * lagrange_basis(t, i, t_points) 
                             for i in range(len(t_points)))
            
    return result

def interpolate_frames_spline(frame1, frame2, t):
    """改进的三次样条插值实现"""
    height, width = len(frame1), len(frame1[0])
    result = [[0 for _ in range(width)] for _ in range(height)]
    
    # 定义控制点的时间坐标
    t_points = np.array([0, 1/3, 2/3, 1])
    
    for y in range(height):
        for x in range(width):
            # 获取控制点的像素值
            pixel_values = [
                frame1[y][x],
                frame1[y][x] * 2/3 + frame2[y][x] * 1/3,
                frame1[y][x] * 1/3 + frame2[y][x] * 2/3,
                frame2[y][x]
            ]
            
            # 使用自然边界条件的三次样条
            cs = CubicSpline(t_points, pixel_values, bc_type='natural')
            result[y][x] = cs(t)
            
            # 确保值在[0,1]范围内
            result[y][x] = max(0, min(1, result[y][x]))
    
    return result

def main():
    num_frames = 51
    image_size = 32  # 修改为32x32
    
    # 生成原始帧序列
    print("生成原始帧序列...")
    frames = generate_sequence(num_frames, image_size)
    
    # 显示原始帧
    print("\n展示原始帧序列：")
    for i, frame in enumerate(frames):
        print(f"\n原始帧 #{i + 1} ({image_size}x{image_size}):")
        print_image(frame)
    
    input("\n按回车键开始拉格朗日插值测试...")
    
    # 拉格朗日插值测试
    lagrange_times = []
    print("\n执行拉格朗日插值生成中间帧...")
    for i in range(num_frames - 1):
        start_time = time.time()
        middle_frame = interpolate_frames_lagrange(frames[i], frames[i+1], 0.5)
        end_time = time.time()
        lagrange_times.append(end_time - start_time)
        print(f"\n帧 {i+1} 和 {i+2} 之间的中间帧（拉格朗日）：")
        print_image(middle_frame)
    
    input("\n按回车键开始三次样条插值测试...")
    
    # 三次样条插值测试
    spline_times = []
    print("\n执行三次样条插值生成中间帧...")
    for i in range(num_frames - 1):
        start_time = time.time()
        middle_frame = interpolate_frames_spline(frames[i], frames[i+1], 0.5)
        end_time = time.time()
        spline_times.append(end_time - start_time)
        print(f"\n帧 {i+1} 和 {i+2} 之间的中间帧（样条）：")
        print_image(middle_frame)

    # 输出性能对比
    print("\n性能对比：")
    print(f"拉格朗日插值平均时间：{np.mean(lagrange_times):.6f}秒/帧")
    print(f"三次样条插值平均时间：{np.mean(spline_times):.6f}秒/帧")
    print(f"拉格朗日插值总时间：{sum(lagrange_times):.6f}秒")
    print(f"三次样条插值总时间：{sum(spline_times):.6f}秒")

if __name__ == "__main__":
    main()
