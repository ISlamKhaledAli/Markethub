import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { ProductCardComponent } from '../../../shared/components/product-card/product-card.component';
import { ProductService } from '../../../core/services/product.service';
import { CategoryService } from '../../../core/services/category.service';
import { Product } from '../../../core/models/product.model';
import { Category } from '../../../core/models/category.model';
import { UiService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductCardComponent],
  templateUrl: './product-detail.component.html',
  styleUrl: './product-detail.component.scss',
})
export class ProductDetailComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private productService = inject(ProductService);
  private categoryService = inject(CategoryService);
  private uiService = inject(UiService);

  product: Product | null = null;
  relatedProducts: Product[] = [];
  quantity = 1;
  selectedImageUrl = '';
  categoryName = '';
  categorySlug = '';
  
  isLoading = true;
  hasError = false;
  notFound = false;

  private routeSub!: Subscription;

  ngOnInit(): void {
    this.routeSub = this.route.paramMap.subscribe(params => {
      const slug = params.get('slug');
      if (slug) {
        this.loadProduct(slug);
      } else {
        this.notFound = true;
        this.isLoading = false;
      }
    });
  }

  ngOnDestroy(): void {
    if (this.routeSub) {
      this.routeSub.unsubscribe();
    }
  }

  loadProduct(slug: string): void {
    this.isLoading = true;
    this.hasError = false;
    this.notFound = false;
    this.product = null;
    this.relatedProducts = [];
    this.quantity = 1;

    this.productService.getProductBySlug(slug).subscribe({
      next: (product: Product) => {
        this.product = product;
        this.selectedImageUrl = product.images.find(i => i.is_primary)?.image ?? product.images[0]?.image ?? '';
        this.resolveCategory(product.category);
        this.isLoading = false;
      },
      error: (err: any) => {
        if (err.status === 404) {
          this.notFound = true;
        } else {
          this.hasError = true;
        }
        this.isLoading = false;
      }
    });
  }

  resolveCategory(categoryId: number): void {
    this.categoryService.getCategories().subscribe({
      next: (categories: Category[]) => {
        const cat = categories.find((c: Category) => c.id === categoryId);
        if (cat) {
          this.categoryName = cat.name;
          this.categorySlug = cat.slug;
          this.loadRelatedProducts(cat.slug);
        }
      }
    });
  }

  loadRelatedProducts(categorySlug: string): void {
    this.productService.getProducts({ category: categorySlug }).subscribe({
      next: (res: any) => {
        const products = Array.isArray(res) ? res : (res.results || []);
        this.relatedProducts = products
          .filter((p: Product) => p.id !== this.product?.id)
          .slice(0, 4);
      }
    });
  }

  increaseQty(): void {
    if (this.product && this.quantity < this.product.stock) {
      this.quantity++;
    }
  }

  decreaseQty(): void {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  selectImage(url: string): void {
    this.selectedImageUrl = url;
  }

  addToCart(): void {
    this.uiService.showComingSoon('Cart');
  }
}
