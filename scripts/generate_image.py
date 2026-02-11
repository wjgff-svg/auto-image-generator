#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像生成・アップロードスクリプト
Cloudflare R2に画像を自動保存します
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import random
import boto3
from io import BytesIO

def generate_beautiful_image():
    """
    美しいグラデーション画像を生成
    """
    print("🎨 画像生成中...")
    
    # 画像サイズ
    width, height = 1200, 800
    
    # 新しい画像を作成
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # グラデーション背景を作成
    for y in range(height):
        # 上から下へのグラデーション
        r = int(100 + (155 * y / height))
        g = int(150 - (50 * y / height))
        b = int(200 + (55 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # ランダムな円を描画（装飾）
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(30, 150)
        
        # 半透明の色を作成
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        
        # 円を描画
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=color,
            outline=None
        )
    
    # 日時テキストを追加
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    # 大きめのテキスト
    try:
        # デフォルトフォントを使用
        font_size = 40
        # テキストの背景（読みやすくするため）
        text_bbox = draw.textbbox((0, 0), f"生成日時: {timestamp}")
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 半透明の背景
        draw.rectangle(
            [20, 20, 20 + text_width + 40, 20 + text_height + 40],
            fill=(0, 0, 0, 180)
        )
    except:
        pass
    
    # テキスト描画
    draw.text((40, 40), f"生成日時: {timestamp}", fill=(255, 255, 255))
    draw.text((40, 100), "GitHub Actions 自動生成", fill=(255, 255, 255))
    
    print("✅ 画像生成完了")
    return image


def upload_to_cloudflare_r2(image):
    """
    Cloudflare R2に画像をアップロード
    """
    print("☁️  Cloudflare R2にアップロード中...")
    
    # 環境変数から設定を取得
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('R2_BUCKET_NAME')
    
    # 設定チェック
    if not all([account_id, access_key, secret_key, bucket_name]):
        raise ValueError("❌ R2の設定が不足しています。GitHub Secretsを確認してください。")
    
    # R2のエンドポイント（S3互換API）
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    # S3クライアントを作成（R2用）
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'
    )
    
    # 画像をバイト配列に変換
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG', optimize=True)
    img_byte_arr.seek(0)
    
    # ファイル名を生成（年/月/日/時分秒.png）
    now = datetime.now()
    filename = f"generated/{now.strftime('%Y/%m/%d/%H%M%S')}.png"
    
    # R2にアップロード
    try:
        s3_client.upload_fileobj(
            img_byte_arr,
            bucket_name,
            filename,
            ExtraArgs={
                'ContentType': 'image/png',
                'CacheControl': 'max-age=31536000'
            }
        )
        print(f"✅ アップロード成功: {filename}")
        print(f"📁 バケット: {bucket_name}")
        
        return filename
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        raise


def main():
    """
    メイン処理
    """
    print("=" * 50)
    print("🚀 画像生成プログラム開始")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 1. 画像を生成
        image = generate_beautiful_image()
        
        # 2. R2にアップロード
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
```

3. 「Commit new file」をクリック

✅ **完了の確認**: リポジトリに以下のファイルができていればOK
- `.github/workflows/image_generation.yml`
- `scripts/generate_image.py`

---

## Step 4: Cloudflare R2の設定（無料クラウドストレージ）

### 4-1. Cloudflareアカウント作成

1. https://dash.cloudflare.com/sign-up にアクセス
2. メールアドレスとパスワードを入力
3. メール認証を完了

### 4-2. R2を有効化

1. Cloudflareダッシュボードにログイン
2. 左メニューから「R2」をクリック
3. 「Purchase R2」→「Purchase Free Plan」をクリック（無料です）
4. クレジットカード情報を入力（無料枠内なら課金されません）

### 4-3. バケット（保存場所）を作成

1. 「Create bucket」をクリック
2. バケット名を入力: `my-image-storage`（好きな名前でOK）
3. Location: 「Automatic」のまま
4. 「Create bucket」をクリック

### 4-4. APIトークンを取得

1. 右上の「Manage R2 API Tokens」をクリック
2. 「Create API token」をクリック
3. 設定：
   - **Token name**: `github-actions-token`
   - **Permissions**: 「Object Read & Write」を選択
   - **Bucket**: 先ほど作った `my-image-storage` を選択
4. 「Create API Token」をクリック

### 4-5. 情報をメモ

表示される以下の情報を**必ずメモ**してください：
```
Account ID: xxxxxxxxxxxxxxxxxxxxx
Access Key ID: yyyyyyyyyyyyyyyyyyyy
Secret Access Key: zzzzzzzzzzzzzzzzzzzzzzzzzz
