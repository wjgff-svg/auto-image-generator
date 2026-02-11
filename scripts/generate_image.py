#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像生成・アップロードスクリプト
Cloudflare R2に画像を自動保存します
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw
import random
import boto3
from io import BytesIO


def generate_beautiful_image():
    """美しいグラデーション画像を生成"""
    print("🎨 画像生成中...")
    
    width = 1200
    height = 800
    
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # グラデーション背景
    for y in range(height):
        r = int(100 + (155 * y / height))
        g = int(150 - (50 * y / height))
        b = int(200 + (55 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # ランダムな円を描画
    for i in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(30, 150)
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    
    # 日時テキストを追加
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((40, 40), f"Generated: {timestamp}", fill=(255, 255, 255))
    draw.text((40, 100), "GitHub Actions Auto Generated", fill=(255, 255, 255))
    
    print("✅ 画像生成完了")
    return image


def upload_to_cloudflare_r2(image):
    """Cloudflare R2に画像をアップロード"""
    print("☁️  Cloudflare R2にアップロード中...")
    
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('R2_BUCKET_NAME')
    
    if not all([account_id, access_key, secret_key, bucket_name]):
        raise ValueError("❌ R2の設定が不足しています")
    
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'
    )
    
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG', optimize=True)
    img_byte_arr.seek(0)
    
    now = datetime.now()
    filename = f"generated/{now.strftime('%Y/%m/%d/%H%M%S')}.png"
    
    try:
        s3_client.upload_fileobj(
            img_byte_arr,
            bucket_name,
            filename,
            ExtraArgs={'ContentType': 'image/png'}
        )
        print(f"✅ アップロード成功: {filename}")
        return filename
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        raise


def main():
    """メイン処理"""
    print("=" * 50)
    print("🚀 画像生成プログラム開始")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        image = generate_beautiful_image()
        filename = upload_to_cloudflare_r2(image)
        
        print("=" * 50)
        print("✨ すべての処理が完了しました！")
        print(f"📷 保存ファイル: {filename}")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"❌ エラーが発生しました: {e}")
        print("=" * 50)
        raise


if __name__ == "__main__":
    main()
