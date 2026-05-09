import { Component, Input, HostBinding, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Product } from '../../../core/models/product.model';
import { UiService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './product-card.component.html',
  styleUrl: './product-card.component.scss',
})
export class ProductCardComponent {
  @Input({ required: true }) product!: Product;
  private uiService = inject(UiService);

  @HostBinding('class') get hostClasses() {
    return 'block cursor-pointer group';
  }

  get primaryImage(): string {
    const primary = this.product.images.find((i) => i.is_primary);
    return primary?.image || this.product.images[0]?.image || 'assets/images/placeholder.png';
  }

  get hasDiscount(): boolean {
    return !!(
      this.product.discount_price &&
      parseFloat(this.product.discount_price) < parseFloat(this.product.price)
    );
  }

  addToCart(event: Event): void {
    event.stopPropagation();
    this.uiService.showComingSoon('Cart');
  }

  toggleWishlist(event: Event): void {
    event.stopPropagation();
    this.uiService.showComingSoon('Wishlist');
  }
}
