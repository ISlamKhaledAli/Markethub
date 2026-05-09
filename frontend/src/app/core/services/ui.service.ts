import { Injectable, inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class UiService {
  private snackBar = inject(MatSnackBar);

  showComingSoon(feature: string): void {
    this.snackBar.open(`${feature} is coming soon!`, 'OK', {
      duration: 3000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  showInfo(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'end',
      verticalPosition: 'bottom',
    });
  }
}
