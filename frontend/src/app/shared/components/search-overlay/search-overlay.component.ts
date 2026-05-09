import { Component, Input, Output, EventEmitter, ViewChildren, QueryList, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Product } from '../../../core/models/product.model';
import { HighlightPipe } from '../../pipes/highlight.pipe';
import { PrimaryImagePipe } from '../../pipes/primary-image-pipe';
import { ConfigService } from '../../../core/services/config';

@Component({
  selector: 'app-search-overlay',
  standalone: true,
  imports: [CommonModule, HighlightPipe, PrimaryImagePipe],
  templateUrl: './search-overlay.component.html',
  styleUrl: './search-overlay.component.scss'
})
export class SearchOverlayComponent {
  private configService = inject(ConfigService);
  
  @Input() results: Product[] = [];
  @Input() isLoading = false;
  @Input() query = '';
  @Output() resultSelected = new EventEmitter<Product>();
  @Output() viewAllClicked = new EventEmitter<void>();

  @ViewChildren('resultItem') resultItems!: QueryList<ElementRef>;
  focusedIndex = -1;

  handleKeyDown(event: KeyboardEvent): void {
    if (this.results.length === 0) return;

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      this.focusedIndex = (this.focusedIndex + 1) % (this.results.length + 1); // +1 for "View All"
      this.focusElement();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      this.focusedIndex = (this.focusedIndex - 1 + (this.results.length + 1)) % (this.results.length + 1);
      this.focusElement();
    } else if (event.key === 'Enter') {
      if (this.focusedIndex >= 0 && this.focusedIndex < this.results.length) {
        this.onSelect(this.results[this.focusedIndex]);
      } else if (this.focusedIndex === this.results.length) {
        this.onViewAll();
      }
    }
  }

  private focusElement(): void {
    const items = this.resultItems.toArray();
    if (this.focusedIndex >= 0 && this.focusedIndex < items.length) {
      items[this.focusedIndex].nativeElement.focus();
    }
  }

  onSelect(product: Product): void {
    this.resultSelected.emit(product);
  }

  onViewAll(): void {
    this.viewAllClicked.emit();
  }

  onImageError(event: Event): void {
    (event.target as HTMLImageElement).src = this.configService.catalogConfig.placeholders.productImage;
  }
}
