from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from product.serializers import ProductFeedSerializer, ProductCreateSerializer, ProductCategorySerializer
from product.models import Product, ProductCategory
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics


# 페이지네이션
class StandardResultsSetPagination(PageNumberPagination):
    """
    마무리할때 size조정 필요
    """
    page_size = 20


# 판매중 상품 피드 페이지
"""모든 사용자"""
class ProductFeedView(generics.ListAPIView):
    queryset = Product.objects.filter(transaction_status=0, is_hide=False).order_by('-refreshed_at')
    serializer_class = ProductFeedSerializer
    pagination_class = StandardResultsSetPagination


# 상품 등록
"""로그인 사용자"""
class ProductCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 상품 자세히보기 수정 삭제
"""로그인 사용자"""
class ProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 자세히보기
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductFeedSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 수정
    def put(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        if request.user == product.user:
            serializer = ProductCreateSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

    # 삭제
    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # 작성자만 삭제 가능하게
        if request.user == product.user:
            product.delete()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)


# 관심상품 리스트
"""로그인 사용자"""
class ProductBookmarkView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductFeedSerializer
    pagination_class = StandardResultsSetPagination

    # user_id 가져오기 위해 오버라이딩
    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Product.objects.filter(transaction_status=0, is_hide=False, bookmark=user_id).order_by('-refreshed_at')
        """거래중, 숨김상태 아님, 요청유저가 북마크한것만"""
        return queryset


# 상품 카테고리 페이지
class ProductCategoryView(APIView):
    def get(self, request):
        categories = ProductCategory.objects.filter(is_used=True)
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
