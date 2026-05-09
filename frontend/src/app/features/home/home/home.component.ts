import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Observable, catchError, map, of, finalize } from 'rxjs';
import { ProductService } from '../../../core/services/product.service';
import { CategoryService } from '../../../core/services/category.service';
import { Product } from '../../../core/models/product.model';
import { Category } from '../../../core/models/category.model';
import { ProductCardComponent } from '../../../shared/components/product-card/product-card.component';

interface Banner {
  title: string;
  subtitle: string;
  description: string;
  image: string;
  badge: string;
  ctaText: string;
  link: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductCardComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  categories$: Observable<Category[]> = of([]);
  featuredProducts$: Observable<Product[]> = of([]);
  isLoading = true;
  error: string | null = null;

  banners: Banner[] = [
    {
      title: 'Defining the New Standard.',
      subtitle: 'Summer Collection 2024',
      description: 'Discover our curated arrivals designed for modern living. Precision-crafted essentials that bridge the gap between utility and luxury.',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDziO1l-bCgTE_FnyHagml6xf9Nj1xt_KP2AL33Rs57k_FgHm05gyUIdk6Vck6IdDOAEuS0qvMzRF_FQBWbvqFFiPvJn0ln74bvAcXaoeKZnJxKh6v5PZtedJ6TK8Lho462creZUryz1VqCI4NT2s2OQG4BTmlVsKEzybivG2hWNh9xk-TvxhBiByFY_ictSJ9NGipNlTwm5UhgN6TrMg6LpaiR_WtS1E20fxN_6RWp3hFmKYEtnMJcigfdH0fQ7__XrX5ONdgasQ4',
      badge: 'New Arrivals',
      ctaText: 'Shop New Arrivals',
      link: '/catalog'
    }
  ];

  constructor(
    private productService: ProductService,
    private categoryService: CategoryService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    this.categories$ = this.categoryService.getCategories().pipe(
      catchError(err => {
        console.error('Error fetching categories', err);
        this.error = 'Failed to load categories';
        return of([]);
      })
    );

    this.featuredProducts$ = this.productService.getProducts({ ordering: '-created_at' }).pipe(
      map(products => products.slice(0, 8)),
      catchError(err => {
        console.error('Error fetching products', err);
        this.error = 'Failed to load featured products';
        return of([]);
      }),
      finalize(() => this.isLoading = false)
    );
  }

  addToCart(event: Event, product: Product): void {
    event.stopPropagation(); // prevent card navigation
    // TODO: integrate CartService
    console.log('Add to cart:', product.slug);
  }

  isNew(dateString: string): boolean {
    const createdDate = new Date(dateString);
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return createdDate > thirtyDaysAgo;
  }
}
