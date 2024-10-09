from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category
from .forms import ProductForm, SearchForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import SimpleTextForm
from .forms import CategoryForm 

## 商品検索機能
def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all()  # クエリセットの初期化
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')  # 並び替えオプションを取得
        
        # 名前で部分一致検索
        if query:
            results = results.filter(name__icontains=query)

        # カテゴリでフィルタリング
        if category:
            results = results.filter(category=category)

        # 価格フィルタリング
        if min_price is not None and min_price != '':
            results = results.filter(price__gte=float(min_price))
        if max_price is not None and max_price != '':
            results = results.filter(price__lte=float(max_price))

        # 並び替え処理
        if sort_by == 'price_asc':
            results = results.order_by('price')
        elif sort_by == 'price_desc':
            results = results.order_by('-price')
        elif sort_by == 'popularity':
            results = results.order_by('-popularity')  # 商品モデルに人気度フィールドがある前提

    # 検索結果の数を取得
    total_results = results.count()

    # ページネーションの設定
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAXリクエストの場合、JSON形式で検索結果を返す
        products = [
            {
                'name': product.name,
                'price': product.price,
            } for product in page_obj
        ]
        return JsonResponse({
            'results': products,
            'total_results': total_results
        })

    # 通常のリクエストの場合はHTMLテンプレートを返す
    return render(request, 'search.html', {
        'form': form,
        'page_obj': page_obj,
        'total_results': total_results  # 結果数をテンプレートに渡す
    })

# 商品リスト表示機能
def product_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)  # 1ページあたり10件表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product_list.html', {'page_obj': page_obj})

# 商品作成機能
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # 商品作成後にリストへリダイレクト
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# 商品詳細表示
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

# 商品更新機能
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
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

# カテゴリ作成機能
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # カテゴリ作成後にリストへリダイレクト
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})
    

# 商品テキスト入力機能
def simple_text_view(request):
    if request.method == 'POST':
        form = SimpleTextForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text_input']
            return render(request, 'text_result.html', {'text': text})
    else:
        form = SimpleTextForm()

    return render(request, 'simple_text_form.html', {'form': form})
