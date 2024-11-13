from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, SearchHistory
from .forms import ProductForm, SearchForm, SimpleTextForm, CategoryForm, FileNameForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
import csv
import requests

import requests
from django.shortcuts import render
from translate import Translator



KATAKANA_TO_ROMAJI = {
    'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
    'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
    'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
    'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
    'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
    'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
    'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
    'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
    'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
    'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
    'ガ': 'ga', 'ギ': 'gi', 'グ': 'gu', 'ゲ': 'ge', 'ゴ': 'go',
    'ザ': 'za', 'ジ': 'ji', 'ズ': 'zu', 'ゼ': 'ze', 'ゾ': 'zo',
    'ダ': 'da', 'ヂ': 'ji', 'ヅ': 'zu', 'デ': 'de', 'ド': 'do',
    'バ': 'ba', 'ビ': 'bi', 'ブ': 'bu', 'ベ': 'be', 'ボ': 'bo',
    'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po'
}


# 商品検索機能 - ログイン不要
def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all()  # クエリセットの初期化
    sort_by = 'price_asc'  # デフォルトのソート順は価格昇順

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by', 'price_asc')

        # 検索履歴を保存
        SearchHistory.objects.create(
            query=query,
            category=category.name if category else "指定なし",
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by
        )

        # フル一致と部分一致の検索
        if query:
            exact_match_results = results.filter(name=query)
            if exact_match_results.exists():
                results = exact_match_results
            else:
                partial_match_results = results.filter(name__icontains=query)
                if partial_match_results.exists():
                    results = partial_match_results
                else:
                    # フルテキスト検索とランキング
                    search_vector = SearchVector('name', 'description')
                    search_query = SearchQuery(query)
                    results = results.annotate(
                        rank=SearchRank(search_vector, search_query)
                    ).filter(rank__gte=0.1).order_by('-rank')

        # カテゴリによるフィルタリング
        if category:
            results = results.filter(category=category)

        # 価格フィルタリング
        if min_price:
            results = results.filter(price__gte=float(min_price))
        if max_price:
            results = results.filter(price__lte=float(max_price))

        # 並び替え処理
        if sort_by == 'price_asc':
            results = results.order_by('price')
        elif sort_by == 'price_desc':
            results = results.order_by('-price')
        elif sort_by == 'name_asc':
            results = results.order_by('name')
        elif sort_by == 'name_desc':
            results = results.order_by('-name')
        elif sort_by == 'popularity':
            results = results.order_by('-popularity')  # 人気順で並び替え

    # 検索履歴の取得
    search_history = SearchHistory.objects.order_by('-searched_at')[:10]  # 最新10件を表示

    # ページネーションの設定
    total_results = results.count()
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 「あなたにおすすめ」商品リスト（人気度順に上位5つ）
    recommended_products = Product.objects.order_by('-popularity')[:5]

    return render(request, 'search.html', {
        'form': form,
        'page_obj': page_obj,
        'total_results': total_results,
        'sort_by': sort_by,
        'recommended_products': recommended_products,
        'search_history': search_history,
    })

# 検索履歴削除機能
@login_required
def delete_search_history(request, history_id):
    history = get_object_or_404(SearchHistory, id=history_id)
    history.delete()
    messages.success(request, "検索履歴が削除されました")
    return redirect('search_view')

# 商品リスト表示機能 - ログイン不要
def product_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product_list.html', {'page_obj': page_obj})

# 商品作成機能
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# 商品詳細表示
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # 人気度を1増加させる（上限を100とする）
    if product.popularity < 100:
        product.popularity += 1
    product.save()

    # 人気度順に上位5つのレコメンド商品（自身を除外）
    recommended_products = Product.objects.exclude(pk=pk).order_by('-popularity')[:5]
    category_related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:5]

    return render(request, 'product_detail.html', {
        'product': product,
        'recommended_products': recommended_products,
        'category_related_products': category_related_products
    })

# 商品更新機能
@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'product': product})

# 商品削除機能
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

# カテゴリ作成機能
@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

# 商品テキスト入力機能
@login_required
def simple_text_view(request):
    if request.method == 'POST':
        form = SimpleTextForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text_input']
            return render(request, 'text_result.html', {'text': text})
    else:
        form = SimpleTextForm()
    return render(request, 'simple_text_form.html', {'form': form})

# CSVアップロード機能
@login_required
def upload_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        file_data = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(file_data)
        next(reader)

        for row in reader:
            name, price, category_name = row
            category, created = Category.objects.get_or_create(name=category_name)
            Product.objects.create(
                name=name,
                price=float(price.replace('¥', '').replace(',', '')), 
                category=category
            )
        return redirect('product_list')

    return render(request, 'upload_csv.html')

# SWAPIのデータを取得する新しいビュー
# views.py
from django.shortcuts import render
import requests

# views.py
from django.shortcuts import render
import requests

def swapi_character_search(request):
    character_name = request.GET.get('character', '').lower()
    characters = []

    if character_name:
        url = f'https://swapi.dev/api/people/?search={character_name}'
        response = requests.get(url)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            for character in results:
                # 日本語に変換
                character['hair_color'] = translate_hair_color(character['hair_color'])
                character['skin_color'] = translate_skin_color(character['skin_color'])
                character['eye_color'] = translate_eye_color(character['eye_color'])
                character['gender'] = translate_gender(character['gender'])
                characters.append(character)
        else:
            characters = None  # APIエラー時にNoneを設定

    return render(request, 'swapi_character_search.html', {'characters': characters, 'character_name': character_name})

# 属性を日本語に変換する関数
def translate_hair_color(color):
    translations = {
        "blond": "金髪",
        "brown": "茶色",
        "black": "黒",
        "red": "赤",
        "gray": "灰色",
        "white": "白",
        "none": "なし",
    }
    return translations.get(color, color)

def translate_skin_color(color):
    translations = {
        "fair": "色白",
        "gold": "金色",
        "light": "明るい",
        "dark": "暗い",
        "green": "緑",
        "blue": "青",
        "red": "赤",
        "white": "白",
        "brown": "茶色",
    }
    return translations.get(color, color)

def translate_eye_color(color):
    translations = {
        "blue": "青",
        "brown": "茶色",
        "green": "緑",
        "yellow": "黄色",
        "red": "赤",
        "black": "黒",
        "orange": "オレンジ",
    }
    return translations.get(color, color)

def translate_gender(gender):
    translations = {
        "male": "男性",
        "female": "女性",
        "n/a": "該当なし",
    }
    return translations.get(gender, gender)



def katakana_to_romaji(katakana_text):
    romaji_text = ""
    for char in katakana_text:
        romaji_text += KATAKANA_TO_ROMAJI.get(char, char)  # 対応がない場合はそのまま
    return romaji_text

# 例の使用
katakana_name = "ルーク"
romaji_name = katakana_to_romaji(katakana_name)
print(f"カタカナ「{katakana_name}」をローマ字に変換: {romaji_name}")




# 検索結果のCSVエクスポート機能
@login_required
def export_search_results_csv(request):
    if request.method == 'POST':
        form = FileNameForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['file_name']
            if not file_name.endswith('.csv'):
                file_name += '.csv'

            query = request.GET.get('query', '')
            category = request.GET.get('category', None)
            min_price = request.GET.get('min_price', None)
            max_price = request.GET.get('max_price', None)

            results = Product.objects.all()  # 必要に応じて条件を追加

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'

            writer = csv.writer(response)
            writer.writerow(['商品名', '価格', 'カテゴリ', '人気度'])

            for product in results:
                writer.writerow([product.name, product.price, product.category.name, product.popularity])

            return response
    else:
        form = FileNameForm()

    return render(request, 'export_csv_form.html', {'form': form})


def swapi_all_data(request):
    # SWAPIの主要エンドポイント
    endpoints = {
        "people": "https://swapi.dev/api/people/",
        "planets": "https://swapi.dev/api/planets/",
        "starships": "https://swapi.dev/api/starships/",
        "vehicles": "https://swapi.dev/api/vehicles/",
        "species": "https://swapi.dev/api/species/",
        "films": "https://swapi.dev/api/films/",
    }

    data = {}

    # 各エンドポイントのデータを取得
    for category, url in endpoints.items():
        all_results = []
        while url:
            response = requests.get(url)
            if response.status_code == 200:
                page_data = response.json()
                all_results.extend(page_data['results'])
                url = page_data['next']  # 次のページがあればURLを更新
            else:
                url = None
        data[category] = all_results

    return render(request, 'swapi_all_data.html', {'data': data})