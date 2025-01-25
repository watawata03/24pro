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
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import requests
from django.shortcuts import render
from django.db.models import Q
from .models import Character, Product
from translate import Translator
from .forms import CharacterImageForm
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CharacterForm  
from .models import Character  
from django.shortcuts import render
from django.http import JsonResponse
from .models import UserPreferences




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

def katakana_to_romaji(katakana_text):
    romaji_text = ""
    for char in katakana_text:
        romaji_text += KATAKANA_TO_ROMAJI.get(char, char)  
    return romaji_text


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

def character_list(request):
    response = requests.get('https://swapi.dev/api/people/')
    data = response.json()

    translations = {
        "Luke Skywalker": "ルーク・スカイウォーカー",
        "Darth Vader": "ダース・ベイダー",
    }
    for character in data['results']:
        character['image_url'] = f"https://example.com/images/{character['name'].replace(' ', '_')}.jpg"
        character['name_jp'] = translations.get(character['name'], character['name'])

    return render(request, 'character_list.html', {'characters': data['results']})


def search_results(request):
    query = request.GET.get('query')
    if query:
        character_results = Character.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        product_results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        character_results = Character.objects.none()
        product_results = Product.objects.none()
    return render(request, 'search_results.html', {
        'character_results': character_results,
        'product_results': product_results
    })



def index(request):
    preferences = UserPreferences.objects.first()
    color = preferences.text_color if preferences else "#000000"
    return render(request, "index.html", {"text_color": color})

# 色を保存するAPIエンドポイント
def save_color(request):
    if request.method == "POST":
        color = request.POST.get("color", "#000000")  # デフォルトは黒
        preferences, created = UserPreferences.objects.get_or_create(id=1)  # シングルトンの例
        preferences.text_color = color
        preferences.save()
        return JsonResponse({"message": "カラーが保存されました"})


def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all()  # 商品検索用
    characters = []  # キャラクター検索結果用
    character_name = request.GET.get('character', '').lower()  # キャラクター検索のクエリ
    sort_by = 'price_asc'  # デフォルトの並び替え順

    # 商品検索ロジック
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by', 'price_asc')

        # 商品名検索
        if query:
            results = results.filter(name__icontains=query)

        # カテゴリフィルタ
        if category:
            results = results.filter(category=category)

        # 価格フィルタ
        if min_price:
            results = results.filter(price__gte=min_price)
        if max_price:
            results = results.filter(price__lte=max_price)

        # 並び替え
        if sort_by == 'price_asc':
            results = results.order_by('price')
        elif sort_by == 'price_desc':
            results = results.order_by('-price')
        elif sort_by == 'name_asc':
            results = results.order_by('name')
        elif sort_by == 'name_desc':
            results = results.order_by('-name')
        elif sort_by == 'popularity':
            results = results.order_by('-popularity')

    # ページネーション（商品検索結果のみ）
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # キャラクター検索ロジック
    if character_name:
        url = f'https://swapi.dev/api/people/?search={character_name}'
        response = requests.get(url)
        if response.status_code == 200:
            results_data = response.json().get('results', [])
            for character in results_data:
                character['hair_color'] = translate_hair_color(character['hair_color'])
                character['skin_color'] = translate_skin_color(character['skin_color'])
                character['eye_color'] = translate_eye_color(character['eye_color'])
                character['gender'] = translate_gender(character['gender'])
                characters.append(character)

    context = {
        'form': form,
        'page_obj': page_obj,  # 商品検索のページネーション
        'characters': characters,  # キャラクター検索結果
        'character_name': character_name,  # キャラクター検索キーワード
        'total_results': paginator.count,  # 商品検索の総件数
    }

    return render(request, 'search.html', context)

# 詳細表示ビュー
def character_detail(request, pk):
    character = get_object_or_404(Character, pk=pk)
    return render(request, 'character_detail.html', {'character': character})

# 編集ビュー
def character_edit(request, pk):
    character = get_object_or_404(Character, pk=pk)
    if request.method == 'POST':
        form = CharacterImageForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            form.save()
            return redirect('character_detail', pk=character.pk)
    else:
        form = CharacterImageForm(instance=character)
    return render(request, 'character_edit.html', {'form': form, 'character': character})

# 商品リスト表示機能 - ログイン不要
def product_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product_list.html', {'page_obj': page_obj})


def update_character_image(request, pk):
    character = get_object_or_404(Character, pk=pk)
    if request.method == 'POST':
        form = CharacterImageForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            form.save()
            return redirect('character_list')  # 成功後にリストページなどにリダイレクト
    else:
        form = CharacterImageForm(instance=character)
    return render(request, 'update_character_image.html', {'form': form, 'character': character})

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

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # ユーザーを保存
            messages.success(request, "アカウントが作成されました！ログインしてください。")
            return redirect('login')  # ログインページへリダイレクト
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})




def character_list(request):
    characters = Character.objects.all()  # すべてのキャラクターを取得
    return render(request, 'character_list.html', {'characters': characters})


def character_list(request):
    # Character モデルからすべてのキャラクターを取得
    characters = Character.objects.all()
    
    # 取得したキャラクターをテンプレートに渡して表示
    return render(request, 'character_list.html', {'characters': characters})



@login_required
def character_create(request):
    if request.method == 'POST':
        form = CharacterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "キャラクターが作成されました！")
            return redirect('character_list')  # キャラクター一覧にリダイレクト
    else:
        form = CharacterForm()
    return render(request, 'character_create.html', {'form': form})



def character_create(request):
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES)  # Filsも扱うためrequest.FILESを追加
        if form.is_valid():
            form.save()  # 新しいキャラクターを保存
            return redirect('character_list')  # キャラクター一覧ページにリダイレクト
    else:
        form = CharacterForm()
    return render(request, 'character_form.html', {'form': form})



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
# views.py - search_view にキャラクター検索機能を統合
def search_view(request):
    form = SearchForm(request.GET or None)
    products = Product.objects.all()  # 商品検索用
    characters = []  # キャラクター検索結果用
    character_name = request.GET.get('character', '').lower()  # キャラクター検索のクエリ
    sort_by = 'price_asc'  # デフォルトの並び替え順

    # 商品検索ロジック
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by', 'price_asc')

        # 商品名検索
        if query:
            products = products.filter(name__icontains=query)

        # カテゴリフィルタ
        if category:
            products = products.filter(category=category)

        # 価格フィルタ
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # 並び替え
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'popularity':
            products = products.order_by('-popularity')

    # ページネーション（商品検索結果のみ）
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # キャラクター検索ロジック
    if character_name:
        url = f'https://swapi.dev/api/people/?search={character_name}'
        response = requests.get(url)
        if response.status_code == 200:
            results_data = response.json().get('results', [])
            for character in results_data:
                character['hair_color'] = translate_hair_color(character['hair_color'])
                character['skin_color'] = translate_skin_color(character['skin_color'])
                character['eye_color'] = translate_eye_color(character['eye_color'])
                character['gender'] = translate_gender(character['gender'])
                characters.append(character)

    # コンテキスト作成
    context = {
        'form': form,
        'page_obj': page_obj,  # 商品検索のページネーション
        'characters': characters,  # キャラクター検索結果
        'character_name': character_name,  # キャラクター検索キーワード
        'total_results': paginator.count,  # 商品検索の総件数
    }

    return render(request, 'search.html', context)
