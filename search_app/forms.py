from django import forms
from .models import Product, Category

class SearchForm(forms.Form):
    query = forms.CharField(
        label='検索キーワード',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '検索したいキーワードを入力', 'class': 'form-control'})
    )

    # カテゴリの選択肢
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='カテゴリ',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # 価格範囲の指定
    min_price = forms.DecimalField(
        required=False,
        label='最低価格',
        widget=forms.NumberInput(attrs={'placeholder': '最低価格', 'class': 'form-control'})
    )
    max_price = forms.DecimalField(
        required=False,
        label='最高価格',
        widget=forms.NumberInput(attrs={'placeholder': '最高価格', 'class': 'form-control'})
    )

    # 並び替えの選択肢
    sort_by = forms.ChoiceField(
        required=False,
        choices=[('price_asc', '価格の安い順'), ('price_desc', '価格の高い順'), ('popularity', '人気順')],
        label='並び替え',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # バリデーション: 最低価格が最高価格を超えないようにする
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError('最低価格は最高価格以下である必要があります。')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '商品名'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '商品説明'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '価格'}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }

class SimpleTextForm(forms.Form):
    text_input = forms.CharField(
        label='テキスト入力',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'テキストを入力してください'})
    )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
