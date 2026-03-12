/**
 * Semantic segmentation class definitions.
 *
 * Each pixel in the label map stores one of these class IDs.
 * left/right = person's anatomical left/right (NOT viewer's screen left/right).
 *
 * To add a new class: append to SEG_CLASSES, bump NUM_CLASSES.
 */

export interface SegClass {
  id: number;
  key: string;
  label: string;
  color: [number, number, number];
}

export const SEG_CLASSES: SegClass[] = [
  { id: 0, key: 'background',     label: 'Background',   color: [0, 0, 0] },
  { id: 1, key: 'head',           label: 'Head',          color: [160, 160, 160] },
  { id: 2, key: 'chest',          label: 'Chest',         color: [255, 140, 0] },
  { id: 3, key: 'torso',          label: 'Torso',         color: [255, 99, 71] },
  { id: 4, key: 'left_shoulder',  label: 'L Shoulder',    color: [218, 112, 214] },
  { id: 5, key: 'right_shoulder', label: 'R Shoulder',    color: [255, 105, 180] },
  { id: 6, key: 'left_arm',       label: 'L Arm',         color: [50, 205, 50] },
  { id: 7, key: 'right_arm',      label: 'R Arm',         color: [0, 250, 154] },
];

export const NUM_CLASSES = SEG_CLASSES.length;
export const PAINTABLE_CLASSES = SEG_CLASSES.filter((c) => c.id !== 0);

export function getClassColor(id: number): [number, number, number] {
  return SEG_CLASSES[id]?.color ?? [0, 0, 0];
}
