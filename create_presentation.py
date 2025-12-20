"""
顧客リスト管理システム(cuslist) プレゼンテーション生成スクリプト
PowerPointファイルを生成します
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os

def create_presentation():
    """プレゼンテーションを作成する"""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # スライド1: タイトルスライド
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])  # 空白レイアウト
    
    # 背景色を設定
    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(30, 41, 59)  # ダークブルー
    
    # タイトル
    title_box = slide1.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(1))
    title_frame = title_box.text_frame
    title_frame.text = "顧客リスト管理システム"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(54)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(255, 255, 255)
    title_para.alignment = PP_ALIGN.CENTER
    
    # サブタイトル
    subtitle_box = slide1.shapes.add_textbox(Inches(1), Inches(3.8), Inches(8), Inches(0.8))
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = "Customer List Management System (cuslist)"
    subtitle_para = subtitle_frame.paragraphs[0]
    subtitle_para.font.size = Pt(28)
    subtitle_para.font.color.rgb = RGBColor(148, 163, 184)
    subtitle_para.alignment = PP_ALIGN.CENTER
    
    # 日付
    date_box = slide1.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(0.5))
    date_frame = date_box.text_frame
    date_frame.text = "2025年12月"
    date_para = date_frame.paragraphs[0]
    date_para.font.size = Pt(18)
    date_para.font.color.rgb = RGBColor(148, 163, 184)
    date_para.alignment = PP_ALIGN.CENTER
    
    # スライド2: システム概要
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide2.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide2.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "システム概要"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # 概要テキスト
    content_box = slide2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(5))
    content_frame = content_box.text_frame
    content_frame.word_wrap = True
    
    content_items = [
        "🎯 目的",
        "中小企業・個人事業主向けの顧客情報管理システム",
        "セキュアなデータ保存と柔軟な課金プランを提供",
        "",
        "✨ 主な特徴",
        "• AES暗号化による顧客情報の安全な保存",
        "• CSVベースの軽量なデータ管理",
        "• 6種類の柔軟な課金プラン",
        "• モダンでプレミアムなUI/UX",
        "• ログイン認証とアクセス制御",
        "",
        "🛠️ 技術スタック",
        "• Backend: Python 3.9+, Flask",
        "• Frontend: HTML5, Vanilla CSS",
        "• Security: Flask-WTF (CSRF), Cryptography (Fernet)",
        "• Data Storage: CSV (Encrypted)"
    ]
    
    for item in content_items:
        p = content_frame.add_paragraph()
        p.text = item
        if item.startswith(('🎯', '✨', '🛠️')):
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = RGBColor(79, 70, 229)
            p.space_before = Pt(12)
        elif item.startswith('•'):
            p.font.size = Pt(16)
            p.font.color.rgb = RGBColor(51, 65, 85)
            p.level = 1
        elif item == "":
            p.font.size = Pt(6)
        else:
            p.font.size = Pt(18)
            p.font.color.rgb = RGBColor(51, 65, 85)
    
    # スライド3: システムアーキテクチャ
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide3.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide3.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "システムアーキテクチャ"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # アーキテクチャ図を追加
    img_path = os.path.expanduser('~/.gemini/antigravity/brain/2ecf4b9b-d905-439f-8607-61c4b12275ba/system_architecture_1765672099551.png')
    if os.path.exists(img_path):
        slide3.shapes.add_picture(img_path, Inches(1), Inches(1.5), width=Inches(8))
    
    # 説明テキスト
    desc_box = slide3.shapes.add_textbox(Inches(0.8), Inches(6), Inches(8.4), Inches(1))
    desc_frame = desc_box.text_frame
    desc_frame.word_wrap = True
    p = desc_frame.paragraphs[0]
    p.text = "3層アーキテクチャによる明確な責務分離とセキュアなデータ管理"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(100, 116, 139)
    p.alignment = PP_ALIGN.CENTER
    
    # スライド4: 画面遷移図
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide4.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide4.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "画面遷移フロー"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # 画面遷移図を追加
    img_path = os.path.expanduser('~/.gemini/antigravity/brain/2ecf4b9b-d905-439f-8607-61c4b12275ba/screen_transition_flow_1765672124235.png')
    if os.path.exists(img_path):
        slide4.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), width=Inches(9))
    
    # スライド5: 主要機能
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide5.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide5.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "主要機能"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # 機能ボックス
    features = [
        {
            'title': '🔐 認証・セキュリティ',
            'items': [
                'ログイン認証機能',
                'パスワードハッシュ化',
                'ログイン試行回数制限',
                'CSRF保護',
                'セッション管理'
            ]
        },
        {
            'title': '👥 顧客管理',
            'items': [
                '顧客情報の登録・編集・削除',
                '高度な検索機能',
                'AES暗号化による保存',
                '顧客一覧表示',
                '操作ログ記録'
            ]
        },
        {
            'title': '💰 課金管理',
            'items': [
                'プラン別制限管理',
                '使用量カウント',
                '月次請求計算',
                '請求履歴管理',
                'プランアップグレード'
            ]
        },
        {
            'title': '👤 利用者管理',
            'items': [
                '利用者の追加・削除',
                'プラン変更',
                '権限管理',
                '利用状況確認',
                '管理者機能'
            ]
        }
    ]
    
    x_positions = [0.5, 5.2, 0.5, 5.2]
    y_positions = [1.5, 1.5, 4.2, 4.2]
    
    for i, feature in enumerate(features):
        # ボックス背景
        box = slide5.shapes.add_shape(
            1,  # Rectangle
            Inches(x_positions[i]),
            Inches(y_positions[i]),
            Inches(4.2),
            Inches(2.3)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(255, 255, 255)
        box.line.color.rgb = RGBColor(226, 232, 240)
        box.line.width = Pt(2)
        
        # タイトル
        title_box = slide5.shapes.add_textbox(
            Inches(x_positions[i] + 0.2),
            Inches(y_positions[i] + 0.15),
            Inches(3.8),
            Inches(0.4)
        )
        title_frame = title_box.text_frame
        title_frame.text = feature['title']
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(18)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(79, 70, 229)
        
        # アイテム
        items_box = slide5.shapes.add_textbox(
            Inches(x_positions[i] + 0.3),
            Inches(y_positions[i] + 0.6),
            Inches(3.6),
            Inches(1.5)
        )
        items_frame = items_box.text_frame
        items_frame.word_wrap = True
        
        for item in feature['items']:
            p = items_frame.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(12)
            p.font.color.rgb = RGBColor(51, 65, 85)
            p.space_after = Pt(4)
    
    # スライド6: 料金体系 - サブスクリプション型
    slide6 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide6.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide6.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "料金体系 - サブスクリプション型"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # プランカード
    plans = [
        {
            'name': 'Basic',
            'price': '¥500',
            'period': '/月',
            'features': [
                '顧客登録: 100件まで',
                '検索: 50回/日',
                '編集・削除: 無制限',
                'サポート: メール'
            ],
            'color': RGBColor(99, 102, 241)
        },
        {
            'name': 'Standard',
            'price': '¥1,500',
            'period': '/月',
            'features': [
                '顧客登録: 1,000件まで',
                '検索: 500回/日',
                '編集・削除: 無制限',
                'サポート: メール+チャット'
            ],
            'color': RGBColor(79, 70, 229)
        },
        {
            'name': 'Premium',
            'price': '¥3,000',
            'period': '/月',
            'features': [
                '顧客登録: 無制限',
                '検索: 無制限',
                '編集・削除: 無制限',
                'サポート: フルサポート'
            ],
            'color': RGBColor(67, 56, 202)
        }
    ]
    
    x_positions = [0.8, 3.7, 6.6]
    
    for i, plan in enumerate(plans):
        # カード背景
        card = slide6.shapes.add_shape(
            1,
            Inches(x_positions[i]),
            Inches(1.5),
            Inches(2.6),
            Inches(5)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(255, 255, 255)
        card.line.color.rgb = plan['color']
        card.line.width = Pt(3)
        
        # プラン名
        name_box = slide6.shapes.add_textbox(
            Inches(x_positions[i] + 0.2),
            Inches(1.7),
            Inches(2.2),
            Inches(0.5)
        )
        name_frame = name_box.text_frame
        name_frame.text = plan['name']
        name_para = name_frame.paragraphs[0]
        name_para.font.size = Pt(24)
        name_para.font.bold = True
        name_para.font.color.rgb = plan['color']
        name_para.alignment = PP_ALIGN.CENTER
        
        # 価格
        price_box = slide6.shapes.add_textbox(
            Inches(x_positions[i] + 0.2),
            Inches(2.3),
            Inches(2.2),
            Inches(0.7)
        )
        price_frame = price_box.text_frame
        price_frame.text = plan['price']
        price_para = price_frame.paragraphs[0]
        price_para.font.size = Pt(36)
        price_para.font.bold = True
        price_para.font.color.rgb = RGBColor(30, 41, 59)
        price_para.alignment = PP_ALIGN.CENTER
        
        # 期間
        period_box = slide6.shapes.add_textbox(
            Inches(x_positions[i] + 0.2),
            Inches(3),
            Inches(2.2),
            Inches(0.3)
        )
        period_frame = period_box.text_frame
        period_frame.text = plan['period']
        period_para = period_frame.paragraphs[0]
        period_para.font.size = Pt(14)
        period_para.font.color.rgb = RGBColor(100, 116, 139)
        period_para.alignment = PP_ALIGN.CENTER
        
        # 機能リスト
        features_box = slide6.shapes.add_textbox(
            Inches(x_positions[i] + 0.3),
            Inches(3.6),
            Inches(2),
            Inches(2.5)
        )
        features_frame = features_box.text_frame
        features_frame.word_wrap = True
        
        for feature in plan['features']:
            p = features_frame.add_paragraph()
            p.text = f"✓ {feature}"
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(51, 65, 85)
            p.space_after = Pt(8)
    
    # スライド7: 料金体系 - その他のプラン
    slide7 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide7.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide7.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "料金体系 - 従量課金・トランザクション型"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # 従量課金型
    usage_box = slide7.shapes.add_shape(
        1,
        Inches(0.8),
        Inches(1.5),
        Inches(4),
        Inches(2.5)
    )
    usage_box.fill.solid()
    usage_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
    usage_box.line.color.rgb = RGBColor(16, 185, 129)
    usage_box.line.width = Pt(3)
    
    usage_title = slide7.shapes.add_textbox(Inches(1), Inches(1.7), Inches(3.6), Inches(0.4))
    usage_title_frame = usage_title.text_frame
    usage_title_frame.text = "従量課金型"
    p = usage_title_frame.paragraphs[0]
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(16, 185, 129)
    p.alignment = PP_ALIGN.CENTER
    
    usage_content = slide7.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(3.2), Inches(1.5))
    usage_content_frame = usage_content.text_frame
    usage_content_frame.word_wrap = True
    
    usage_items = [
        "基本料金: ¥0/月",
        "顧客登録: ¥200/100件",
        "検索: ¥100/100回",
        "編集・削除: 無料"
    ]
    
    for item in usage_items:
        p = usage_content_frame.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(51, 65, 85)
        p.space_after = Pt(6)
    
    # トランザクション型
    trans_box = slide7.shapes.add_shape(
        1,
        Inches(5.2),
        Inches(1.5),
        Inches(4),
        Inches(2.5)
    )
    trans_box.fill.solid()
    trans_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
    trans_box.line.color.rgb = RGBColor(245, 158, 11)
    trans_box.line.width = Pt(3)
    
    trans_title = slide7.shapes.add_textbox(Inches(5.4), Inches(1.7), Inches(3.6), Inches(0.4))
    trans_title_frame = trans_title.text_frame
    trans_title_frame.text = "トランザクション型"
    p = trans_title_frame.paragraphs[0]
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(245, 158, 11)
    p.alignment = PP_ALIGN.CENTER
    
    trans_content = slide7.shapes.add_textbox(Inches(5.6), Inches(2.3), Inches(3.2), Inches(1.5))
    trans_content_frame = trans_content.text_frame
    trans_content_frame.word_wrap = True
    
    trans_items = [
        "顧客登録: ¥10/件",
        "顧客編集: ¥5/件",
        "顧客削除: 無料",
        "検索: ¥1/回"
    ]
    
    for item in trans_items:
        p = trans_content_frame.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(51, 65, 85)
        p.space_after = Pt(6)
    
    # ハイブリッド型
    hybrid_box = slide7.shapes.add_shape(
        1,
        Inches(2.5),
        Inches(4.3),
        Inches(5),
        Inches(2.5)
    )
    hybrid_box.fill.solid()
    hybrid_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
    hybrid_box.line.color.rgb = RGBColor(168, 85, 247)
    hybrid_box.line.width = Pt(3)
    
    hybrid_title = slide7.shapes.add_textbox(Inches(2.7), Inches(4.5), Inches(4.6), Inches(0.4))
    hybrid_title_frame = hybrid_title.text_frame
    hybrid_title_frame.text = "ハイブリッド型"
    p = hybrid_title_frame.paragraphs[0]
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(168, 85, 247)
    p.alignment = PP_ALIGN.CENTER
    
    hybrid_content = slide7.shapes.add_textbox(Inches(2.9), Inches(5.1), Inches(4.2), Inches(1.5))
    hybrid_content_frame = hybrid_content.text_frame
    hybrid_content_frame.word_wrap = True
    
    hybrid_items = [
        "基本料金: ¥1,000/月",
        "顧客登録: 500件まで無料、超過分¥500/500件",
        "検索: 200回/日まで無料、超過分¥100/100回",
        "編集・削除: 無制限"
    ]
    
    for item in hybrid_items:
        p = hybrid_content_frame.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(51, 65, 85)
        p.space_after = Pt(6)
    
    # スライド8: セキュリティ機能
    slide8 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide8.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(248, 250, 252)
    
    # タイトル
    title_box = slide8.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "セキュリティ機能"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(36)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(30, 41, 59)
    
    # セキュリティ項目
    security_items = [
        {
            'icon': '🔐',
            'title': 'データ暗号化',
            'desc': '顧客情報はAES-256で暗号化してCSVに保存。万が一ファイルが流出しても復号不可能。'
        },
        {
            'icon': '🔑',
            'title': 'パスワード保護',
            'desc': 'ユーザーパスワードはハッシュ化（bcrypt）して保存。平文での保存は一切なし。'
        },
        {
            'icon': '🛡️',
            'title': 'CSRF保護',
            'desc': 'Flask-WTFによるCSRFトークン検証で、クロスサイトリクエストフォージェリを防止。'
        },
        {
            'icon': '⏱️',
            'title': 'ログイン試行制限',
            'desc': 'ブルートフォース攻撃対策として、連続ログイン失敗時にアカウントを一時ロック。'
        },
        {
            'icon': '📝',
            'title': '操作ログ記録',
            'desc': '全ての顧客情報操作（登録・編集・削除・検索）を記録し、監査証跡を確保。'
        },
        {
            'icon': '👤',
            'title': 'アクセス制御',
            'desc': 'セッションベースの認証により、未認証ユーザーは顧客情報にアクセス不可。'
        }
    ]
    
    y_pos = 1.5
    for item in security_items:
        # アイコン
        icon_box = slide8.shapes.add_textbox(Inches(1), Inches(y_pos), Inches(0.5), Inches(0.5))
        icon_frame = icon_box.text_frame
        icon_frame.text = item['icon']
        icon_para = icon_frame.paragraphs[0]
        icon_para.font.size = Pt(28)
        
        # タイトル
        title_box = slide8.shapes.add_textbox(Inches(1.8), Inches(y_pos), Inches(7.5), Inches(0.4))
        title_frame = title_box.text_frame
        title_frame.text = item['title']
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(18)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(79, 70, 229)
        
        # 説明
        desc_box = slide8.shapes.add_textbox(Inches(1.8), Inches(y_pos + 0.4), Inches(7.5), Inches(0.5))
        desc_frame = desc_box.text_frame
        desc_frame.word_wrap = True
        desc_frame.text = item['desc']
        desc_para = desc_frame.paragraphs[0]
        desc_para.font.size = Pt(13)
        desc_para.font.color.rgb = RGBColor(71, 85, 105)
        
        y_pos += 0.95
    
    # スライド9: まとめ
    slide9 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide9.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(30, 41, 59)
    
    # タイトル
    title_box = slide9.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(1))
    title_frame = title_box.text_frame
    title_frame.text = "まとめ"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(48)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(255, 255, 255)
    title_para.alignment = PP_ALIGN.CENTER
    
    # ポイント
    points_box = slide9.shapes.add_textbox(Inches(1.5), Inches(3.2), Inches(7), Inches(3))
    points_frame = points_box.text_frame
    points_frame.word_wrap = True
    
    points = [
        "✓ セキュアな顧客情報管理システム",
        "✓ 柔軟な6種類の課金プラン",
        "✓ 軽量なCSVベースのデータ管理",
        "✓ モダンでプレミアムなUI/UX",
        "✓ 中小企業・個人事業主に最適"
    ]
    
    for point in points:
        p = points_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(24)
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.space_after = Pt(12)
        p.alignment = PP_ALIGN.CENTER
    
    # 保存
    output_path = '/Applications/Eclipse_2024-09.app/Contents/workspace/GeminiPj/cuslist/顧客リスト管理システム_プレゼンテーション.pptx'
    prs.save(output_path)
    print(f"プレゼンテーションを作成しました: {output_path}")
    return output_path

if __name__ == '__main__':
    create_presentation()
