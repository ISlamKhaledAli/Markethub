import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { ProductCardComponent } from '../../../shared/components/product-card/product-card.component';
import { ProductService } from '../../../core/services/product.service';
import { CategoryService } from '../../../core/services/category.service';
import { Product } from '../../../core/models/product.model';
import { Category } from '../../../core/models/category.model';
import { UiService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink, ProductCardComponent],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss',
})
export class CatalogComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private productService = inject(ProductService);
  private categoryService = inject(CategoryService);
  private uiService = inject(UiService);

  // Filter state
  searchTerm = '';
  selectedCategory: string | null = null;
  minPrice: number | null = null;
  maxPrice: number | null = null;
  availability: boolean | null = null;  // true = in-stock only
  ordering = '-created_at';  // default sort

  // UI state
  products: Product[] = [];
  categories: Category[] = [];
  totalCount = 0;
  isLoading = false;
  hasError = false;
  viewMode: 'grid' | 'list' = 'grid';

  // Pagination
  page = 1;
  pageSize = 12;
  hasMoreProducts = true;

  // Subscriptions
  private searchSubject = new Subject<string>();
  private routeSub!: Subscription;
  private searchSub!: Subscription;

  ngOnInit(): void {
    this.fetchCategories();

    this.searchSub = this.searchSubject.pipe(
      debounceTime(400),
      distinctUntilChanged()
    ).subscribe(term => {
      this.updateUrlParams({ search: term || null, page: null });
    });

    this.routeSub = this.route.queryParams.subscribe(params => {
      this.searchTerm = params['search'] || '';
      this.selectedCategory = params['category'] || null;
      this.minPrice = params['min_price'] ? +params['min_price'] : null;
      this.maxPrice = params['max_price'] ? +params['max_price'] : null;
      this.availability = params['availability'] === 'true' ? true : null;
      this.ordering = params['ordering'] || '-created_at';
      this.page = params['page'] ? +params['page'] : 1;

      this.fetchProducts();
    });
  }

  ngOnDestroy(): void {
    if (this.routeSub) this.routeSub.unsubscribe();
    if (this.searchSub) this.searchSub.unsubscribe();
  }

  fetchCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (cats: Category[]) => this.categories = cats,
      error: (err: any) => console.error('Failed to load categories', err)
    });
  }

  fetchProducts(): void {
    this.isLoading = true;
    this.hasError = false;

    const params: any = {
      ordering: this.ordering,
      page: this.page,
      page_size: this.pageSize
    };

    if (this.searchTerm) params.search = this.searchTerm;
    if (this.selectedCategory) params.category = this.selectedCategory;
    if (this.minPrice !== null) params.min_price = this.minPrice;
    if (this.maxPrice !== null) params.max_price = this.maxPrice;
    if (this.availability !== null) params.availability = this.availability;

    this.productService.getProducts(params).subscribe({
      next: (res: any) => {
        const newProducts = Array.isArray(res) ? res : (res.results || []);
        
        if (this.page === 1) {
          this.products = newProducts;
        } else {
          this.products = [...this.products, ...newProducts];
        }

        this.hasMoreProducts = newProducts.length === this.pageSize;
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Failed to load products', err);
        this.hasError = true;
        this.isLoading = false;
      }
    });
  }

  onSearchChange(term: string): void {
    this.searchSubject.next(term);
  }

  onCategorySelect(categorySlug: string | null): void {
    this.updateUrlParams({ category: categorySlug, page: null });
  }

  onPriceChange(): void {
    this.updateUrlParams({ 
      min_price: this.minPrice, 
      max_price: this.maxPrice,
      page: null
    });
  }

  onAvailabilityChange(): void {
    this.updateUrlParams({ 
      availability: this.availability ? 'true' : null,
      page: null
    });
  }

  onOrderingChange(): void {
    this.updateUrlParams({ ordering: this.ordering, page: null });
  }

  clearAllFilters(): void {
    this.router.navigate(['/catalog']);
  }

  loadMore(): void {
    this.updateUrlParams({ page: this.page + 1 });
  }

  showComingSoon(feature: string): void {
    this.uiService.showComingSoon(feature);
  }

  private updateUrlParams(params: any): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: params,
      queryParamsHandling: 'merge'
    });
  }
}
