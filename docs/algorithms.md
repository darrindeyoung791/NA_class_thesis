# 插值算法伪代码说明

## 1. 超分辨率算法 (Super-resolution)

### 1.1 输入输出
```
Input: 
- image[n][n]: 原始图像 (n×n)
- scale_factor: 放大倍数

Output:
- upscaled_image[m][m]: 放大后图像 (m×m, m = n * scale_factor)
```

### 1.2 拉格朗日插值算法
```
Function lagrange_interpolation(image, x, y):
    1. 在x和y方向各选择4个最近的采样点
    2. 对每个方向:
        a. 计算拉格朗日基函数 L_i(t) = Π(t-t_j)/(t_i-t_j), j≠i
        b. 计算插值多项式 P(t) = Σy_i * L_i(t)
    3. 分别得到x方向和y方向的插值结果
    4. 返回两个方向插值的平均值

Function upscale_image_lagrange(image, scale_factor):
    1. 创建新图像 new_image[n*scale_factor][n*scale_factor]
    2. 对每个新像素位置 (x,y):
        a. 计算对应原图位置 (x/scale_factor, y/scale_factor)
        b. 调用 lagrange_interpolation 计算插值
    3. 返回放大后的图像
```

### 1.3 三次样条插值算法
```
Function cubic_spline_interpolation(image, x, y):
    1. 在x和y方向各选择4-5个局部点
    2. 对每个方向:
        a. 构建三次样条方程组 S_i(t) = a_i + b_i(t-t_i) + c_i(t-t_i)² + d_i(t-t_i)³
        b. 使用自然边界条件求解系数
        c. 计算插值点的值
    3. 返回两个方向插值的平均值

Function upscale_image_spline(image, scale_factor):
    1. 创建新图像 new_image[n*scale_factor][n*scale_factor]
    2. 对每个新像素位置 (x,y):
        a. 计算对应原图位置 (x/scale_factor, y/scale_factor)
        b. 调用 cubic_spline_interpolation 计算插值
    3. 返回放大后的图像
```

## 2. 帧插值算法 (Frame Interpolation)

### 2.1 输入输出
```
Input:
- frame1[n][n], frame2[n][n]: 相邻两帧
- t: 插值时间点 (0≤t≤1)

Output:
- middle_frame[n][n]: 插值生成的中间帧
```

### 2.2 拉格朗日帧插值算法
```
Function interpolate_frames_lagrange(frame1, frame2, t):
    1. 对每个像素位置 (x,y):
        a. 构建时间维度上的4个控制点 [-1,0,1,2]
        b. 计算拉格朗日基函数
        c. 使用t进行时间维度插值
    2. 确保插值结果在[0,1]范围内
    3. 返回生成的中间帧
```

### 2.3 样条帧插值算法
```
Function interpolate_frames_spline(frame1, frame2, t):
    1. 定义时间维度控制点 [0, 1/3, 2/3, 1]
    2. 对每个像素位置 (x,y):
        a. 计算控制点对应的像素值:
           - v1 = frame1[y][x]
           - v2 = frame1[y][x] * 2/3 + frame2[y][x] * 1/3
           - v3 = frame1[y][x] * 1/3 + frame2[y][x] * 2/3
           - v4 = frame2[y][x]
        b. 构建三次样条并计算t时刻的值
    3. 确保插值结果在[0,1]范围内
    4. 返回生成的中间帧
```
