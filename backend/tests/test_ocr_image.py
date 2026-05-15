import warnings
warnings.filterwarnings('ignore')

from paddleocr import PaddleOCR
import os

# 检查文件
file_path = r'C:\Users\Administrator\Desktop\test.png'
if not os.path.exists(file_path):
    print(f"文件不存在: {file_path}")
    print("请确保 test.png 在桌面上")
    exit()

print("✅ 找到文件")
print("🔄 初始化 OCR...")

# 初始化（模型已缓存，很快）
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

print("🔍 开始识别...")
result = ocr.ocr(file_path, cls=True)

# 输出结果
if result and len(result) > 0 and result[0]:
    print(f"\n✅ 识别成功！共识别到 {len(result[0])} 个文本区域\n")
    print("=" * 60)
    for idx, line in enumerate(result[0], 1):
        text = line[1][0]
        confidence = line[1][1]
        print(f"{idx:2d}. {text}")
        print(f"    置信度: {confidence:.2%}")
        print()
else:
    print("❌ 未识别到文字")
    print("可能原因：图片中没有文字，或图片太模糊")