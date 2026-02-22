'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { Trash2, Edit } from 'lucide-react';
import { Card, CardContent, Button, Badge, ConfirmDialog } from '@/components/ui';
import { Input, Select } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { foodApi } from '@/lib/api/services';
import type { FoodLog } from '@/types/api';

interface MealCardProps {
  meal: FoodLog;
  onDelete: () => void;
  onUpdate: () => void;
}

export function MealCard({ meal, onDelete, onUpdate }: MealCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    food_name: meal.food_name,
    calories: meal.calories,
    protein: meal.protein || 0,
    carbs: meal.carbs || 0,
    fat: meal.fat || 0,
    serving_size: meal.serving_size || '',
    meal_type: meal.meal_type,
  });

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await foodApi.deleteLog(meal.id);
      onDelete();
      toast.success('Meal deleted');
    } catch (error) {
      console.error('Failed to delete meal:', error);
      toast.error('Failed to delete meal');
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleEdit = async () => {
    try {
      await foodApi.updateLog(meal.id, {
        date: meal.date,
        food_name: editData.food_name,
        calories: editData.calories,
        protein: editData.protein,
        carbs: editData.carbs,
        fat: editData.fat,
        serving_size: editData.serving_size,
        meal_type: editData.meal_type,
      });
      setIsEditing(false);
      onUpdate();
      toast.success('Meal updated');
    } catch (error) {
      console.error('Failed to update meal:', error);
      toast.error('Failed to update meal');
    }
  };

  const getMealTypeBadgeVariant = (type: string) => {
    switch (type) {
      case 'breakfast':
        return 'info';
      case 'lunch':
        return 'success';
      case 'dinner':
        return 'warning';
      case 'snack':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Card variant="outlined" className="hover:shadow-lg hover:-translate-y-1 transition-all">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h4 className="font-semibold text-gray-900 dark:text-white">{meal.food_name}</h4>
              <Badge variant={getMealTypeBadgeVariant(meal.meal_type)}>
                {meal.meal_type}
              </Badge>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Calories:</span>
                <span className="font-medium text-gray-900 dark:text-white ml-1">{Math.round(meal.calories)}</span>
              </div>
              {meal.protein !== undefined && (
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Protein:</span>
                  <span className="font-medium text-gray-900 dark:text-white ml-1">{Math.round(meal.protein)}g</span>
                </div>
              )}
              {meal.carbs !== undefined && (
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Carbs:</span>
                  <span className="font-medium text-gray-900 dark:text-white ml-1">{Math.round(meal.carbs)}g</span>
                </div>
              )}
              {meal.fat !== undefined && (
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Fat:</span>
                  <span className="font-medium text-gray-900 dark:text-white ml-1">{Math.round(meal.fat)}g</span>
                </div>
              )}
            </div>

            {meal.serving_size && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Serving: {meal.serving_size}
              </p>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditing(true)}
              className="text-primary hover:bg-primary/10"
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isDeleting}
              className="text-error hover:bg-error/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <ConfirmDialog
          isOpen={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
          onConfirm={handleDelete}
          title="Delete Food Entry"
          message="Are you sure you want to delete this food entry? This cannot be undone."
          loading={isDeleting}
        />

        {/* Edit Modal */}
        {isEditing && (
          <Modal
            isOpen={isEditing}
            onClose={() => setIsEditing(false)}
            title="Edit Food Log"
          >
            <div className="space-y-4">
              <Input
                label="Food Name"
                value={editData.food_name}
                onChange={(e) => setEditData({ ...editData, food_name: e.target.value })}
                placeholder="Food name"
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Calories"
                  type="number"
                  value={editData.calories}
                  onChange={(e) => setEditData({ ...editData, calories: parseFloat(e.target.value) || 0 })}
                  placeholder="Calories"
                />
                <Input
                  label="Serving Size"
                  value={editData.serving_size}
                  onChange={(e) => setEditData({ ...editData, serving_size: e.target.value })}
                  placeholder="e.g., 100g"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <Input
                  label="Protein (g)"
                  type="number"
                  value={editData.protein}
                  onChange={(e) => setEditData({ ...editData, protein: parseFloat(e.target.value) || 0 })}
                  placeholder="Protein"
                />
                <Input
                  label="Carbs (g)"
                  type="number"
                  value={editData.carbs}
                  onChange={(e) => setEditData({ ...editData, carbs: parseFloat(e.target.value) || 0 })}
                  placeholder="Carbs"
                />
                <Input
                  label="Fat (g)"
                  type="number"
                  value={editData.fat}
                  onChange={(e) => setEditData({ ...editData, fat: parseFloat(e.target.value) || 0 })}
                  placeholder="Fat"
                />
              </div>

              <div>
                <Select
                  label="Meal Type"
                  value={editData.meal_type}
                  onChange={(e) => setEditData({ ...editData, meal_type: e.target.value as 'breakfast' | 'lunch' | 'dinner' | 'snack' })}
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </Select>
              </div>

              <div className="flex gap-3 justify-end pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsEditing(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleEdit}
                >
                  Save Changes
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </CardContent>
    </Card>
  );
}
