// Product Card Component for RAG results
import React from 'react';
import { Tag, Star } from 'lucide-react';

interface Product {
  id: string;
  title: string;
  description: string;
  relevance: number;
}

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  return (
    <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-4 mt-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold text-indigo-900 flex items-center gap-2">
            <Tag size={14} />
            {product.title}
          </h4>
          <p className="text-sm text-gray-600 mt-1">{product.description}</p>
        </div>
        <div className="flex items-center gap-1 bg-indigo-100 px-2 py-1 rounded-full">
          <Star size={12} className="text-indigo-600" />
          <span className="text-xs font-medium text-indigo-600">
            {Math.min((product.relevance || 0) * 100, 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
};

interface ProductListProps {
  products: Product[];
}

export const ProductList: React.FC<ProductListProps> = ({ products }) => {
  if (!products || products.length === 0) return null;

  return (
    <div className="mt-3">
      <p className="text-xs font-semibold text-gray-500 mb-2 flex items-center gap-1">
        <Tag size={12} /> Recommended Products
      </p>
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};

export default ProductCard;
