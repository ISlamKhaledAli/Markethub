import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-star-rating',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './star-rating.html',
  styleUrl: './star-rating.scss'
})
export class StarRatingComponent {
  @Input() rating: number = 0;     // e.g. 4.5
  @Input() count: number = 0;      // e.g. 128 reviews

  get stars(): ('full' | 'half' | 'empty')[] {
    return Array.from({ length: 5 }, (_, i) => {
      if (this.rating >= i + 1) return 'full';
      if (this.rating >= i + 0.5) return 'half';
      return 'empty';
    });
  }
}
