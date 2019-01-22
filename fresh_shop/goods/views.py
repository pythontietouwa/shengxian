from django.core.paginator import Paginator
from django.shortcuts import render

from fresh_shop.settings import ORDER_NUMBER
from goods.models import GoodsCategory, Goods


def index(request):
    if request.method == 'GET':
        ddf = request.session.get('goods')
        ddf1 = request.COOKIES
        # 如果访问首页，返回渲染的首页index.html
        # 思路：组装结果[object1, object2, object3, object4, object5, object6]
        # 组装结果的对象object：包含分类，该分类的前四个商品信息
        # 方式1：object==>[GoodsCategory Object, [Goods.objects1, Goods.objects2, Goods.objects3, Goods.objects4]]
        # 方式2：object==>{'category_name': [Goods.objects1, Goods.objects2, Goods.objects3, Goods.objects4]}
        categorys = GoodsCategory.objects.all()
        result = []
        for category in categorys:
            goods = category.goods_set.all()[:4]
            data = [category, goods]
            result.append(data)
        category_type = GoodsCategory.CATEGORY_TYPE
        return render(request, 'index.html', {'result': result,
                                              'category_type': category_type})


def detail(request, id):
    if request.method == 'GET':
        # 返回详情页面解析的商品信息
        goods = Goods.objects.filter(pk=id).first()
        data = goods.goods_front_image
        category_type = GoodsCategory.CATEGORY_TYPE
        new_goods = Goods.objects.filter(category_id=goods.category_id)[:2]
        # 最近浏览
        cookies = request.session.get('goods_cookies', '')
        str_id = str(id)
        if cookies == '':
            # 说明是第一次浏览商品详情，本地还没有生成商品的cookie信息,那么直接将这个商品的id存到cookie。
            cookies = str_id + ';'  # '1;2;3;'
            request.session['goods_cookies'] = cookies
        else:
            # 说明不是第一次浏览商品详情，本地已经存在商品的cookie信息了；
            # 从'1;2;3;'这个cookie字符串中，取出每一个商品的id
            goods_id_list = cookies.split(';')  # ['1','2','3']
            # 判断当前浏览的这个商品的id是否存在于这个goods_id列表中，存在说明商品之前浏览过，不存在说明之前没有浏览过 。
            if str_id in goods_id_list:
                # 说明当前这个商品记录已经存在了，将这个记录从cookie中删除
                goods_id_list.remove(str_id)
            # 将这个记录插在所有元素的第一个，保证实时性
            goods_id_list.insert(0, str_id)
            # 如果大于五个则只保留五个数据
            if len(goods_id_list) >= 6:
                goods_id_list = goods_id_list[:5]
            cookies = ';'.join(goods_id_list)
            request.session['goods_cookies'] = cookies
        return render(request, 'detail.html',
                      {'data': data, 'goods': goods, 'category_type': category_type, 'new_goods': new_goods})


def list(request, id):
    if request.method == 'GET':
        all_goods = Goods.objects.filter(category_id=id)
        new_goods = Goods.objects.filter(category_id=id)[:2]
        page = int(request.GET.get('page', 1))
        pg = Paginator(all_goods, ORDER_NUMBER)
        ddf = pg.page(page)
        category_type = GoodsCategory.CATEGORY_TYPE
        return render(request, 'list.html',
                      {'all_goods': ddf, 'id': id, 'category_type': category_type, 'new_goods': new_goods})


def search(request):
    if request.method == 'GET':
        search_goods = request.GET.get('search_goods')
        goods = Goods.objects.filter(name__contains=search_goods)
        return render(request, 'search.html', {'goods': goods})

