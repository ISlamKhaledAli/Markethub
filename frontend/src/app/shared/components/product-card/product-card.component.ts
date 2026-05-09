import { Component, Input, HostBinding } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Product } from '../../../core/models/product.model';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './product-card.component.html',
  styleUrl: './product-card.component.scss',
})
export class ProductCardComponent {
  @Input({ required: true }) product!: Product;

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
}
