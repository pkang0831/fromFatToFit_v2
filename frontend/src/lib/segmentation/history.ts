/**
 * Undo/redo manager for label map snapshots.
 * Stores full Uint8Array copies.  Cap at 30 to bound memory.
 */

const MAX_HISTORY = 30;

export class UndoManager {
  private undoStack: Uint8Array[] = [];
  private redoStack: Uint8Array[] = [];

  push(snapshot: Uint8Array): void {
    this.undoStack.push(new Uint8Array(snapshot));
    if (this.undoStack.length > MAX_HISTORY) this.undoStack.shift();
    this.redoStack = [];
  }

  undo(current: Uint8Array): Uint8Array | null {
    if (this.undoStack.length === 0) return null;
    this.redoStack.push(new Uint8Array(current));
    return this.undoStack.pop()!;
  }

  redo(current: Uint8Array): Uint8Array | null {
    if (this.redoStack.length === 0) return null;
    this.undoStack.push(new Uint8Array(current));
    return this.redoStack.pop()!;
  }

  get canUndo(): boolean { return this.undoStack.length > 0; }
  get canRedo(): boolean { return this.redoStack.length > 0; }

  clear(): void {
    this.undoStack = [];
    this.redoStack = [];
  }
}
