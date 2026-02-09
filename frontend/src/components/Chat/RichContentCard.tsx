import React from 'react';
import { RichContent } from '../../types';
import { ProductRecommendation } from '../../types';

interface RichContentCardProps {
  content: RichContent;
}

const RichContentCard: React.FC<RichContentCardProps> = ({ content }) => {
  const renderProductCard = (data: Record<string, unknown>) => {
    const product = data as ProductRecommendation;
    return (
      <div className="rich-card overflow-hidden">
        {product.imageUrl && (
          <img src={product.imageUrl} alt={product.name} className="w-full h-48 object-cover" />
        )}
        <div className="p-4">
          <h4 className="text-white font-semibold">{product.name}</h4>
          <p className="text-white/60 text-sm mt-1">{product.description}</p>
          {product.price && (
            <p className="text-primary-400 font-medium mt-2">${product.price}</p>
          )}
          <div className="flex flex-wrap gap-1 mt-2">
            {Object.entries(product.attributes || {}).map(([key, value]) => (
              <span key={key} className="text-xs px-2 py-0.5 bg-white/10 rounded-full text-white/60">
                {key}: {value}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderStepGuide = (data: Record<string, unknown>) => {
    const steps = data.steps as { title: string; description: string }[];
    return (
      <div className="space-y-3">
        {steps?.map((step, idx) => (
          <div key={idx} className="flex gap-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500 text-white flex items-center justify-center text-sm font-medium">
              {idx + 1}
            </div>
            <div>
              <h4 className="text-white font-medium">{step.title}</h4>
              <p className="text-white/60 text-sm">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderList = (data: Record<string, unknown>) => {
    const items = data.items as string[];
    return (
      <ul className="space-y-2">
        {items?.map((item, idx) => (
          <li key={idx} className="flex items-start gap-2 text-white/80">
            <span className="text-primary-400 mt-1">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    );
  };

  switch (content.type) {
    case 'product_card':
      return renderProductCard(content.data);
    case 'step_guide':
      return renderStepGuide(content.data);
    case 'list':
      return renderList(content.data);
    default:
      return null;
  }
};

export default RichContentCard;
