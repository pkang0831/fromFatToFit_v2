'use client';

import { CheckCircle, AlertTriangle, XCircle, AlertCircle, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/progress';

interface DecisionReason {
  type: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
}

interface FoodItem {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  serving_size?: string;
  sodium?: number;
  sugar?: number;
}

interface ImpactAnalysis {
  calories_used_percentage: number;
  remaining_calories: number;
  remaining_protein: number;
  remaining_carbs: number;
  remaining_fat: number;
}

interface AlternativeFood {
  food_id: string;
  name: string;
  category: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  reason: string;
}

interface ShouldIEatResponse {
  decision: 'green' | 'yellow' | 'red';
  decision_text: string;
  food_items: FoodItem[];
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  total_sodium?: number;
  total_sugar?: number;
  impact: ImpactAnalysis;
  reasons: DecisionReason[];
  ai_advice: string;
  alternatives?: AlternativeFood[];
  confidence: string;
}

interface Props {
  result: ShouldIEatResponse;
  onEatAnyway: () => void;
  onFindAlternative: () => void;
}

export function FoodDecisionResult({ result, onEatAnyway, onFindAlternative }: Props) {
  const decisionConfig = {
    green: {
      icon: CheckCircle,
      bgGradient: 'bg-gradient-to-br from-green-400 to-green-600',
      textColor: 'text-white',
      iconColor: 'text-white',
      title: '좋은 선택이에요! 👍',
    },
    yellow: {
      icon: AlertTriangle,
      bgGradient: 'bg-gradient-to-br from-yellow-400 to-orange-500',
      textColor: 'text-white',
      iconColor: 'text-white',
      title: '주의하세요 ⚠️',
    },
    red: {
      icon: XCircle,
      bgGradient: 'bg-gradient-to-br from-red-400 to-red-600',
      textColor: 'text-white',
      iconColor: 'text-white',
      title: '다시 생각해보세요 🚫',
    },
  };

  const config = decisionConfig[result.decision];
  const Icon = config.icon;

  return (
    <div className="space-y-6">
      {/* Decision Header with Gradient */}
      <Card className={`${config.bgGradient} shadow-2xl border-0`}>
        <CardContent className="p-8">
          <div className="flex flex-col items-center text-center">
            <Icon className={`h-20 w-20 ${config.iconColor} animate-pulse mb-4`} />
            <h2 className={`text-3xl font-bold ${config.textColor} mb-2`}>
              {config.title}
            </h2>
            <p className={`text-lg ${config.textColor} opacity-90`}>
              {result.decision_text}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Food Items */}
      <Card>
        <CardHeader>
          <CardTitle>음식 분석</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {result.food_items.map((item, idx) => (
              <div key={idx} className="flex justify-between py-2 border-b last:border-0">
                <span className="font-medium">{item.name}</span>
                <span className="text-gray-600">{item.calories.toFixed(0)} kcal</span>
              </div>
            ))}
          </div>
          <div className="flex justify-between py-3 mt-2 font-bold text-lg border-t-2">
            <span>총합</span>
            <span>{result.total_calories.toFixed(0)} kcal</span>
          </div>
          <div className="grid grid-cols-3 gap-2 mt-3 text-sm text-center">
            <div>
              <div className="text-gray-600">단백질</div>
              <div className="font-semibold">{result.total_protein.toFixed(1)}g</div>
            </div>
            <div>
              <div className="text-gray-600">탄수화물</div>
              <div className="font-semibold">{result.total_carbs.toFixed(1)}g</div>
            </div>
            <div>
              <div className="text-gray-600">지방</div>
              <div className="font-semibold">{result.total_fat.toFixed(1)}g</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Impact Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>영향 분석</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span>오늘 칼로리 사용량</span>
              <span className="font-bold">
                {result.impact.calories_used_percentage.toFixed(0)}%
              </span>
            </div>
            <Progress value={result.impact.calories_used_percentage} className="h-3" />
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-gray-600">남은 칼로리</div>
              <div className="font-bold text-lg">{result.impact.remaining_calories.toFixed(0)} kcal</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-gray-600">남은 단백질</div>
              <div className="font-bold text-lg">{result.impact.remaining_protein.toFixed(0)}g</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reasons */}
      {result.reasons.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>상세 분석</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {result.reasons.map((reason, idx) => (
              <div
                key={idx}
                className={`flex items-start gap-2 p-3 rounded-lg ${
                  reason.severity === 'critical'
                    ? 'bg-red-50 border border-red-200'
                    : reason.severity === 'warning'
                    ? 'bg-yellow-50 border border-yellow-200'
                    : 'bg-blue-50 border border-blue-200'
                }`}
              >
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <p className="text-sm">{reason.message}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* AI Advice */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            AI 코치의 조언
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-800 leading-relaxed">{result.ai_advice}</p>
        </CardContent>
      </Card>

      {/* Alternatives (if yellow/red) */}
      {result.alternatives && result.alternatives.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>대신 이건 어때요?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {result.alternatives.map((alt, idx) => (
              <button
                key={idx}
                className="w-full text-left p-4 rounded-lg border-2 border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition"
                onClick={() => onFindAlternative()}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-semibold text-lg">{alt.name}</div>
                    <div className="text-sm text-gray-600 mt-1">{alt.category}</div>
                    <div className="flex gap-3 mt-2 text-sm text-gray-700">
                      <span>{alt.calories.toFixed(0)} kcal</span>
                      <span>단백질 {alt.protein.toFixed(1)}g</span>
                    </div>
                    <p className="text-sm text-blue-700 mt-2">💡 {alt.reason}</p>
                  </div>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Button
          variant="outline"
          size="lg"
          onClick={onFindAlternative}
          className="flex-1"
        >
          다른 음식 찾기
        </Button>
        <Button
          size="lg"
          onClick={onEatAnyway}
          className="flex-1"
        >
          {result.decision === 'green' ? '먹기' : '그래도 먹기'}
        </Button>
      </div>
    </div>
  );
}
